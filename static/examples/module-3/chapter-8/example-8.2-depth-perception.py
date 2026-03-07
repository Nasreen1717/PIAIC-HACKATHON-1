#!/usr/bin/env python3
"""
Example 8.2: Depth Perception with Stereo Depth Estimation

Demonstrates GPU-accelerated depth perception using stereo image pairs or monocular
depth estimation. Generates dense depth maps for obstacle detection and 3D perception.

Prerequisites:
  - ROS 2 with isaac_ros_stereo_image_proc or isaac_ros_ess packages
  - Stereo camera providing left/right images OR monocular camera for depth network
  - NVIDIA GPU (preferably Jetson for edge deployment)

Usage:
  ros2 run example_8_2_depth_perception depth_node

Input topics:
  - /camera/left/image_rect: Left stereo image
  - /camera/right/image_rect: Right stereo image
  - OR /camera/image: Monocular image for depth network

Output topics:
  - /camera/depth_image: Dense depth map (Image message, uint16 encoding)
  - /camera/disparity: Disparity map (Image message)
  - /camera/point_cloud: 3D point cloud (PointCloud2)

Example output:
  Depth map: 1280x720, depth range 0.1-10.0m, fps=30
  Point cloud: 921600 points, memory=22.4MB
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo
from std_msgs.msg import Header
from cv_bridge import CvBridge
import numpy as np
import cv2


class DepthPerceptionNode(Node):
    """GPU-accelerated depth perception from stereo or monocular images."""

    def __init__(self):
        super().__init__('depth_perception_node')

        # Parameters
        self.declare_parameter('mode', 'stereo')  # stereo or monocular
        self.declare_parameter('disparity_levels', 256)  # Stereo depth levels
        self.declare_parameter('window_size', 5)  # Stereo matching window
        self.declare_parameter('model_path', '/models/depth_anything.pt')
        self.declare_parameter('depth_scale', 1000)  # Convert to millimeters

        self.mode = self.get_parameter('mode').value
        self.disparity_levels = self.get_parameter('disparity_levels').value
        self.window_size = self.get_parameter('window_size').value
        self.model_path = self.get_parameter('model_path').value
        self.depth_scale = self.get_parameter('depth_scale').value

        # CV Bridge
        self.bridge = CvBridge()

        # Initialize stereo matcher
        if self.mode == 'stereo':
            self.stereo = cv2.StereoBM_create(
                numDisparities=self.disparity_levels,
                blockSize=self.window_size
            )
            self.stereo.setPreFilterType(1)
            self.stereo.setPreFilterSize(9)
            self.stereo.setPreFilterCap(31)
            self.stereo.setTextureThreshold(10)
            self.stereo.setUniquenessRatio(15)
            self.stereo.setSpeckleRange(0)
            self.stereo.setSpeckleWindowSize(0)
            self.stereo.setDisp12MaxDiff(1)

            self.get_logger().info("Stereo depth matcher initialized")

        else:
            # Monocular depth estimation (using neural network)
            import torch
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            try:
                self.depth_model = torch.jit.load(self.model_path).to(self.device)
                self.depth_model.eval()
                self.get_logger().info(f"Depth model loaded on {self.device}")
            except Exception as e:
                self.get_logger().error(f"Failed to load depth model: {e}")

        # Subscriptions
        if self.mode == 'stereo':
            self.left_sub = self.create_subscription(
                Image,
                '/camera/left/image_rect',
                self.stereo_callback,
                10
            )
            self.right_sub = self.create_subscription(
                Image,
                '/camera/right/image_rect',
                self.stereo_right_callback,
                10
            )
            self.right_image = None

        else:
            self.image_sub = self.create_subscription(
                Image,
                '/camera/image',
                self.monocular_callback,
                10
            )

        # Camera info (for 3D reconstruction)
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10
        )
        self.K = np.eye(3)  # Will be updated from camera_info

        # Publications
        self.depth_pub = self.create_publisher(Image, '/camera/depth_image', 10)
        self.disparity_pub = self.create_publisher(Image, '/camera/disparity', 10)
        self.pointcloud_pub = self.create_publisher(PointCloud2, '/camera/point_cloud', 10)

        self.frame_count = 0

    def camera_info_callback(self, msg: CameraInfo):
        """Store camera intrinsics."""
        self.K = np.array(msg.K).reshape(3, 3)

    def stereo_right_callback(self, msg: Image):
        """Store right stereo image."""
        self.right_image = self.bridge.imgmsg_to_cv2(msg, 'mono8')

    def stereo_callback(self, msg: Image):
        """Process stereo pair for depth estimation."""
        if self.right_image is None:
            return

        try:
            left = self.bridge.imgmsg_to_cv2(msg, 'mono8')

            # Compute disparity map
            disparity = self.stereo.compute(left, self.right_image)

            # Convert disparity to depth (Z = f * b / d, where b=baseline)
            baseline = 0.065  # Example: 6.5cm stereo baseline
            focal_length = self.K[0, 0]
            depth = np.zeros_like(disparity, dtype=np.float32)
            mask = disparity > 0
            depth[mask] = (baseline * focal_length) / (disparity[mask] / 16.0)

            # Publish results
            self.publish_depth_image(depth, msg.header)
            self.publish_disparity(disparity, msg.header)
            self.publish_point_cloud(depth, msg.header)

            self.frame_count += 1
            if self.frame_count % 30 == 0:
                valid_depth = depth[mask].astype(np.float32) / 1000.0
                self.get_logger().info(
                    f"Stereo depth: min={valid_depth.min():.2f}m, "
                    f"max={valid_depth.max():.2f}m, "
                    f"mean={valid_depth.mean():.2f}m"
                )

        except Exception as e:
            self.get_logger().error(f"Stereo processing error: {e}")

    def monocular_callback(self, msg: Image):
        """Process monocular image with depth network."""
        try:
            import torch

            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Preprocess
            h, w = frame.shape[:2]
            input_tensor = torch.from_numpy(
                cv2.resize(frame, (640, 480)).transpose(2, 0, 1)
            ).float().unsqueeze(0).to(self.device) / 255.0

            # Inference
            with torch.no_grad():
                depth_pred = self.depth_model(input_tensor)

            # Postprocess
            depth = depth_pred[0, 0].cpu().numpy()
            depth = cv2.resize(depth, (w, h))
            depth = (depth * 1000).astype(np.uint16)

            # Publish
            self.publish_depth_image(depth, msg.header)
            self.publish_point_cloud(depth.astype(np.float32) / 1000.0, msg.header)

            self.frame_count += 1
            if self.frame_count % 30 == 0:
                self.get_logger().info(
                    f"Monocular depth: min={depth.min()/1000:.2f}m, "
                    f"max={depth.max()/1000:.2f}m"
                )

        except Exception as e:
            self.get_logger().error(f"Monocular depth error: {e}")

    def publish_depth_image(self, depth: np.ndarray, header: Header):
        """Publish depth map as 16-bit image."""
        depth_uint16 = np.clip(depth * self.depth_scale, 0, 65535).astype(np.uint16)
        msg = self.bridge.cv2_to_imgmsg(depth_uint16, encoding='mono16')
        msg.header = header
        self.depth_pub.publish(msg)

    def publish_disparity(self, disparity: np.ndarray, header: Header):
        """Publish disparity map."""
        # Normalize to 0-255 for visualization
        disp_norm = cv2.normalize(disparity.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX)
        disp_uint8 = disp_norm.astype(np.uint8)
        msg = self.bridge.cv2_to_imgmsg(disp_uint8, encoding='mono8')
        msg.header = header
        self.disparity_pub.publish(msg)

    def publish_point_cloud(self, depth: np.ndarray, header: Header):
        """Publish 3D point cloud from depth map."""
        h, w = depth.shape
        x = np.arange(w, dtype=np.float32)
        y = np.arange(h, dtype=np.float32)
        X, Y = np.meshgrid(x, y)

        # Back-project to 3D
        Z = depth
        X_3d = (X - self.K[0, 2]) * Z / self.K[0, 0]
        Y_3d = (Y - self.K[1, 2]) * Z / self.K[1, 1]

        # Flatten and filter
        points = np.column_stack([X_3d.flat, Y_3d.flat, Z.flat])
        valid = Z.flat > 0
        points = points[valid]

        # Create PointCloud2 message
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]

        pc2 = PointCloud2(
            header=header,
            height=1,
            width=len(points),
            fields=fields,
            is_bigendian=False,
            point_step=12,
            row_step=12 * len(points),
            data=np.asarray(points, np.float32).tobytes(),
            is_dense=False
        )

        self.pointcloud_pub.publish(pc2)


def main(args=None):
    rclpy.init(args=args)
    node = DepthPerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
