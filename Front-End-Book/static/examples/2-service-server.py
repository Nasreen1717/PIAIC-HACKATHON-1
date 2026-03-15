#!/usr/bin/env python3
"""
ROS 2 Service Server Example
Provides an arithmetic service that adds two integers
Usage:
    python3 2-service-server.py
Then in another terminal:
    ros2 service call /add_two_ints example_interfaces/AddTwoInts "{a: 5, b: 3}"
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class ArithmeticServer(Node):
    """ROS 2 service server for arithmetic operations."""

    def __init__(self):
        super().__init__('arithmetic_server')

        # Create service server
        self.service = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )
        self.get_logger().info('Arithmetic service server ready')
        self.get_logger().info('Service: /add_two_ints')
        self.get_logger().info('Type: example_interfaces/AddTwoInts')

    def add_two_ints_callback(self, request, response):
        """
        Process incoming service request.

        Args:
            request: AddTwoInts.Request with fields 'a' and 'b'
            response: AddTwoInts.Response to populate with result

        Returns:
            response: Populated with sum of a and b
        """
        response.sum = request.a + request.b

        self.get_logger().info(
            f'Request: {request.a} + {request.b} = {response.sum}'
        )

        return response


def main(args=None):
    rclpy.init(args=args)

    server = ArithmeticServer()

    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        pass
    finally:
        server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
