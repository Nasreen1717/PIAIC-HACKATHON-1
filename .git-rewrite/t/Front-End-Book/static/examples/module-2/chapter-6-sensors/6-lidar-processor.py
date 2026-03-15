#!/usr/bin/env python3
"""
Chapter 6 Example: LiDAR Point Cloud Processing

This example demonstrates:
- Subscribing to 3D LiDAR data from Gazebo
- Filtering point clouds (voxel downsampling, outlier removal)
- Computing point cloud statistics
- Publishing filtered data for visualization

Prerequisites:
- Gazebo with 3D LiDAR sensor (gpu_ray plugin)
- ROS 2 Humble with PCL integration
- Point cloud has reasonable density (>10k points per scan)

Usage:
    python3 6-lidar-processor.py
    # Watch /lidar/filtered topic for processed point cloud
    # Statistics printed to console every 1 second

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import sys
import time
import logging
from typing import Optional, Tuple, List

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import PointCloud2, PointField
from geometry_msgs.msg import Point32
import sensor_msgs.point_cloud2 as pc2


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiDARProcessor(Node):
    """
    Process and filter LiDAR point cloud data.

    Subscribes to:
    - /lidar/scan: Raw 3D point cloud from Gazebo

    Publishes:
    - /lidar/filtered: Filtered point cloud (downsampled + outliers removed)
    - /lidar/statistics: Point cloud metrics (optional, logged)
    """

    def __init__(self):
        """Initialize LiDAR processor node."""
        super().__init__('lidar_processor')

        # Processing parameters
        self.voxel_size = 0.01  # 1cm voxel for downsampling
        self.outlier_radius = 0.5  # Remove points isolated beyond 50cm
        self.outlier_k_neighbors = 5  # Need at least 5 neighbors within radius

        # Performance metrics
        self.point_count_raw = 0
        self.point_count_filtered = 0
        self.processing_time_ms = 0.0
        self.frame_count = 0
        self.last_time = time.time()

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscriber
        self.create_subscription(
            PointCloud2,
            '/lidar/scan',
            self.lidar_callback,
            qos_profile=qos_profile
        )

        # Publishers
        self.filtered_pub = self.create_publisher(
            PointCloud2,
            '/lidar/filtered',
            qos_profile=qos_profile
        )

        logger.info("✅ LiDAR Processor initialized")
        logger.info(f"   Voxel size: {self.voxel_size}m")
        logger.info(f"   Outlier radius: {self.outlier_radius}m")

    def lidar_callback(self, msg: PointCloud2) -> None:
        """
        Process incoming LiDAR point cloud.

        Args:
            msg: PointCloud2 message from Gazebo LiDAR sensor
        """
        start_time = time.time()

        try:
            # Convert ROS PointCloud2 to numpy array
            points = self._pointcloud2_to_array(msg)

            if points is None or len(points) == 0:
                logger.warning("⚠️  Empty point cloud received")
                return

            self.point_count_raw = len(points)

            # Apply filters
            points_filtered = self._voxel_downsample(points, self.voxel_size)
            points_filtered = self._statistical_outlier_removal(
                points_filtered,
                self.outlier_k_neighbors,
                self.outlier_radius
            )

            self.point_count_filtered = len(points_filtered)

            # Create output PointCloud2 message
            output_msg = self._array_to_pointcloud2(
                points_filtered,
                frame_id=msg.header.frame_id,
                timestamp=msg.header.stamp
            )

            self.filtered_pub.publish(output_msg)

            # Update metrics
            self.processing_time_ms = (time.time() - start_time) * 1000.0
            self.frame_count += 1

            # Log statistics every 1 second
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self._log_statistics()
                self.last_time = current_time

        except Exception as e:
            logger.error(f"❌ LiDAR processing error: {e}")

    def _pointcloud2_to_array(self, pc_msg: PointCloud2) -> Optional[np.ndarray]:
        """
        Convert ROS PointCloud2 message to numpy array.

        Args:
            pc_msg: PointCloud2 message

        Returns:
            numpy array of shape (N, 3) with [x, y, z] coordinates
        """
        points_list = list(pc2.read_points(pc_msg, skip_nans=True))

        if len(points_list) == 0:
            return None

        # Extract x, y, z coordinates
        points = np.array([(pt[0], pt[1], pt[2]) for pt in points_list],
                         dtype=np.float32)
        return points

    def _voxel_downsample(
        self,
        points: np.ndarray,
        voxel_size: float
    ) -> np.ndarray:
        """
        Downsample point cloud using voxel grid.

        Simple implementation: divide space into voxels and keep one point per voxel.

        Args:
            points: Input points (N, 3)
            voxel_size: Edge length of voxel cubes (meters)

        Returns:
            Downsampled points
        """
        if len(points) == 0:
            return points

        # Convert to voxel indices
        voxel_indices = (points / voxel_size).astype(np.int32)

        # Use tuple of indices as key for unique voxels
        unique_voxels = {}
        for i, (point, idx) in enumerate(zip(points, voxel_indices)):
            idx_tuple = tuple(idx)
            if idx_tuple not in unique_voxels:
                unique_voxels[idx_tuple] = point

        # Extract downsampled points
        downsampled = np.array(list(unique_voxels.values()), dtype=np.float32)

        logger.debug(
            f"🔽 Voxel downsample: {len(points)} → {len(downsampled)} points "
            f"({100*len(downsampled)/len(points):.1f}%)"
        )

        return downsampled

    def _statistical_outlier_removal(
        self,
        points: np.ndarray,
        k: int = 5,
        radius: float = 0.5
    ) -> np.ndarray:
        """
        Remove isolated points (outliers).

        Removes points that have fewer than k neighbors within radius distance.

        Args:
            points: Input points (N, 3)
            k: Minimum number of neighbors required
            radius: Search radius in meters

        Returns:
            Filtered points without isolated outliers
        """
        if len(points) < k:
            return points

        # Compute pairwise distances (simplified: O(N²) but OK for cloud sizes)
        filtered_points = []

        for point in points:
            # Find neighbors within radius
            distances = np.linalg.norm(points - point, axis=1)
            neighbors = np.sum(distances < radius)

            if neighbors >= k:
                filtered_points.append(point)

        filtered_array = np.array(filtered_points, dtype=np.float32)

        logger.debug(
            f"🔍 Outlier removal: {len(points)} → {len(filtered_array)} points "
            f"(removed {len(points) - len(filtered_array)} outliers)"
        )

        return filtered_array

    def _array_to_pointcloud2(
        self,
        points: np.ndarray,
        frame_id: str = "lidar_link",
        timestamp=None
    ) -> PointCloud2:
        """
        Convert numpy array to ROS PointCloud2 message.

        Args:
            points: Array of shape (N, 3)
            frame_id: Frame ID for the point cloud
            timestamp: ROS Time (uses current if None)

        Returns:
            PointCloud2 message
        """
        return pc2.create_cloud_xyz32(
            frame_id=frame_id,
            timestamp=timestamp,
            xyz=points
        )

    def _log_statistics(self) -> None:
        """Log point cloud processing statistics."""
        reduction_ratio = (
            100.0 * (1.0 - self.point_count_filtered / max(self.point_count_raw, 1))
        )
        logger.info(
            f"📊 LiDAR Statistics: "
            f"Raw={self.point_count_raw:6d}, "
            f"Filtered={self.point_count_filtered:6d}, "
            f"Reduced={reduction_ratio:5.1f}%, "
            f"Time={self.processing_time_ms:5.1f}ms"
        )


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting LiDAR Processor...")
        logger.info("Topics:")
        logger.info("  Subscribe: /lidar/scan (PointCloud2)")
        logger.info("  Publish: /lidar/filtered (PointCloud2)")
        logger.info("")
        logger.info("To visualize with RViz2:")
        logger.info("  rviz2 -d /path/to/rviz.config")
        logger.info("  # Add /lidar/scan (original) and /lidar/filtered (processed)")

        processor = LiDARProcessor()
        rclpy.spin(processor)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
