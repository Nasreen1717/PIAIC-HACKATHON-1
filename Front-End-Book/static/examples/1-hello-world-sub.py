#!/usr/bin/env python3
"""
Hello World Subscriber Example for ROS 2 Chapter 1.

This example demonstrates:
- Creating a ROS 2 node
- Creating a subscriber
- Processing messages via a callback function

Run with publisher:
    # Terminal 1:
    python3 examples/1-hello-world-pub.py

    # Terminal 2:
    python3 examples/1-hello-world-sub.py

Expected output in Terminal 2:
    [INFO] [subscriber_node]: Received: "Hello World #0"
    [INFO] [subscriber_node]: Received: "Hello World #1"
    ...
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloWorldSubscriber(Node):
    """ROS 2 node that subscribes to and prints 'Hello World' messages."""

    def __init__(self):
        """Initialize the subscriber node."""
        super().__init__('subscriber_node')

        # Create a subscription to 'hello_world_topic' with message type String
        # Queue size of 10 means buffer up to 10 messages
        # When a message arrives, listener_callback is called
        self.subscription = self.create_subscription(
            String,
            'hello_world_topic',
            self.listener_callback,
            queue_size=10
        )

        # Keep reference to prevent garbage collection
        self.subscription

        # Counter to track received messages
        self.message_count = 0

        self.get_logger().info('Subscriber node started. Listening on /hello_world_topic')

    def listener_callback(self, msg):
        """
        Called when a message is received on the subscribed topic.

        Args:
            msg (String): The received message
        """
        self.message_count += 1
        self.get_logger().info(f'[Message #{self.message_count}] Received: "{msg.data}"')


def main(args=None):
    """Main entry point for the subscriber node."""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the subscriber node
    subscriber_node = HelloWorldSubscriber()

    try:
        # Keep the node running and processing callbacks
        # When messages arrive, listener_callback is invoked automatically
        rclpy.spin(subscriber_node)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean shutdown
        subscriber_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
