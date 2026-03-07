#!/usr/bin/env python3
"""
ROS 2 Joint Controller Example
Implements a proportional (P) controller for joint angles
Subscribes to /joint_states and publishes desired commands to /joint_commands
Usage:
    python3 2-joint-controller.py
Note: This is a standalone example. In a real system, you would have:
    - Joint state publisher (from robot/simulator)
    - Actuator node that subscribes to commands
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState


class JointController(Node):
    """
    Simple joint controller using P (proportional) control.

    Implements a feedback control loop:
    - Reads desired joint state from /joint_states topic
    - Computes error between desired and actual position
    - Applies proportional gain to produce control command
    - Publishes command to /joint_commands topic
    """

    def __init__(self):
        super().__init__('joint_controller')

        # Subscribe to joint state (actual position)
        self.state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.state_callback,
            10
        )

        # Publish desired commands
        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        # Control loop timer (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)

        # Store current state
        self.current_state = None

        # Controller parameters
        self.goal_position = [0.785, 0.785, 0.785]  # 45 degrees for all joints
        self.kp = 0.5  # Proportional gain
        self.max_command = 1.0  # Clamp commands to [-1.0, 1.0]

        self.get_logger().info('Joint controller initialized')
        self.get_logger().info(f'Goal position: {self.goal_position}')
        self.get_logger().info(f'Proportional gain: {self.kp}')

    def state_callback(self, msg):
        """
        Store current joint state from sensor.

        Args:
            msg: JointState message containing positions, velocities, efforts
        """
        self.current_state = msg

    def control_loop(self):
        """
        Main control algorithm running at regular intervals.

        Implements:
        1. Error calculation: error = goal - actual
        2. Control law: command = kp * error
        3. Command saturation: clamp to [-max, +max]
        4. Publish to actuators
        """
        if self.current_state is None:
            self.get_logger().warn('No joint state received yet')
            return

        # Extract current positions
        current_positions = list(self.current_state.position)

        # Ensure we have correct number of joints
        if len(current_positions) != len(self.goal_position):
            self.get_logger().error(
                f'Joint count mismatch: got {len(current_positions)}, '
                f'expected {len(self.goal_position)}'
            )
            return

        # Calculate position error for each joint
        errors = [
            self.goal_position[i] - current_positions[i]
            for i in range(len(current_positions))
        ]

        # Apply P-controller: command = kp * error
        raw_commands = [self.kp * error for error in errors]

        # Saturate commands to [-max_command, +max_command]
        commands = [
            max(-self.max_command, min(self.max_command, cmd))
            for cmd in raw_commands
        ]

        # Publish commands
        cmd_msg = Float64MultiArray()
        cmd_msg.data = commands
        self.cmd_pub.publish(cmd_msg)

        # Log at reduced frequency (every 10th iteration = 1 second)
        if self.get_clock().now().nanoseconds % 10 == 0:
            self.get_logger().info(
                f'Positions: {[round(p, 3) for p in current_positions]}, '
                f'Errors: {[round(e, 3) for e in errors]}, '
                f'Commands: {[round(c, 3) for c in commands]}'
            )


def main(args=None):
    rclpy.init(args=args)

    controller = JointController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
