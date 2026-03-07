#!/usr/bin/env python3
"""
ROS 2 Action Client Example
Calls the Fibonacci action and monitors feedback
Usage:
    python3 2-action-client.py
Note: Must have 2-action-server.py running in another terminal
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):
    """ROS 2 action client for Fibonacci sequence generation."""

    def __init__(self):
        super().__init__('fibonacci_client')

        # Create action client
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

        # Wait for action server to be available
        while not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info('Action server not available, waiting...')

        self.get_logger().info('Action server connected')

    def send_goal(self, order):
        """
        Send a fibonacci goal to the action server.

        Args:
            order: Fibonacci order (number of sequence elements to generate)
        """
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Sending goal: order={order}')

        # Send goal and get handle
        # Register callbacks for feedback and result
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Wait for goal acceptance, then wait for result
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        Handle goal acceptance response.

        Args:
            future: Future object with goal_handle
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected by server')
            return

        self.get_logger().info('Goal accepted by server')

        # Request result from goal handle
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """
        Handle feedback from action server.

        Args:
            feedback_msg: Feedback message with partial_sequence
        """
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Received feedback: {feedback.partial_sequence}'
        )

    def get_result_callback(self, future):
        """
        Handle final result from action server.

        Args:
            future: Future object with result
        """
        result = future.result().result
        self.get_logger().info(f'Final sequence: {result.sequence}')
        print(f'Fibonacci sequence: {result.sequence}')


def main(args=None):
    rclpy.init(args=args)

    client = FibonacciActionClient()

    # Send a fibonacci goal to generate the first 10 numbers
    client.send_goal(10)

    # Spin to process callbacks (feedback and result)
    try:
        rclpy.spin(client)
    except KeyboardInterrupt:
        pass
    finally:
        client.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
