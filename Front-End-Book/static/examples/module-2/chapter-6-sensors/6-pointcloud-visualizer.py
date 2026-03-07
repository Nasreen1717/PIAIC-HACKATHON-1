#!/usr/bin/env python3
"""
Chapter 6 Example: Point Cloud Visualization and Analysis

This example demonstrates:
- Subscribing to point cloud data
- Computing statistics (density, bounds, centroid)
- Performing spatial analysis (clustering, intensity mapping)
- Publishing colored point clouds for RViz visualization

Prerequisites:
- Point cloud data source (LiDAR, camera, etc.)
- ROS 2 Humble with PCL and numpy

Usage:
    python3 6-pointcloud-visualizer.py
    # In RViz2, add /pointcloud/colored PointCloud2 display
    # Watch console for statistics output every 5 frames

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import sys
import time
import logging
from typing import Optional, Tuple

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pc2
from std_msgs.msg import Header


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PointCloudVisualizer(Node):
    """
    Analyze and visualize point cloud data with statistics and coloring.

    Subscribes to:
    - /lidar/filtered or /camera/depth_pointcloud: Point cloud source

    Publishes:
    - /pointcloud/colored: Colored point cloud for visualization
    - /pointcloud/statistics: Logging statistics
    """

    def __init__(self):
        """Initialize point cloud visualizer."""
        super().__init__('pointcloud_visualizer')

        # Statistics tracking
        self.frame_count = 0
        self.total_points = 0
        self.max_density = 0.0
        self.processing_time_ms = 0.0

        # Bounds tracking
        self.global_bounds = {
            'min': np.array([float('inf'), float('inf'), float('inf')]),
            'max': np.array([float('-inf'), float('-inf'), float('-inf')])
        }

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscriber (flexible: can use any point cloud topic)
        self.create_subscription(
            PointCloud2,
            '/lidar/filtered',
            self.pointcloud_callback,
            qos_profile=qos_profile
        )

        # Publisher for colored point cloud
        self.colored_pub = self.create_publisher(
            PointCloud2,
            '/pointcloud/colored',
            qos_profile=qos_profile
        )

        logger.info("✅ Point Cloud Visualizer initialized")
        logger.info("   Input topic: /lidar/filtered")
        logger.info("   Output topic: /pointcloud/colored (RViz)")

    def pointcloud_callback(self, msg: PointCloud2) -> None:
        """
        Process and visualize point cloud.

        Args:
            msg: PointCloud2 message
        """
        start_time = time.time()

        try:
            # Convert to numpy array
            points = self._pointcloud2_to_array(msg)

            if points is None or len(points) == 0:
                logger.warning("⚠️  Empty point cloud")
                return

            self.total_points = len(points)

            # Compute statistics
            stats = self._compute_statistics(points)

            # Color points by height (Z-axis) for visualization
            colors = self._color_by_height(points)

            # Create colored point cloud
            colored_pc = self._create_colored_pointcloud(
                points,
                colors,
                frame_id=msg.header.frame_id,
                timestamp=msg.header.stamp
            )

            self.colored_pub.publish(colored_pc)

            # Track performance
            self.processing_time_ms = (time.time() - start_time) * 1000.0
            self.frame_count += 1

            # Log statistics periodically
            if self.frame_count % 5 == 0:
                self._log_statistics(stats)

        except Exception as e:
            logger.error(f"❌ Point cloud processing error: {e}")

    def _pointcloud2_to_array(self, pc_msg: PointCloud2) -> Optional[np.ndarray]:
        """
        Convert PointCloud2 message to numpy array.

        Args:
            pc_msg: ROS PointCloud2 message

        Returns:
            Array of shape (N, 3) or None if empty
        """
        points_list = list(pc2.read_points(pc_msg, skip_nans=True))

        if len(points_list) == 0:
            return None

        # Extract x, y, z
        points = np.array([(pt[0], pt[1], pt[2]) for pt in points_list],
                         dtype=np.float32)
        return points

    def _compute_statistics(self, points: np.ndarray) -> dict:
        """
        Compute point cloud statistics.

        Args:
            points: Array of shape (N, 3)

        Returns:
            Dictionary with statistics
        """
        stats = {}

        # Basic stats
        stats['count'] = len(points)
        stats['centroid'] = np.mean(points, axis=0)
        stats['bounds_min'] = np.min(points, axis=0)
        stats['bounds_max'] = np.max(points, axis=0)
        stats['size'] = stats['bounds_max'] - stats['bounds_min']

        # Density (assuming 1m × 1m × 1m volume)
        volume = 1.0
        if np.prod(stats['size']) > 0:
            volume = np.prod(stats['size'])
        stats['density'] = stats['count'] / volume

        # Update global bounds
        self.global_bounds['min'] = np.minimum(
            self.global_bounds['min'],
            stats['bounds_min']
        )
        self.global_bounds['max'] = np.maximum(
            self.global_bounds['max'],
            stats['bounds_max']
        )

        # Distance statistics
        distances = np.linalg.norm(points, axis=1)
        stats['distance_mean'] = np.mean(distances)
        stats['distance_min'] = np.min(distances)
        stats['distance_max'] = np.max(distances)

        return stats

    def _color_by_height(self, points: np.ndarray) -> np.ndarray:
        """
        Generate RGB colors based on Z-height.

        Low points: blue, high points: red

        Args:
            points: Array of shape (N, 3)

        Returns:
            Array of shape (N, 3) with RGB values [0-255]
        """
        z_values = points[:, 2]
        z_min = np.min(z_values)
        z_max = np.max(z_values)

        # Normalize to [0, 1]
        if z_max > z_min:
            z_normalized = (z_values - z_min) / (z_max - z_min)
        else:
            z_normalized = np.zeros_like(z_values)

        # Color map: blue (low) → green → red (high)
        colors = np.zeros((len(points), 3), dtype=np.uint8)

        for i, z_norm in enumerate(z_normalized):
            if z_norm < 0.5:
                # Blue to green
                colors[i, 0] = 0                           # Red
                colors[i, 1] = int(255 * (z_norm * 2))   # Green
                colors[i, 2] = int(255 * (1 - z_norm * 2))  # Blue
            else:
                # Green to red
                colors[i, 0] = int(255 * ((z_norm - 0.5) * 2))  # Red
                colors[i, 1] = int(255 * (1 - (z_norm - 0.5) * 2))  # Green
                colors[i, 2] = 0                                      # Blue

        return colors

    def _create_colored_pointcloud(
        self,
        points: np.ndarray,
        colors: np.ndarray,
        frame_id: str = "lidar_link",
        timestamp=None
    ) -> PointCloud2:
        """
        Create PointCloud2 message with RGB colors.

        Args:
            points: Point coordinates (N, 3)
            colors: RGB colors (N, 3) as uint8
            frame_id: Frame ID
            timestamp: ROS timestamp

        Returns:
            PointCloud2 message
        """
        # Create structured array with x, y, z, rgb
        num_points = len(points)
        data = np.zeros(num_points, dtype=[
            ('x', np.float32),
            ('y', np.float32),
            ('z', np.float32),
            ('rgb', np.uint32)
        ])

        data['x'] = points[:, 0]
        data['y'] = points[:, 1]
        data['z'] = points[:, 2]

        # Pack RGB into single uint32 (standard ROS format)
        # Format: R in highest byte, G in middle, B in lowest
        data['rgb'] = (
            (colors[:, 0].astype(np.uint32) << 16) |
            (colors[:, 1].astype(np.uint32) << 8) |
            colors[:, 2].astype(np.uint32)
        )

        # Create field descriptors
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='rgb', offset=12, datatype=PointField.UINT32, count=1),
        ]

        # Create header
        header = Header()
        header.frame_id = frame_id
        header.stamp = timestamp or self.get_clock().now().to_msg()

        # Create and return PointCloud2
        pc_msg = PointCloud2()
        pc_msg.header = header
        pc_msg.height = 1
        pc_msg.width = num_points
        pc_msg.is_dense = True
        pc_msg.is_bigendian = False
        pc_msg.fields = fields
        pc_msg.point_step = 16
        pc_msg.row_step = 16 * num_points
        pc_msg.data = data.tobytes()

        return pc_msg

    def _log_statistics(self, stats: dict) -> None:
        """
        Log point cloud statistics.

        Args:
            stats: Statistics dictionary
        """
        logger.info(
            f"📊 Point Cloud Stats: "
            f"Frame={self.frame_count}, "
            f"Points={stats['count']}, "
            f"Density={stats['density']:.0f} pts/m³, "
            f"Distance={stats['distance_min']:.2f}-{stats['distance_max']:.2f}m, "
            f"ProcessTime={self.processing_time_ms:.1f}ms"
        )

        logger.debug(
            f"   Centroid: ({stats['centroid'][0]:.2f}, "
            f"{stats['centroid'][1]:.2f}, {stats['centroid'][2]:.2f})m"
        )
        logger.debug(
            f"   Bounds: X=[{stats['bounds_min'][0]:.2f}, {stats['bounds_max'][0]:.2f}], "
            f"Y=[{stats['bounds_min'][1]:.2f}, {stats['bounds_max'][1]:.2f}], "
            f"Z=[{stats['bounds_min'][2]:.2f}, {stats['bounds_max'][2]:.2f}]"
        )


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting Point Cloud Visualizer...")
        logger.info("Topics:")
        logger.info("  Subscribe: /lidar/filtered (PointCloud2)")
        logger.info("  Publish: /pointcloud/colored (PointCloud2, colored by height)")
        logger.info("")
        logger.info("Visualization Instructions:")
        logger.info("1. Launch RViz2: rviz2")
        logger.info("2. Set Fixed Frame: lidar_link")
        logger.info("3. Add display: PointCloud2 → /pointcloud/colored")
        logger.info("4. Color encoding: RGB (from rgb field)")
        logger.info("5. Watch the colored point cloud update in real-time!")

        visualizer = PointCloudVisualizer()
        rclpy.spin(visualizer)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
