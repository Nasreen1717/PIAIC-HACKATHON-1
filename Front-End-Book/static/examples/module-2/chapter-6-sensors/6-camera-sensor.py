#!/usr/bin/env python3
"""
Chapter 6 Example: RGB-D Camera Sensor Processing

This example demonstrates:
- Subscribing to RGB and depth camera topics from Gazebo
- Processing RGB images with OpenCV
- Converting depth images to point clouds
- Publishing processed data for visualization

Prerequisites:
- Gazebo running with RGB-D camera
- ROS 2 Humble with cv_bridge, image_geometry packages
- Camera simulated with proper noise and parameters

Usage:
    python3 6-camera-sensor.py
    # Watch /camera/rgb_image_processed (OpenCV edge detection output)
    # Watch /camera/depth_pointcloud (converted point cloud)

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import sys
import time
import logging
from typing import Optional, Tuple

import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image, PointCloud2, CameraInfo
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Header

from cv_bridge import CvBridge, CvBridgeError
from image_geometry import PinholeCameraModel
import sensor_msgs.point_cloud2 as pc2


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RGBDCameraProcessor(Node):
    """
    Process RGB-D camera data from Gazebo.

    Subscribes to:
    - /camera/color/image_raw: RGB image
    - /camera/depth/image_raw: Depth image
    - /camera/color/camera_info: Camera intrinsics

    Publishes:
    - /camera/rgb_processed: Edge-detected RGB image
    - /camera/depth_pointcloud: Converted point cloud
    """

    def __init__(self):
        """Initialize RGB-D camera processor node."""
        super().__init__('rgbd_camera_processor')

        self.bridge = CvBridge()
        self.camera_model = PinholeCameraModel()
        self.camera_info_received = False

        # Performance metrics
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0.0

        # QoS profile for better synchronization
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscribers
        self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.camera_info_callback,
            qos_profile=qos_profile
        )

        self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.rgb_callback,
            qos_profile=qos_profile
        )

        self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            qos_profile=qos_profile
        )

        # Publishers
        self.rgb_pub = self.create_publisher(
            Image, '/camera/rgb_processed', qos_profile=qos_profile
        )
        self.depth_pub = self.create_publisher(
            PointCloud2, '/camera/depth_pointcloud', qos_profile=qos_profile
        )

        logger.info("✅ RGB-D Camera Processor initialized")

    def camera_info_callback(self, msg: CameraInfo) -> None:
        """
        Store camera intrinsics for depth processing.

        Args:
            msg: CameraInfo message with K, D (distortion), etc.
        """
        if not self.camera_info_received:
            self.camera_model.fromCameraInfo(msg)
            self.camera_info_received = True
            logger.info(f"📷 Camera calibration received: {msg.width}x{msg.height}")

    def rgb_callback(self, msg: Image) -> None:
        """
        Process RGB image: edge detection, visualization.

        Args:
            msg: ROS 2 Image message
        """
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Colorize edges: white edges on black background
            edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # Convert back to ROS Image
            processed_msg = self.bridge.cv2_to_imgmsg(
                edges_color, encoding='bgr8'
            )
            processed_msg.header = msg.header

            # Publish processed image
            self.rgb_pub.publish(processed_msg)

            # Update FPS counter
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.last_time)
                logger.info(f"📊 RGB Processing: {self.fps:.1f} FPS")
                self.frame_count = 0
                self.last_time = current_time

        except CvBridgeError as e:
            logger.error(f"❌ RGB conversion error: {e}")

    def depth_callback(self, msg: Image) -> None:
        """
        Convert depth image to point cloud.

        Args:
            msg: Depth image (typically FLOAT32, unit: meters)
        """
        if not self.camera_info_received:
            logger.warning("⚠️  Waiting for camera calibration...")
            return

        try:
            # Convert ROS Image to numpy array
            depth_image = self.bridge.imgmsg_to_cv2(
                msg, desired_encoding='passthrough'
            )

            # Check for valid depth range
            if depth_image.dtype != np.float32:
                depth_image = depth_image.astype(np.float32) / 1000.0

            # Generate point cloud from depth image
            points = self._depth_to_pointcloud(depth_image, msg.header)

            if points is not None and len(points) > 0:
                # Convert to PointCloud2 message
                pc2_msg = pc2.create_cloud(
                    frame_id=msg.header.frame_id,
                    timestamp=msg.header.stamp,
                    xyz=points
                )
                self.depth_pub.publish(pc2_msg)
                logger.debug(f"🔷 Published {len(points)} points")

        except CvBridgeError as e:
            logger.error(f"❌ Depth conversion error: {e}")
        except Exception as e:
            logger.error(f"❌ Point cloud generation error: {e}")

    def _depth_to_pointcloud(
        self,
        depth_image: np.ndarray,
        header: Header
    ) -> Optional[np.ndarray]:
        """
        Convert depth image to 3D point cloud using camera intrinsics.

        Args:
            depth_image: Depth map (H×W), values in meters
            header: ROS message header with timestamp

        Returns:
            numpy array of shape (N, 3) with [x, y, z] coordinates
        """
        height, width = depth_image.shape

        # Camera intrinsics (from self.camera_model)
        fx = self.camera_model.fx()
        fy = self.camera_model.fy()
        cx = self.camera_model.cx()
        cy = self.camera_model.cy()

        # Create mesh grid of pixel coordinates
        u, v = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
            indexing='xy'
        )

        # Get depth values (flatten for easier processing)
        depth_flat = depth_image.flatten()
        u_flat = u.flatten()
        v_flat = v.flatten()

        # Remove invalid depths (0 = no data, > 10m = noise)
        valid_mask = (depth_flat > 0.1) & (depth_flat < 10.0)

        # Back-project pixels to 3D
        x = (u_flat[valid_mask] - cx) * depth_flat[valid_mask] / fx
        y = (v_flat[valid_mask] - cy) * depth_flat[valid_mask] / fy
        z = depth_flat[valid_mask]

        # Combine into point array
        points = np.column_stack([x, y, z]).astype(np.float32)

        logger.info(
            f"🔷 Depth Image {width}×{height}: "
            f"{np.sum(valid_mask)} valid points, "
            f"depth range: {np.min(z):.2f}-{np.max(z):.2f}m"
        )

        return points


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting RGB-D Camera Processor...")
        logger.info("Topics:")
        logger.info("  Subscribe: /camera/color/image_raw")
        logger.info("  Subscribe: /camera/depth/image_raw")
        logger.info("  Subscribe: /camera/color/camera_info")
        logger.info("  Publish: /camera/rgb_processed")
        logger.info("  Publish: /camera/depth_pointcloud")
        logger.info("")
        logger.info("To visualize:")
        logger.info("  ros2 run rqt_image_view rqt_image_view /camera/rgb_processed")
        logger.info("  rviz2 -d /path/to/rviz.config  # Add /camera/depth_pointcloud")

        processor = RGBDCameraProcessor()
        rclpy.spin(processor)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
