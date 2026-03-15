#!/usr/bin/env python3
"""
Chapter 6 Example: Sensor Fusion with Extended Kalman Filter (EKF)

This example demonstrates:
- Multi-sensor fusion combining IMU, visual odometry, and LiDAR
- Extended Kalman Filter for robust state estimation
- Time synchronization of asynchronous sensors
- Handling sensor uncertainty and noise

Prerequisites:
- Multiple sensors available (IMU, camera/visual odometry, LiDAR)
- ROS 2 Humble with message_filters package
- ApproximateTimeSynchronizer for synchronized subscriptions

Usage:
    python3 6-sensor-fusion.py
    # Watch /robot/fused_odometry for combined estimate
    # Covariance values indicate uncertainty

Key Concepts:
- Predict step: Use motion model (IMU) to predict next state
- Update step: Correct prediction using measurement (camera, LiDAR)
- Covariance: Uncertainty ellipse shrinks with good measurements

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import sys
import time
import logging
from typing import Tuple, Optional

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from message_filters import Subscriber, ApproximateTimeSynchronizer
from geometry_msgs.msg import Quaternion
from std_msgs.msg import Header


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtendedKalmanFilter:
    """
    Simplified Extended Kalman Filter for 3D pose estimation.

    State: [x, y, z, vx, vy, vz] (position and velocity)
    """

    def __init__(self, dt: float = 0.01):
        """
        Initialize EKF.

        Args:
            dt: Nominal time step (seconds)
        """
        # State: [x, y, z, vx, vy, vz]
        self.state = np.zeros(6)

        # State covariance (uncertainty)
        self.P = np.eye(6) * 0.1  # Initial uncertainty

        # Process noise (how much we trust our motion model)
        self.Q = np.eye(6) * 0.01

        # Measurement noise (how much we trust sensors)
        self.R_imu = np.eye(3) * 0.05  # IMU (acceleration)
        self.R_odom = np.eye(3) * 0.1  # Odometry (position)

        self.dt = dt

    def predict(self, imu_accel: np.ndarray) -> None:
        """
        Predict step using motion model.

        Args:
            imu_accel: Accelerometer reading [ax, ay, az]
        """
        # Motion model: x += v*dt, v += a*dt
        F = np.eye(6)
        F[0, 3] = self.dt  # x += vx*dt
        F[1, 4] = self.dt  # y += vy*dt
        F[2, 5] = self.dt  # z += vz*dt

        # Update state using motion model
        accel_input = np.array([imu_accel[0] * self.dt,
                                imu_accel[1] * self.dt,
                                imu_accel[2] * self.dt])
        self.state = F @ self.state
        self.state[3:6] += imu_accel  # Add acceleration directly to velocity

        # Predict covariance
        self.P = F @ self.P @ F.T + self.Q

    def update_position(self, measured_pos: np.ndarray) -> None:
        """
        Update step using position measurement.

        Args:
            measured_pos: Measured position [x, y, z] from odometry/camera
        """
        # Measurement matrix (we measure position directly)
        H = np.zeros((3, 6))
        H[0, 0] = 1  # measure x
        H[1, 1] = 1  # measure y
        H[2, 2] = 1  # measure z

        # Innovation (difference between measurement and prediction)
        innovation = measured_pos - self.state[0:3]

        # Innovation covariance
        S = H @ self.P @ H.T + self.R_odom

        # Kalman gain (how much to trust measurement vs prediction)
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update state
        self.state = self.state + K @ innovation

        # Update covariance
        self.P = (np.eye(6) - K @ H) @ self.P

    def get_state(self) -> np.ndarray:
        """Get current state estimate."""
        return self.state.copy()

    def get_covariance(self) -> np.ndarray:
        """Get current covariance (uncertainty)."""
        return self.P.copy()


class SensorFusionNode(Node):
    """
    Fuse multiple sensors using Extended Kalman Filter.

    Subscribes to (synchronized):
    - /imu/data: Accelerometer and gyroscope
    - /visual_odometry: Camera-based position estimate
    - /lidar_odometry: LiDAR-based position estimate (optional)

    Publishes:
    - /robot/fused_odometry: Combined estimate with lower uncertainty
    """

    def __init__(self):
        """Initialize sensor fusion node."""
        super().__init__('sensor_fusion')

        # Initialize EKF
        self.ekf = ExtendedKalmanFilter(dt=0.01)

        # Statistics
        self.update_count = 0
        self.last_log_time = time.time()

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers with time synchronization
        imu_sub = Subscriber(
            self,
            Imu,
            '/imu/data',
            qos_profile=qos_profile
        )
        odom_sub = Subscriber(
            self,
            Odometry,
            '/visual_odometry',
            qos_profile=qos_profile
        )

        # Synchronize messages (allow up to 0.1s time difference)
        self.sync = ApproximateTimeSynchronizer(
            [imu_sub, odom_sub],
            queue_size=10,
            slop=0.1
        )
        self.sync.registerCallback(self.sensor_callback)

        # Publisher
        self.fused_pub = self.create_publisher(
            Odometry,
            '/robot/fused_odometry',
            qos_profile=qos_profile
        )

        logger.info("✅ Sensor Fusion Node initialized")
        logger.info("   Using Extended Kalman Filter")
        logger.info("   Fusing: IMU (motion) + Visual Odometry (position)")

    def sensor_callback(self, imu_msg: Imu, odom_msg: Odometry) -> None:
        """
        Sensor fusion callback with time-synchronized data.

        Args:
            imu_msg: IMU message
            odom_msg: Visual odometry message
        """
        try:
            # Extract measurements
            imu_accel = np.array([
                imu_msg.linear_acceleration.x,
                imu_msg.linear_acceleration.y,
                imu_msg.linear_acceleration.z
            ])

            odom_pos = np.array([
                odom_msg.pose.pose.position.x,
                odom_msg.pose.pose.position.y,
                odom_msg.pose.pose.position.z
            ])

            # EKF Predict step (using IMU)
            self.ekf.predict(imu_accel)

            # EKF Update step (using visual odometry)
            self.ekf.update_position(odom_pos)

            # Publish fused estimate
            self._publish_fused_odometry(imu_msg.header)

            self.update_count += 1

            # Log statistics every 2 seconds
            current_time = time.time()
            if current_time - self.last_log_time >= 2.0:
                self._log_fusion_statistics()
                self.last_log_time = current_time

        except Exception as e:
            logger.error(f"❌ Sensor fusion error: {e}")

    def _publish_fused_odometry(self, header: Header) -> None:
        """
        Publish fused odometry estimate.

        Args:
            header: ROS message header
        """
        odom = Odometry()

        # Header
        odom.header = Header()
        odom.header.frame_id = 'odom'
        odom.header.stamp = header.stamp
        odom.child_frame_id = 'base_link'

        # State
        state = self.ekf.get_state()
        covariance = self.ekf.get_covariance()

        # Position
        odom.pose.pose.position.x = float(state[0])
        odom.pose.pose.position.y = float(state[1])
        odom.pose.pose.position.z = float(state[2])

        # Orientation (identity for now)
        odom.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

        # Pose covariance from EKF
        odom.pose.covariance[0] = float(covariance[0, 0])   # x variance
        odom.pose.covariance[7] = float(covariance[1, 1])   # y variance
        odom.pose.covariance[14] = float(covariance[2, 2])  # z variance

        # Velocity
        odom.twist.twist.linear.x = float(state[3])
        odom.twist.twist.linear.y = float(state[4])
        odom.twist.twist.linear.z = float(state[5])

        # Twist covariance
        odom.twist.covariance[0] = float(covariance[3, 3])   # vx variance
        odom.twist.covariance[7] = float(covariance[4, 4])   # vy variance
        odom.twist.covariance[14] = float(covariance[5, 5])  # vz variance

        self.fused_pub.publish(odom)

    def _log_fusion_statistics(self) -> None:
        """Log sensor fusion statistics and uncertainty."""
        state = self.ekf.get_state()
        cov = self.ekf.get_covariance()

        # Position uncertainty (standard deviation)
        pos_std = np.sqrt(np.diag(cov)[0:3])

        logger.info(
            f"📊 Sensor Fusion Stats: "
            f"Position=({state[0]:.2f}, {state[1]:.2f}, {state[2]:.2f})m, "
            f"Uncertainty=±({pos_std[0]:.3f}, {pos_std[1]:.3f}, {pos_std[2]:.3f})m"
        )


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting Sensor Fusion Node (EKF)...")
        logger.info("Topics:")
        logger.info("  Subscribe: /imu/data (Imu)")
        logger.info("  Subscribe: /visual_odometry (Odometry)")
        logger.info("  Publish: /robot/fused_odometry (Odometry)")
        logger.info("")
        logger.info("EKF Benefits:")
        logger.info("  ✓ Combines multiple sensors")
        logger.info("  ✓ Reduces drift from dead reckoning")
        logger.info("  ✓ Estimates uncertainty (covariance)")
        logger.info("  ✓ Optimal state estimate")

        fusion = SensorFusionNode()
        rclpy.spin(fusion)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
