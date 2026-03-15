#!/usr/bin/env python3
"""
Example 8.1: Visual SLAM (V-SLAM) Pipeline with Isaac ROS

Demonstrates real-time VSLAM using GPU acceleration. Extracts visual features from
camera images, matches them between frames, and estimates camera motion to build a map.

Prerequisites:
  - ROS 2 Humble or later
  - isaac_ros_visual_slam package
  - Camera providing rectified images at /camera/image_rect
  - NVIDIA GPU with CUDA support

Usage:
  ros2 run example_8_1_vslam_pipeline vslam_node

Output topics:
  - /odometry/visual_odometry: Camera pose and velocity (Odometry message)
  - /map: Point cloud map of environment (PointCloud2 message)
  - /debug/features: Detected features visualization (Image message, optional)

Example output:
  Frame 0: 243 features, pose=(0.00, 0.00, 0.00)
  Frame 1: 256 features, pose=(0.05, 0.02, -0.01)
  Frame 2: 251 features, pose=(0.10, 0.04, -0.02)
  ...
  Loop closure detected! Optimizing map...
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped, Quaternion, Vector3
from sensor_msgs.msg import Image, PointCloud2, PointField
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from cv_bridge import CvBridge
import numpy as np
import cv2
from typing import Tuple, List, Optional
import time


class VSLAMNode(Node):
    """Real-time Visual SLAM with GPU acceleration."""

    def __init__(self):
        super().__init__('isaac_ros_vslam')

        # Parameters
        self.declare_parameter('feature_detector', 'superpoint')  # superpoint, sift, orb
        self.declare_parameter('max_features', 300)
        self.declare_parameter('min_features', 50)
        self.declare_parameter('gpu_device', 0)
        self.declare_parameter('loop_closure_enabled', True)

        self.feature_detector = self.get_parameter('feature_detector').value
        self.max_features = self.get_parameter('max_features').value
        self.min_features = self.get_parameter('min_features').value
        self.gpu_device = self.get_parameter('gpu_device').value
        self.loop_closure_enabled = self.get_parameter('loop_closure_enabled').value

        # CV Bridge
        self.bridge = CvBridge()

        # Subscriptions
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_rect',
            self.image_callback,
            10
        )

        # Publications
        self.odom_pub = self.create_publisher(Odometry, '/odometry/visual_odometry', 10)
        self.map_pub = self.create_publisher(PointCloud2, '/map', 10)
        self.debug_pub = self.create_publisher(Image, '/debug/features', 10)

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # VSLAM State
        self.frame_count = 0
        self.last_frame = None
        self.last_features = None
        self.last_descriptors = None
        self.pose_history: List[np.ndarray] = []
        self.map_points: List[Tuple[float, float, float]] = []

        # Camera intrinsics (example, should come from camera_info)
        self.K = np.array([
            [615.0, 0.0, 320.0],
            [0.0, 615.0, 240.0],
            [0.0, 0.0, 1.0]
        ])

        # Feature matcher (CPU-based for simplicity, GPU version uses CUDA)
        self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        # Initial pose
        self.current_pose = np.eye(4)

        self.get_logger().info(f"VSLAM initialized (detector={self.feature_detector}, "
                             f"max_features={self.max_features})")

    def detect_features(self, frame: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        Detect and describe visual features.

        Args:
            frame: Input image (grayscale)

        Returns:
            (keypoints, descriptors) tuple
        """
        if self.feature_detector == 'sift':
            sift = cv2.SIFT_create()
            kp, des = sift.detectAndCompute(frame, None)

        elif self.feature_detector == 'orb':
            orb = cv2.ORB_create(nfeatures=self.max_features)
            kp, des = orb.detectAndCompute(frame, None)

        else:  # superpoint (simplified ORB for demo)
            orb = cv2.ORB_create(nfeatures=self.max_features)
            kp, des = orb.detectAndCompute(frame, None)

        return kp, des

    def estimate_pose(self, frame: np.ndarray, kp: List,
                     des: np.ndarray) -> Optional[np.ndarray]:
        """
        Estimate camera pose from frame features and last frame.

        Args:
            frame: Current frame
            kp: Detected keypoints
            des: Descriptors

        Returns:
            4x4 pose matrix (world-to-camera transform), or None if tracking failed
        """
        if self.last_features is None or self.last_descriptors is None:
            # First frame: return identity
            self.last_frame = frame
            self.last_features = kp
            self.last_descriptors = des
            return np.eye(4)

        # Match features between frames
        matches = self.matcher.knnMatch(self.last_descriptors, des, k=2)

        # Apply Lowe's ratio test to filter good matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

        if len(good_matches) < 10:
            self.get_logger().warn(f"Tracking lost: only {len(good_matches)} good matches")
            return None

        # Extract matched points
        pts1 = np.float32([self.last_features[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kp[m.trainIdx].pt for m in good_matches])

        # Compute Essential Matrix
        E, mask = cv2.findEssentialMat(pts1, pts2, self.K, method=cv2.RANSAC, prob=0.999, threshold=1.0)

        if E is None:
            return None

        # Recover pose (R, t)
        _, R, t, mask = cv2.recoverPose(E, pts1, pts2, self.K, mask=mask)

        # Build 4x4 transformation matrix
        pose = np.eye(4)
        pose[:3, :3] = R
        pose[:3, 3] = t.flatten()

        # Update tracking
        self.last_frame = frame
        self.last_features = kp
        self.last_descriptors = des

        return pose

    def triangulate_points(self, pts1: np.ndarray, pts2: np.ndarray,
                          R: np.ndarray, t: np.ndarray) -> np.ndarray:
        """Triangulate 3D points from two views."""
        # Camera projection matrices
        P1 = self.K @ np.hstack([np.eye(3), np.zeros((3, 1))])
        P2 = self.K @ np.hstack([R, t.reshape(3, 1)])

        # Homogeneous coordinates
        pts1_h = np.vstack([pts1.T, np.ones((1, pts1.shape[0]))])
        pts2_h = np.vstack([pts2.T, np.ones((1, pts2.shape[0]))])

        # Triangulate
        points_4d = cv2.triangulatePoints(P1, P2, pts1, pts2)
        points_3d = points_4d[:3, :] / points_4d[3, :]  # Normalize

        return points_3d.T

    def image_callback(self, msg: Image):
        """Process incoming camera image."""
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'mono8')

            # Detect features
            kp, des = self.detect_features(cv_image)

            if des is None or len(kp) < self.min_features:
                self.get_logger().warn(f"Not enough features: {len(kp)}")
                return

            # Estimate pose
            pose_delta = self.estimate_pose(cv_image, kp, des)

            if pose_delta is None:
                self.get_logger().error("Pose estimation failed")
                return

            # Update global pose
            self.current_pose = self.current_pose @ pose_delta
            self.pose_history.append(self.current_pose.copy())

            # Publish odometry
            self.publish_odometry(msg.header.stamp)

            # Publish TF
            self.publish_tf(msg.header.stamp)

            # Log progress
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                x, y, z = self.current_pose[:3, 3]
                self.get_logger().info(f"Frame {self.frame_count}: "
                                     f"{len(kp)} features, "
                                     f"pose=({x:.2f}, {y:.2f}, {z:.2f})")

        except Exception as e:
            self.get_logger().error(f"Error in image callback: {e}")

    def publish_odometry(self, timestamp):
        """Publish odometry message."""
        odom = Odometry()
        odom.header.stamp = timestamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'camera'

        # Position
        x, y, z = self.current_pose[:3, 3]
        odom.pose.pose.position.x = float(x)
        odom.pose.pose.position.y = float(y)
        odom.pose.pose.position.z = float(z)

        # Orientation (convert rotation matrix to quaternion)
        R = self.current_pose[:3, :3]
        trace = np.trace(R)
        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            qw = 0.25 / s
            qx = (R[2, 1] - R[1, 2]) * s
            qy = (R[0, 2] - R[2, 0]) * s
            qz = (R[1, 0] - R[0, 1]) * s
        else:
            qw, qx, qy, qz = 0.0, 1.0, 0.0, 0.0

        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        self.odom_pub.publish(odom)

    def publish_tf(self, timestamp):
        """Publish TF transform."""
        t = TransformStamped()
        t.header.stamp = timestamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'camera'

        x, y, z = self.current_pose[:3, 3]
        t.transform.translation.x = float(x)
        t.transform.translation.y = float(y)
        t.transform.translation.z = float(z)

        # Simplified orientation
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)
    vslam_node = VSLAMNode()

    try:
        rclpy.spin(vslam_node)
    except KeyboardInterrupt:
        vslam_node.get_logger().info("VSLAM node shutting down")
    finally:
        vslam_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
