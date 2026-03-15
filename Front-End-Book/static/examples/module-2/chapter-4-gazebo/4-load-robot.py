#!/usr/bin/env python3
"""
Gazebo Robot Loader - ROS 2 Node

Purpose:
  Load a robot model (URDF) into a running Gazebo simulation using ROS 2 services.
  This example demonstrates:
  - ROS 2 service client to spawn entities in Gazebo
  - Waiting for services to be available
  - Reading URDF from file
  - Verifying successful robot loading

Requirements:
  - ROS 2 Humble
  - Gazebo 11+
  - gazebo_ros package (for SpawnEntity service)
  - Running gzserver with gazebo_ros plugins

Usage:
  python3 4-load-robot.py --urdf humanoid.urdf --name humanoid --x 0 --y 0 --z 1

Date: 2026-01-22
Author: Module 2 - Digital Twin
License: MIT
"""

import argparse
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from gazebo_msgs.srv import SpawnEntity, DeleteEntity
from sensor_msgs.msg import JointState


class RobotLoader(Node):
    """ROS 2 node for loading robots into Gazebo."""

    def __init__(self):
        """Initialize the robot loader node."""
        super().__init__('robot_loader')

        # Logging
        self.logger = self.get_logger()
        self.logger.info("RobotLoader node initialized")

        # Service clients
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')

        # Subscription to verify robot loaded
        self.joint_state_sub = None
        self.robot_loaded = False

    def wait_for_service(self, client, service_name: str, timeout: int = 30) -> bool:
        """
        Wait for a ROS 2 service to become available.

        Args:
            client: The service client to check
            service_name: Name of service (for logging)
            timeout: Maximum seconds to wait

        Returns:
            True if service available, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if client.service_is_ready():
                self.logger.info(f"✅ Service available: {service_name}")
                return True

            self.logger.info(f"⏳ Waiting for service: {service_name}...")
            time.sleep(1)

        self.logger.error(f"❌ Service timeout: {service_name}")
        return False

    def load_urdf(self, urdf_path: str) -> str:
        """
        Load URDF from file.

        Args:
            urdf_path: Path to URDF file

        Returns:
            URDF content as string

        Raises:
            FileNotFoundError: If URDF file not found
        """
        path = Path(urdf_path)
        if not path.exists():
            raise FileNotFoundError(f"URDF file not found: {urdf_path}")

        self.logger.info(f"📄 Loading URDF: {urdf_path}")
        with open(urdf_path, 'r') as f:
            urdf_content = f.read()

        self.logger.info(f"✅ URDF loaded ({len(urdf_content)} bytes)")
        return urdf_content

    def spawn_robot(
        self,
        urdf_path: str,
        entity_name: str,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 1.0,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0,
    ) -> bool:
        """
        Spawn a robot in Gazebo.

        Args:
            urdf_path: Path to URDF file
            entity_name: Name to give robot in Gazebo
            x, y, z: Position in meters
            roll, pitch, yaw: Orientation in radians

        Returns:
            True if spawn successful, False otherwise
        """
        # Wait for spawn service
        if not self.wait_for_service(self.spawn_client, '/spawn_entity'):
            return False

        try:
            # Load URDF
            urdf_content = self.load_urdf(urdf_path)

            # Create spawn request
            request = SpawnEntity.Request()
            request.name = entity_name
            request.xml = urdf_content
            request.robot_namespace = ''
            request.initial_pose.position.x = x
            request.initial_pose.position.y = y
            request.initial_pose.position.z = z

            # Quaternion from Euler (for initial_pose.orientation)
            # Using simple conversion for small angles (yaw only for this example)
            import math
            cy = math.cos(yaw * 0.5)
            sy = math.sin(yaw * 0.5)
            cp = math.cos(pitch * 0.5)
            sp = math.sin(pitch * 0.5)
            cr = math.cos(roll * 0.5)
            sr = math.sin(roll * 0.5)

            request.initial_pose.orientation.w = cr * cp * cy + sr * sp * sy
            request.initial_pose.orientation.x = sr * cp * cy - cr * sp * sy
            request.initial_pose.orientation.y = cr * sp * cy + sr * cp * sy
            request.initial_pose.orientation.z = cr * cp * sy - sr * sp * cy

            self.logger.info(
                f"🤖 Spawning robot '{entity_name}' at "
                f"({x:.2f}, {y:.2f}, {z:.2f})"
            )

            # Call spawn service
            future = self.spawn_client.call_async(request)

            # Wait for response
            while rclpy.ok():
                if future.done():
                    result = future.result()
                    if result.success:
                        self.logger.info(f"✅ Robot spawned successfully: {entity_name}")
                        self.robot_loaded = True
                        return True
                    else:
                        self.logger.error(
                            f"❌ Failed to spawn robot: {result.status_message}"
                        )
                        return False
                time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"❌ Error during spawn: {e}")
            return False

    def verify_robot_loaded(self, timeout: int = 10) -> bool:
        """
        Verify robot is loaded by checking for /joint_states topic.

        Args:
            timeout: Maximum seconds to wait for joint_states

        Returns:
            True if joint states received, False if timeout
        """
        self.logger.info("🔍 Verifying robot loaded (waiting for /joint_states)...")

        # Create subscriber
        self.joint_states_received = False

        def joint_state_callback(msg: JointState):
            self.joint_states_received = True
            self.logger.info(
                f"✅ Joint states received! "
                f"Joints: {list(msg.name)}"
            )

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            joint_state_callback,
            10
        )

        # Wait for joint states
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.joint_states_received:
                return True
            time.sleep(0.1)

        self.logger.warning(
            f"⏱️  Timeout waiting for /joint_states "
            f"({timeout}s) - robot may not have published yet"
        )
        return False

    def delete_robot(self, entity_name: str) -> bool:
        """
        Delete a robot from Gazebo.

        Args:
            entity_name: Name of entity to delete

        Returns:
            True if delete successful, False otherwise
        """
        if not self.wait_for_service(self.delete_client, '/delete_entity'):
            return False

        try:
            request = DeleteEntity.Request()
            request.name = entity_name

            self.logger.info(f"🗑️  Deleting entity: {entity_name}")

            future = self.delete_client.call_async(request)

            while rclpy.ok():
                if future.done():
                    result = future.result()
                    if result.success:
                        self.logger.info(f"✅ Entity deleted: {entity_name}")
                        return True
                    else:
                        self.logger.error(
                            f"❌ Failed to delete entity: {result.status_message}"
                        )
                        return False
                time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"❌ Error during delete: {e}")
            return False


def main(args=None):
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Load a robot into Gazebo simulation'
    )
    parser.add_argument(
        '--urdf',
        type=str,
        default='humanoid.urdf',
        help='Path to URDF file (default: humanoid.urdf)'
    )
    parser.add_argument(
        '--name',
        type=str,
        default='robot',
        help='Name for robot in Gazebo (default: robot)'
    )
    parser.add_argument(
        '--x',
        type=float,
        default=0.0,
        help='Initial X position in meters (default: 0)'
    )
    parser.add_argument(
        '--y',
        type=float,
        default=0.0,
        help='Initial Y position in meters (default: 0)'
    )
    parser.add_argument(
        '--z',
        type=float,
        default=1.0,
        help='Initial Z position in meters (default: 1.0 to avoid ground)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify robot loaded by checking joint_states topic'
    )

    cmd_args = parser.parse_args()

    # Initialize ROS 2
    rclpy.init(args=args)

    # Create node
    loader = RobotLoader()

    try:
        # Spawn robot
        success = loader.spawn_robot(
            urdf_path=cmd_args.urdf,
            entity_name=cmd_args.name,
            x=cmd_args.x,
            y=cmd_args.y,
            z=cmd_args.z,
        )

        if not success:
            loader.logger.error("Failed to spawn robot")
            return 1

        # Verify loaded
        if cmd_args.verify:
            if loader.verify_robot_loaded(timeout=10):
                loader.logger.info("✅ Robot successfully loaded and publishing!")
            else:
                loader.logger.warning("⚠️  Robot may not be publishing joint states yet")

        loader.logger.info("\n" + "=" * 50)
        loader.logger.info("Robot loader complete!")
        loader.logger.info("=" * 50)

        return 0

    except KeyboardInterrupt:
        loader.logger.info("\n⏸️  Interrupted by user")
        return 0

    except Exception as e:
        loader.logger.error(f"Unhandled exception: {e}")
        return 1

    finally:
        # Cleanup
        rclpy.shutdown()


if __name__ == '__main__':
    exit(main())
