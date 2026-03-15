#!/bin/bash
# Topic Introspection Script for ROS 2 Chapter 1
#
# This script demonstrates ROS 2 CLI tools for inspecting topics.
# Run the hello world pub/sub examples first, then run this script.
#
# Usage:
#   bash examples/1-topic-introspection.sh

set -e

echo "======================================"
echo "ROS 2 Topic Introspection Demonstration"
echo "======================================"
echo ""

# Ensure ROS 2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "⚠️  ROS 2 environment not set. Sourcing /opt/ros/humble/setup.bash..."
    source /opt/ros/humble/setup.bash
fi

echo "1. Listing all active topics:"
echo "   Command: ros2 topic list"
echo ""
ros2 topic list
echo ""

echo "======================================"
echo ""

echo "2. Listing all topics with message types:"
echo "   Command: ros2 topic list --full"
echo ""
ros2 topic list --full
echo ""

echo "======================================"
echo ""

echo "3. Getting information about 'hello_world_topic':"
echo "   Command: ros2 topic info /hello_world_topic"
echo ""
if ros2 topic info /hello_world_topic 2>/dev/null; then
    echo ""
    echo "======================================"
    echo ""

    echo "4. Viewing messages on 'hello_world_topic' (first 5 messages):"
    echo "   Command: ros2 topic echo /hello_world_topic"
    echo ""
    echo "   (Receiving for 5 seconds...)"
    timeout 5 ros2 topic echo /hello_world_topic || true
    echo ""

    echo "======================================"
    echo ""

    echo "5. Monitoring message rate:"
    echo "   Command: ros2 topic hz /hello_world_topic"
    echo ""
    echo "   (Measuring for 5 seconds...)"
    timeout 5 ros2 topic hz /hello_world_topic || true
    echo ""

    echo "======================================"
    echo ""

    echo "6. Monitoring bandwidth usage:"
    echo "   Command: ros2 topic bw /hello_world_topic"
    echo ""
    echo "   (Measuring for 5 seconds...)"
    timeout 5 ros2 topic bw /hello_world_topic || true
    echo ""

else
    echo "❌ Topic not found. Make sure publisher is running!"
    echo "   Run this first: python3 examples/1-hello-world-pub.py"
    exit 1
fi

echo "======================================"
echo "Introspection Complete"
echo "======================================"
echo ""
echo "Key Takeaways:"
echo "- Use 'ros2 topic list' to discover available topics"
echo "- Use 'ros2 topic info' to see publisher/subscriber count and message type"
echo "- Use 'ros2 topic echo' to view messages in real-time"
echo "- Use 'ros2 topic hz' to monitor message frequency"
echo "- Use 'ros2 topic bw' to check bandwidth consumption"
