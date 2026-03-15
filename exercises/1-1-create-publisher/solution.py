#!/usr/bin/env python3
"""
Solution for Exercise 1.1: Create a Publisher Node.

This solution demonstrates:
- Creating a ROS 2 node
- Creating a publisher for Int32 messages
- Publishing with a timer callback at 1 Hz
- Proper error handling and cleanup
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterPublisher(Node):
    """ROS 2 node that publishes incrementing integer counters."""

    def __init__(self):
        """Initialize the counter publisher node."""
        super().__init__('counter_publisher')

        # Create a publisher for Int32 messages on 'counter_topic'
        # Queue size of 10 allows buffering up to 10 messages
        self.publisher = self.create_publisher(Int32, 'counter_topic', queue_size=10)

        # Create a timer that fires every 1 second
        # When timer fires, timer_callback() is called
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter variable - incremented each publishing
        self.counter = 0

        self.get_logger().info('Counter publisher started. Publishing to /counter_topic at 1 Hz')

    def timer_callback(self):
        """
        Called by timer every 1 second.

        Creates an Int32 message with current counter value and publishes it.
        """
        # Create an Int32 message
        msg = Int32()
        msg.data = self.counter

        # Publish the message
        self.publisher.publish(msg)

        # Log the publication
        self.get_logger().info(f'Published counter: {self.counter}')

        # Increment counter for next publication
        self.counter += 1


def main(args=None):
    """Main entry point for the counter publisher node."""
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the publisher node
    publisher_node = CounterPublisher()

    try:
        # Spin the node (keep it running and processing callbacks)
        rclpy.spin(publisher_node)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print('\nShutting down...')
    finally:
        # Clean shutdown
        publisher_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
