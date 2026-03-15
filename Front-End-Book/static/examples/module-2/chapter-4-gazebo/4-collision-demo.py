#!/usr/bin/env python3
"""
Collision Detection & Contact Forces Demo - ROS 2 Node

Purpose:
  Demonstrates Gazebo collision detection and contact force measurement.
  - Monitors contact states between objects
  - Displays collision forces in real-time
  - Shows contact point locations
  - Logs collision events

Features:
  - Real-time collision state monitoring
  - Contact force magnitude display (Newtons)
  - Contact point coordinates (XYZ)
  - Collision duration tracking
  - Human-readable collision reports

Requirements:
  - ROS 2 Humble
  - Gazebo 11+ with robots/objects loaded
  - gazebo_ros package

Usage:
  python3 4-collision-demo.py

Topics:
  - Input: /gazebo/contact_states (gazebo_msgs/ContactsState)
  - Input: /joint_states (sensor_msgs/JointState)
  - Output: Log to console

Date: 2026-01-22
Author: Module 2 - Digital Twin
License: MIT
"""

import time
from typing import Dict, Tuple

import rclpy
from rclpy.node import Node

from gazebo_msgs.msg import ContactsState, Contact
from sensor_msgs.msg import JointState


class CollisionDemo(Node):
    """
    ROS 2 node for collision detection and contact force analysis.

    Monitors /gazebo/contact_states topic for collision events.
    """

    def __init__(self):
        """Initialize collision demo node."""
        super().__init__('collision_demo')

        self.logger = self.get_logger()
        self.logger.info("CollisionDemo node initialized")

        # Track collision states
        self.active_collisions: Dict[Tuple[str, str], float] = {}  # (body1, body2) -> start_time
        self.collision_count = 0
        self.total_contact_events = 0
        self.max_force_seen = 0.0

        # Subscribe to contact states
        self.contacts_sub = self.create_subscription(
            ContactsState,
            '/gazebo/contact_states',
            self.contact_states_callback,
            10
        )

        # Also subscribe to joint states for additional context
        self.joint_states_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )

        # Timer for periodic status update
        self.create_timer(2.0, self.status_update)

        self.logger.info("✅ Subscribed to /gazebo/contact_states")
        self.logger.info("✅ Collision monitoring active")

    def contact_states_callback(self, msg: ContactsState) -> None:
        """
        Callback for /gazebo/contact_states topic.

        Analyzes collision contacts and displays information.

        Args:
            msg: gazebo_msgs/ContactsState containing:
                 - msg.contact: list of Contact messages
                   Each Contact contains:
                   - collision1: Name of first colliding body
                   - collision2: Name of second colliding body
                   - wrench: Force and torque at contact
                   - contact_positions: List of contact point positions
        """
        if not msg.contact:
            # No active collisions
            return

        self.total_contact_events += len(msg.contact)

        # Process each contact
        for contact in msg.contact:
            collision_key = self._normalize_collision_pair(
                contact.collision1.body_name,
                contact.collision2.body_name
            )

            # Track new collisions
            if collision_key not in self.active_collisions:
                self.active_collisions[collision_key] = time.time()
                self.collision_count += 1
                self._log_collision_start(contact, collision_key)

            # Analyze forces
            self._analyze_contact_forces(contact, collision_key)

    def _normalize_collision_pair(self, body1: str, body2: str) -> Tuple[str, str]:
        """
        Normalize collision pair (alphabetically sorted for consistency).

        Args:
            body1: First body name
            body2: Second body name

        Returns:
            Tuple of sorted names
        """
        return tuple(sorted([body1, body2]))

    def _log_collision_start(self, contact: Contact, collision_key: Tuple[str, str]) -> None:
        """
        Log when collision starts.

        Args:
            contact: Contact message
            collision_key: Normalized collision pair
        """
        body1, body2 = collision_key
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"🔴 COLLISION #{self.collision_count} STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Body 1: {body1}")
        self.logger.info(f"Body 2: {body2}")

        # Contact point information
        if contact.contact_positions:
            pos = contact.contact_positions[0]
            self.logger.info(
                f"Contact Point: ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}) meters"
            )
            # Show distance from origin
            dist = (pos.x**2 + pos.y**2 + pos.z**2) ** 0.5
            self.logger.info(f"Distance from origin: {dist:.3f} m")

        self.logger.info("=" * 80)

    def _analyze_contact_forces(self, contact: Contact, collision_key: Tuple[str, str]) -> None:
        """
        Analyze and log contact forces.

        Args:
            contact: Contact message with wrench (force/torque)
            collision_key: Collision pair identifier
        """
        # Extract force from wrench
        fx = contact.wrench.force.x
        fy = contact.wrench.force.y
        fz = contact.wrench.force.z

        # Calculate magnitude
        force_magnitude = (fx**2 + fy**2 + fz**2) ** 0.5

        # Track maximum force
        if force_magnitude > self.max_force_seen:
            self.max_force_seen = force_magnitude

        # Log contact forces (only if significant)
        if force_magnitude > 0.1:  # Only log forces > 0.1 N
            body1, body2 = collision_key

            # Determine which direction the force is acting
            if force_magnitude > 10.0:  # High force
                indicator = "⚠️ HIGH FORCE"
            elif force_magnitude > 5.0:  # Medium force
                indicator = "📊 MEDIUM FORCE"
            else:  # Low force
                indicator = "📈 CONTACT"

            self.logger.info(
                f"{indicator}: {body1} ↔ {body2} "
                f"| Force: {force_magnitude:.2f} N "
                f"({fx:7.2f}, {fy:7.2f}, {fz:7.2f}) N"
            )

    def joint_states_callback(self, msg: JointState) -> None:
        """
        Callback for /joint_states (for context).

        Args:
            msg: Current joint states
        """
        # Could be used to correlate collisions with joint positions
        # Not actively used in this demo, but available for extension
        pass

    def status_update(self) -> None:
        """Periodic status update."""
        if not self.active_collisions:
            return

        # Log current collision status
        self.logger.info("\n" + "-" * 80)
        self.logger.info(f"📊 COLLISION STATUS (Total Events: {self.total_contact_events})")
        self.logger.info("-" * 80)

        current_time = time.time()
        for (body1, body2), start_time in list(self.active_collisions.items()):
            duration = current_time - start_time
            self.logger.info(
                f"  ⚡ {body1} ↔ {body2}: {duration:.1f}s duration"
            )

        self.logger.info(f"  📈 Total collisions detected: {self.collision_count}")
        self.logger.info(f"  📊 Max force observed: {self.max_force_seen:.2f} N")
        self.logger.info("-" * 80)

    def shutdown(self) -> None:
        """Cleanup and final statistics."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("COLLISION DEMO STATISTICS")
        self.logger.info("=" * 80)
        self.logger.info(f"Total collision events: {self.collision_count}")
        self.logger.info(f"Total contact updates: {self.total_contact_events}")
        self.logger.info(f"Maximum force recorded: {self.max_force_seen:.2f} N")

        if self.active_collisions:
            self.logger.info(f"Active collisions at shutdown: {len(self.active_collisions)}")
            for (body1, body2) in self.active_collisions.items():
                self.logger.info(f"  - {body1} ↔ {body2}")

        self.logger.info("=" * 80)


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)

    demo = CollisionDemo()

    try:
        print("\n" + "=" * 80)
        print("Collision Detection Demo Running")
        print("Monitoring /gazebo/contact_states for collisions...")
        print("Press Ctrl+C to stop")
        print("=" * 80 + "\n")

        rclpy.spin(demo)

    except KeyboardInterrupt:
        print("\n⏸️  Interrupted by user")

    finally:
        demo.shutdown()
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    exit(main())
