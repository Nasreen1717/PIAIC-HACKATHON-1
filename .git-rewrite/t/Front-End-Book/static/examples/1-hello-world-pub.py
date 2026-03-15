#!/usr/bin/env python3
"""
Hello World Publisher Example for ROS 2 Chapter 1.

This example demonstrates:
- Creating a ROS 2 node
- Creating a publisher
- Publishing messages periodically via a timer

Run:
    python3 examples/1-hello-world-pub.py

Expected output:
    [INFO] [publisher_node]: Publishing: Hello World #0
    [INFO] [publisher_node]: Publishing: Hello World #1
    ...
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloWorldPublisher(Node):
    """ROS 2 node that publishes 'Hello World' messages to a topic."""

    def __init__(self):
        """Initialize the publisher node."""
        super().__init__('publisher_node')

        # Create a publisher that publishes String messages to 'hello_world_topic'
        # Queue size of 10 means buffer up to 10 messages if subscribers lag
        self.publisher_ = self.create_publisher(
            String,
            'hello_world_topic',
            queue_size=10
        )

        # Create a timer that calls timer_callback every 1 second
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter to show message sequence
        self.counter = 0

        self.get_logger().info('Publisher node started. Publishing to /hello_world_topic')

    def timer_callback(self):
        """Called periodically by the timer to publish messages."""
        msg = String()
        msg.data = f'Hello World #{self.counter}'

        # Publish the message
        self.publisher_.publish(msg)

        # Log the publication
        self.get_logger().info(f'Publishing: "{msg.data}"')

        self.counter += 1


def main(args=None):
    """Main entry point for the publisher node."""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the publisher node
    publisher_node = HelloWorldPublisher()

    try:
        # Keep the node running and processing callbacks
        rclpy.spin(publisher_node)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean shutdown
        publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
