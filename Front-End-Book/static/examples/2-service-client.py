#!/usr/bin/env python3
"""
ROS 2 Service Client Example
Calls the arithmetic service to add two integers
Usage:
    python3 2-service-client.py
Note: Must have 2-service-server.py running in another terminal
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class ArithmeticClient(Node):
    """ROS 2 service client for arithmetic operations."""

    def __init__(self):
        super().__init__('arithmetic_client')

        # Create service client
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for server to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        self.get_logger().info('Service server connected')

    def call_service(self, a, b):
        """
        Call the service with two integers.

        Args:
            a: First integer
            b: Second integer

        Returns:
            sum: Result of a + b, or None if service call failed
        """
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        self.get_logger().info(f'Calling service with a={a}, b={b}')

        # Blocking call - waits for response
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(
                f'Result: {a} + {b} = {response.sum}'
            )
            return response.sum
        else:
            self.get_logger().error('Service call failed')
            return None


def main(args=None):
    rclpy.init(args=args)

    client = ArithmeticClient()

    # Test the service with several calls
    test_cases = [(5, 3), (10, 20), (0, 0), (-5, 5)]

    for a, b in test_cases:
        result = client.call_service(a, b)
        if result is not None:
            print(f'{a} + {b} = {result}')
        print()

    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
