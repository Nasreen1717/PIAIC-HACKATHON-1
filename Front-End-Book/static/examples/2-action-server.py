#!/usr/bin/env python3
"""
ROS 2 Action Server Example
Provides a Fibonacci number generator action with feedback
Usage:
    python3 2-action-server.py
Then in another terminal:
    ros2 action send_goal /fibonacci example_interfaces/Fibonacci "{order: 10}"
"""

import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    """ROS 2 action server for Fibonacci sequence generation."""

    def __init__(self):
        super().__init__('fibonacci_server')

        # Create action server with multi-threaded executor support
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )
        self.get_logger().info('Fibonacci action server ready')
        self.get_logger().info('Action: /fibonacci')
        self.get_logger().info('Type: example_interfaces/Fibonacci')

    def execute_callback(self, goal_handle):
        """
        Execute the fibonacci action.

        Args:
            goal_handle: Action goal handle with request containing 'order'

        Returns:
            result: Fibonacci.Result with complete sequence
        """
        self.get_logger().info(
            f'Executing fibonacci with order: {goal_handle.request.order}'
        )

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        # Generate fibonacci sequence
        for i in range(2, goal_handle.request.order):
            # Check if cancellation was requested
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Fibonacci action was canceled')
                return Fibonacci.Result()

            # Calculate next fibonacci number
            next_fib = (
                feedback_msg.partial_sequence[i - 1] +
                feedback_msg.partial_sequence[i - 2]
            )
            feedback_msg.partial_sequence.append(next_fib)

            # Publish feedback
            self.get_logger().info(
                f'Publishing feedback: {feedback_msg.partial_sequence}'
            )
            goal_handle.publish_feedback(feedback_msg)

            # Simulate processing time (0.1 seconds per number)
            time.sleep(0.1)

        # Action completed successfully
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence
        goal_handle.succeed()

        self.get_logger().info(f'Fibonacci complete: {result.sequence}')
        return result


def main(args=None):
    rclpy.init(args=args)

    server = FibonacciActionServer()

    # Use multi-threaded executor for action servers
    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(server, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
