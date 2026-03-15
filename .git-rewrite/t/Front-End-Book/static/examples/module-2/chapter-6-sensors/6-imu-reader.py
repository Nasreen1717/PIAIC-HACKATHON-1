#!/usr/bin/env python3
"""
Chapter 6 Example: IMU Sensor Reading and Dead Reckoning

This example demonstrates:
- Subscribing to IMU sensor data (accelerometer, gyroscope, magnetometer)
- Computing motion using dead reckoning (velocity, position integration)
- Tracking sensor drift accumulation
- Publishing odometry estimates

Prerequisites:
- Gazebo with IMU sensor on robot
- ROS 2 Humble with geometry/nav_msgs packages
- IMU publishing at >50Hz for good integration accuracy

Usage:
    python3 6-imu-reader.py
    # Watch /imu/odometry for dead reckoning position estimate
    # Statistics printed to console every 2 seconds

Important Notes:
- Dead reckoning accumulates error (drift) over time
- Use only for short-term estimates (~1-10 seconds)
- Sensor fusion (EKF) combines with other sensors for long-term accuracy

Author: Educational Module
Date: 2026-01-22
License: MIT
"""

import sys
import time
import logging
from typing import Tuple, Optional
from collections import deque

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, PoseWithCovariance, Twist, TwistWithCovariance
from std_msgs.msg import Header


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IMUOdometer(Node):
    """
    Perform dead reckoning using IMU sensor data.

    Subscribes to:
    - /imu/data: Accelerometer, gyroscope, magnetometer from Gazebo IMU plugin

    Publishes:
    - /imu/odometry: Estimated pose and velocity using dead reckoning

    State tracking:
    - Position (x, y, z)
    - Velocity (vx, vy, vz)
    - Orientation (as quaternion or Euler angles)
    """

    def __init__(self):
        """Initialize IMU odometer node."""
        super().__init__('imu_odometer')

        # Position and velocity state
        self.position = np.array([0.0, 0.0, 0.0])  # x, y, z meters
        self.velocity = np.array([0.0, 0.0, 0.0])  # vx, vy, vz m/s
        self.orientation = np.array([0.0, 0.0, 1.0, 0.0])  # quaternion (x,y,z,w)

        # Acceleration offset (for calibration, typically small)
        self.accel_bias = np.array([0.0, 0.0, 0.0])

        # Last message timestamp for numerical integration
        self.last_timestamp: Optional[float] = None
        self.sequence_number = 0

        # Statistics for drift analysis
        self.max_velocity = 0.0
        self.total_distance = 0.0
        self.drift_samples = deque(maxlen=100)

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscriber
        self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            qos_profile=qos_profile
        )

        # Publisher
        self.odometry_pub = self.create_publisher(
            Odometry,
            '/imu/odometry',
            qos_profile=qos_profile
        )

        logger.info("✅ IMU Odometer initialized")
        logger.info("   Starting position: (0, 0, 0)")
        logger.info("   Integration method: Euler (velocity + position)")

    def imu_callback(self, msg: Imu) -> None:
        """
        Process IMU data and update odometry estimate.

        Args:
            msg: IMU message with acceleration, angular velocity
        """
        # Get accelerometer and gyroscope data
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])
        gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Current timestamp in seconds
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9

        # First message: initialize time reference
        if self.last_timestamp is None:
            self.last_timestamp = current_time
            logger.info(f"📍 IMU data started at {current_time:.3f}s")
            return

        # Time delta (seconds)
        dt = current_time - self.last_timestamp

        # Clamp dt to reasonable range (avoid discontinuities)
        if dt < 0.001 or dt > 1.0:
            logger.warning(
                f"⚠️  Unusual time delta: {dt:.3f}s "
                f"(skipping integration step)"
            )
            self.last_timestamp = current_time
            return

        # Apply acceleration bias and integrate velocity
        accel_corrected = accel - self.accel_bias
        self.velocity += accel_corrected * dt

        # Integrate velocity to get position
        self.position += self.velocity * dt

        # Update orientation using gyroscope (simplified integration)
        # In production, use proper quaternion integration
        self._integrate_gyroscope(gyro, dt)

        # Track statistics
        speed = np.linalg.norm(self.velocity)
        self.max_velocity = max(self.max_velocity, speed)
        self.total_distance += speed * dt

        # Publish odometry estimate
        self._publish_odometry(msg.header.frame_id, current_time)

        # Update for next iteration
        self.last_timestamp = current_time
        self.sequence_number += 1

        # Log statistics periodically
        if self.sequence_number % 100 == 0:
            self._log_statistics(speed)

    def _integrate_gyroscope(self, gyro: np.ndarray, dt: float) -> None:
        """
        Update orientation using angular velocity (gyroscope).

        Simple Euler angle integration (not ideal for large rotations).
        In production, use proper quaternion integration.

        Args:
            gyro: Angular velocity [wx, wy, wz] in rad/s
            dt: Time delta in seconds
        """
        # This is simplified; proper implementation uses quaternion dynamics
        # For now, we just note that gyro should integrate to update orientation
        logger.debug(f"Gyro: {gyro} rad/s, dt={dt:.3f}s")

    def _publish_odometry(self, frame_id: str, timestamp: float) -> None:
        """
        Publish current odometry estimate.

        Args:
            frame_id: Coordinate frame (e.g., 'odom')
            timestamp: ROS time in seconds
        """
        odom = Odometry()

        # Header
        odom.header = Header()
        odom.header.frame_id = frame_id or 'odom'
        odom.header.seq = self.sequence_number
        odom.child_frame_id = 'base_link'

        # Set timestamp
        sec = int(timestamp)
        nanosec = int((timestamp - sec) * 1e9)
        odom.header.stamp.sec = sec
        odom.header.stamp.nanosec = nanosec

        # Position
        odom.pose.pose.position.x = float(self.position[0])
        odom.pose.pose.position.y = float(self.position[1])
        odom.pose.pose.position.z = float(self.position[2])

        # Orientation (quaternion)
        odom.pose.pose.orientation.x = float(self.orientation[0])
        odom.pose.pose.orientation.y = float(self.orientation[1])
        odom.pose.pose.orientation.z = float(self.orientation[2])
        odom.pose.pose.orientation.w = float(self.orientation[3])

        # Pose covariance (increased for dead reckoning!)
        odom.pose.covariance[0] = 0.1   # x variance increases with time
        odom.pose.covariance[7] = 0.1   # y variance
        odom.pose.covariance[14] = 0.1  # z variance

        # Velocity
        odom.twist.twist.linear.x = float(self.velocity[0])
        odom.twist.twist.linear.y = float(self.velocity[1])
        odom.twist.twist.linear.z = float(self.velocity[2])

        # Twist covariance
        odom.twist.covariance[0] = 0.01  # vx variance
        odom.twist.covariance[7] = 0.01  # vy variance
        odom.twist.covariance[14] = 0.01 # vz variance

        self.odometry_pub.publish(odom)

    def _log_statistics(self, current_speed: float) -> None:
        """
        Log motion statistics and drift analysis.

        Args:
            current_speed: Current velocity magnitude
        """
        logger.info(
            f"📊 IMU Dead Reckoning Stats: "
            f"Position=({self.position[0]:.2f}, {self.position[1]:.2f}, {self.position[2]:.2f})m, "
            f"Speed={current_speed:.2f}m/s, "
            f"MaxSpeed={self.max_velocity:.2f}m/s, "
            f"Distance={self.total_distance:.2f}m"
        )


def main():
    """Main entry point."""
    rclpy.init()

    try:
        logger.info("Starting IMU Odometer (Dead Reckoning)...")
        logger.info("Topics:")
        logger.info("  Subscribe: /imu/data (Imu)")
        logger.info("  Publish: /imu/odometry (Odometry)")
        logger.info("")
        logger.info("⚠️  Warning: Dead reckoning accumulates drift!")
        logger.info("   Use for short-term estimates only (~1-10 seconds)")
        logger.info("   For long-term, use sensor fusion (EKF)")

        odometer = IMUOdometer()
        rclpy.spin(odometer)

    except KeyboardInterrupt:
        logger.info("✋ Shutdown requested")
    finally:
        rclpy.shutdown()
        logger.info("✅ Node shutdown complete")


if __name__ == '__main__':
    main()
