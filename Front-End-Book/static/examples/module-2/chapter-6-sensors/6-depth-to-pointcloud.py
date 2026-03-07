#!/usr/bin/env python3
"""
Chapter 6 Example: Depth Image to Point Cloud Conversion

This example demonstrates:
- Converting depth images to 3D point clouds using camera intrinsics
- Handling different depth image formats and noise
- Optimizing conversion performance with vectorized operations
- Publishing point clouds for 3D visualization

Prerequisites:
- Depth camera sensor in Gazebo
- ROS 2 Humble with cv_bridge and image_geometry
- Camera calibration info available

Usage:
    python3 6-depth-to-pointcloud.py
    # Subscribe to /camera/depth/image_raw
    # Publish to /camera/converted_pointcloud
    # Watch performance metrics in console

Key Implementation Details:
- Back-projection formula: X = (u - cx) * Z / fx
- Vectorized NumPy for fast processing
- Handles invalid depths (0, NaN, infinity)
- Optional bilateral filtering for noise reduction

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

from sensor_msgs.msg import Image, PointCloud2, CameraInfo, PointField
from cv_bridge import CvBridge, CvBridgeError
from image_geometry import PinholeCameraModel
import sensor_msgs.point_cloud2 as pc2
from std_msgs.msg import Header


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DepthToPointCloud(Node):
    """
    Convert depth images to point clouds efficiently.

    This node:
    1. Subscribes to depth images and camera calibration
    2. Filters invalid depths and applies smoothing
    3. Converts to 3D points using back-projection
    4. Publishes as PointCloud2 for visualization

    Performance: ~30ms per VGA (640×480) image
    """

    def __init__(self):
        """Initialize depth-to-pointcloud converter."""
        super().__init__('depth_to_pointcloud')

        self.bridge = CvBridge()
        self.camera_model = PinholeCameraModel()
        self.camera_info_received = False

        # Processing parameters
        self.bilateral_filter = True  # Smooth depth while preserving edges
        self.min_depth = 0.1  # Minimum valid depth (meters)
        self.max_depth = 10.0  # Maximum valid depth (meters)

        # Statistics
        self.frame_count = 0
        self.processing_time_ms = 0.0
        self.points_per_frame = 0
        self.fps = 0.0
        self.last_time = time.time()

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscribers
        self.create_subscription(
            CameraInfo,
            '/camera/depth/camera_info',
            self.camera_info_callback,
            qos_profile=qos_profile
        )

        self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            qos_profile=qos_profile
        )

        # Publisher
        self.pointcloud_pub = self.create_publisher(
            PointCloud2,
            '/camera/converted_pointcloud',
            qos_profile=qos_profile
        )

        logger.info("✅ Depth-to-PointCloud Converter initialized")

    def camera_info_callback(self, msg: CameraInfo) -> None:
        """
        Store camera calibration (intrinsics).

        Args:
            msg: CameraInfo message with K (intrinsics), D (distortion)
        """
        if not self.camera_info_received:
            self.camera_model.fromCameraInfo(msg)
            self.camera_info_received = True
            logger.info(
                f"📷 Camera calibration received: "
                f"{msg.width}×{msg.height}, "
                f"fx={msg.K[0]:.1f}, fy={msg.K[4]:.1f}, "
                f"cx={msg.K[2]:.1f}, cy={msg.K[5]:.1f}"
            )

    def depth_callback(self, msg: Image) -> None:
        """
        Convert depth image to point cloud.

        Args:
            msg: Depth image message
        """
        if not self.camera_info_received:
            logger.warning("⚠️  Waiting for camera calibration...")
            return

        start_time = time.time()

        try:
            # Convert ROS Image to OpenCV format
            depth_image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='passthrough'
            )

            # Convert to float32 if needed (handle 16-bit depth images)
            if depth_image.dtype != np.float32:
                depth_image = depth_image.astype(np.float32) / 1000.0

            # Apply preprocessing
            depth_image = self._preprocess_depth(depth_image)

            # Back-project to 3D points
            points = self._depth_to_points(depth_image)

            if points is not None and len(points) > 0:
                # Create PointCloud2 message
                pc_msg = pc2.create_cloud_xyz32(
                    frame_id=msg.header.frame_id,
                    timestamp=msg.header.stamp,
                    xyz=points
                )

                self.pointcloud_pub.publish(pc_msg)

                self.points_per_frame = len(points)
            else:
                logger.warning("⚠️  No valid points generated")

            # Update metrics
            self.processing_time_ms = (time.time() - start_time) * 1000.0
            self.frame_count += 1

            # Log FPS periodically
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = 1.0 / (self.processing_time_ms / 1000.0)
                logger.info(
                    f"📊 Conversion Performance: "
                    f"{self.fps:.1f} FPS, "
                    f"{self.processing_time_ms:.1f}ms per frame, "
                    f"{self.points_per_frame} points"
                )
                self.last_time = current_time

        except CvBridgeError as e:
            logger.error(f"❌ Image conversion error: {e}")
        except Exception as e:
            logger.error(f"❌ Processing error: {e}")

    def _preprocess_depth(self, depth_image: np.ndarray) -> np.ndarray:
        """
        Preprocess depth image: filter, smooth, validate.

        Args:
            depth_image: Raw depth image (H×W), values in meters

        Returns:
            Cleaned depth image
        """
        # Create valid depth mask
        valid_mask = (
            (depth_image > self.min_depth) &
            (depth_image < self.max_depth) &
            np.isfinite(depth_image)
        )

        # Apply bilateral filter to reduce noise while preserving edges
        if self.bilateral_filter:
            try:
                # Bilateral filter: strong edge preservation
                depth_filtered = cv2.bilateralFilter(
                    depth_image,
                    d=9,  # Diameter of pixel neighborhood
                    sigmaColor=0.1,  # Sigma in value space
                    sigmaSpace=10  # Sigma in coordinate space
                )
                depth_image = depth_filtered
            except cv2.error as e:
                logger.debug(f"Bilateral filter skipped: {e}")

        # Zero out invalid depths
        depth_image[~valid_mask] = 0.0

        logger.debug(
            f"Depth preprocessing: "
            f"{np.sum(valid_mask)} valid pixels, "
            f"range: {np.min(depth_image[valid_mask]):.2f}-"
            f"{np.max(depth_image[valid_mask]):.2f}m"
        )

        return depth_image

    def _depth_to_points(
        self,
        depth_image: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Back-project depth image to 3D points using camera intrinsics.

        Uses vectorized NumPy operations for efficiency.

        Formula:
            X = (u - cx) * Z / fx
            Y = (v - cy) * Z / fy
            Z = depth[v, u]

        Args:
            depth_image: Depth map of shape (height, width), values in meters

        Returns:
            Point array of shape (N, 3) with [x, y, z] coordinates
        """
        height, width = depth_image.shape

        # Get camera intrinsics
        fx = self.camera_model.fx()
        fy = self.camera_model.fy()
        cx = self.camera_model.cx()
        cy = self.camera_model.cy()

        # Create pixel coordinate grids
        u, v = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
            indexing='xy'
        )

        # Get depth values
        z = depth_image

        # Vectorized back-projection
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy

        # Stack into Nx3 array
        points = np.stack([x.ravel(), y.ravel(), z.ravel()], axis=1)

        # Remove points with zero depth (invalid)
        valid_idx = z.ravel() > 0
        points = points[valid_idx]

        logger.debug(
            f"Back-projection: {width}×{height} depth → "
            f"{len(points)} 3D points"
        )

        return points.astype(np.float32)


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting Depth-to-PointCloud Converter...")
        logger.info("Topics:")
        logger.info("  Subscribe: /camera/depth/image_raw (Image)")
        logger.info("  Subscribe: /camera/depth/camera_info (CameraInfo)")
        logger.info("  Publish: /camera/converted_pointcloud (PointCloud2)")
        logger.info("")
        logger.info("Performance Tips:")
        logger.info("  • Bilateral filtering improves quality but uses CPU")
        logger.info("  • Vectorized NumPy operations are fast")
        logger.info("  • Typical speed: 30-50ms for VGA (640×480) images")
        logger.info("")
        logger.info("Visualization:")
        logger.info("  rviz2 -d config.rviz  # Add /camera/converted_pointcloud")

        converter = DepthToPointCloud()
        rclpy.spin(converter)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
