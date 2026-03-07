#!/usr/bin/env python3
"""
Simple Joint Controller - ROS 2 Node

Purpose:
  Demonstrates basic joint control in Gazebo using ROS 2 topics.
  - Subscribes to /joint_states for feedback
  - Publishes sinusoidal joint commands
  - Shows real-time feedback control loop

Features:
  - 10 Hz control loop (10 updates per second)
  - Sinusoidal motion pattern (smooth, natural movement)
  - Feedback-based control (reads joint states, sends commands)
  - Graceful shutdown on Ctrl+C
  - Logging of all joint states and commands

Requirements:
  - ROS 2 Humble
  - Gazebo 11+ with humanoid robot loaded
  - Run after 4-load-robot.py

Usage:
  python3 4-joint-controller.py

  Options:
    --amplitude : Sinusoidal amplitude in radians (default: 0.5)
    --frequency : Sinusoidal frequency in Hz (default: 0.5)
    --rate      : Control loop rate in Hz (default: 10)

Example:
  python3 4-joint-controller.py --amplitude 0.3 --frequency 1.0

Date: 2026-01-22
Author: Module 2 - Digital Twin
License: MIT
"""

import argparse
import math
import time
from typing import Dict, List

import rclpy
from rclpy.node import Node
from rclpy.timer import Timer

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class SimpleJointController(Node):
    """
    Simple joint controller for Gazebo robots.

    Implements:
    - Joint state subscription (feedback)
    - Sinusoidal command generation
    - ROS 2 topic publishing (commands)
    """

    def __init__(
        self,
        amplitude: float = 0.5,
        frequency: float = 0.5,
        control_rate: float = 10.0,
    ):
        """
        Initialize joint controller.

        Args:
            amplitude: Sinusoidal motion amplitude in radians (default: 0.5 rad ≈ 28°)
            frequency: Sinusoidal motion frequency in Hz (default: 0.5 Hz = 2 sec period)
            control_rate: Control loop frequency in Hz (default: 10 Hz)
        """
        super().__init__('simple_joint_controller')

        # Parameters
        self.amplitude = amplitude
        self.frequency = frequency
        self.control_rate = control_rate
        self.period = 1.0 / control_rate

        # State tracking
        self.joint_names: List[str] = []
        self.current_positions: Dict[str, float] = {}
        self.current_velocities: Dict[str, float] = {}
        self.current_efforts: Dict[str, float] = {}
        self.time_step = 0

        # Logging
        self.logger = self.get_logger()
        self.logger.info("SimpleJointController initialized")
        self.logger.info(f"  Amplitude: {self.amplitude:.3f} rad ({math.degrees(self.amplitude):.1f}°)")
        self.logger.info(f"  Frequency: {self.frequency:.3f} Hz")
        self.logger.info(f"  Control rate: {self.control_rate:.1f} Hz")

        # ROS 2 subscriptions
        self.joint_states_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10  # Queue size
        )

        # ROS 2 publishers (joint commands)
        self.cmd_publisher = self.create_publisher(
            Float64MultiArray,
            '/gazebo/humanoid/cmd_pos',  # Topic for joint position commands
            10
        )

        # Timer for control loop
        self.timer: Timer = self.create_timer(
            self.period,  # Period in seconds
            self.control_loop_callback
        )

        self.logger.info("✅ Subscribed to /joint_states")
        self.logger.info(f"✅ Publishing to /gazebo/humanoid/cmd_pos at {self.control_rate} Hz")

    def joint_states_callback(self, msg: JointState) -> None:
        """
        Callback for /joint_states topic.

        Extracts current joint positions, velocities, and efforts for feedback control.

        Args:
            msg: sensor_msgs/JointState message containing:
                 - msg.name: list of joint names
                 - msg.position: list of current angles (radians)
                 - msg.velocity: list of current velocities (rad/s)
                 - msg.effort: list of current torques (N⋅m)
        """
        self.joint_names = list(msg.name)

        # Store current state for each joint
        for i, name in enumerate(msg.name):
            self.current_positions[name] = msg.position[i]
            self.current_velocities[name] = msg.velocity[i]
            self.current_efforts[name] = msg.effort[i]

    def compute_sinusoidal_command(self, joint_idx: int) -> float:
        """
        Compute sinusoidal command for a joint.

        Pattern: position = amplitude * sin(2π * frequency * time)

        This creates smooth, natural-looking motion that oscillates between
        [-amplitude, +amplitude] with period 1/frequency seconds.

        Args:
            joint_idx: Index of joint (0, 1, 2, ...)

        Returns:
            Desired joint position in radians
        """
        time_val = self.time_step * self.period

        # Phase offset for each joint (stagger motion for visual interest)
        # Joint 0: phase 0; Joint 1: phase 90°; Joint 2: phase 180°; etc.
        phase_offset = (joint_idx * math.pi / 2.0)

        # Sinusoidal equation
        command = self.amplitude * math.sin(
            2 * math.pi * self.frequency * time_val + phase_offset
        )

        return command

    def control_loop_callback(self) -> None:
        """
        Main control loop callback.

        Called at control_rate (default 10 Hz).
        Generates sinusoidal commands and publishes to Gazebo.
        """
        # Generate commands for all joints
        commands = []
        for joint_idx in range(len(self.joint_names)):
            cmd = self.compute_sinusoidal_command(joint_idx)
            commands.append(cmd)

        # Publish commands
        msg = Float64MultiArray()
        msg.data = commands
        self.cmd_publisher.publish(msg)

        # Log periodically (every 10 iterations = every 1 second at 10 Hz)
        if self.time_step % 10 == 0:
            self._log_state(commands)

        # Increment timestep
        self.time_step += 1

    def _log_state(self, commands: List[float]) -> None:
        """
        Log current state for debugging.

        Args:
            commands: List of joint commands just published
        """
        if not self.joint_names:
            self.logger.info("⏳ Waiting for joint_states...")
            return

        # Format joint info
        joint_info = []
        for i, name in enumerate(self.joint_names):
            pos = self.current_positions.get(name, 0.0)
            vel = self.current_velocities.get(name, 0.0)
            cmd = commands[i] if i < len(commands) else 0.0

            joint_info.append(
                f"{name:15s} pos={pos:7.3f} "
                f"vel={vel:7.3f} cmd={cmd:7.3f}"
            )

        elapsed = self.time_step * self.period

        # Log header on first iteration
        if self.time_step == 10:
            self.logger.info("\n" + "=" * 70)
            self.logger.info("CONTROL LOOP ACTIVE - Joint States and Commands")
            self.logger.info("=" * 70)

        # Log state
        self.logger.info(f"[{elapsed:6.1f}s] " + " | ".join(joint_info))

    def shutdown(self) -> None:
        """Cleanup on shutdown."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("SHUTDOWN: Stopping joint controller")
        self.logger.info(f"Total iterations: {self.time_step}")
        self.logger.info(f"Total time: {self.time_step * self.period:.1f}s")
        self.logger.info("=" * 70)


def main(args=None):
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Simple ROS 2 joint controller for Gazebo robots'
    )
    parser.add_argument(
        '--amplitude',
        type=float,
        default=0.5,
        help='Sinusoidal amplitude in radians (default: 0.5, ≈ 28°)'
    )
    parser.add_argument(
        '--frequency',
        type=float,
        default=0.5,
        help='Sinusoidal frequency in Hz (default: 0.5)'
    )
    parser.add_argument(
        '--rate',
        type=float,
        default=10.0,
        help='Control loop rate in Hz (default: 10)'
    )

    cmd_args = parser.parse_args()

    # Initialize ROS 2
    rclpy.init(args=args)

    # Create controller
    controller = SimpleJointController(
        amplitude=cmd_args.amplitude,
        frequency=cmd_args.frequency,
        control_rate=cmd_args.rate,
    )

    try:
        print("\n" + "=" * 70)
        print("SimpleJointController is running")
        print("Press Ctrl+C to stop")
        print("=" * 70 + "\n")

        # Spin (keep node running, process callbacks)
        rclpy.spin(controller)

    except KeyboardInterrupt:
        print("\n⏸️  Interrupted by user")

    finally:
        # Shutdown
        controller.shutdown()
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    exit(main())
