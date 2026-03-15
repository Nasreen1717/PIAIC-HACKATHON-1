# Chapter 1: ROS 2 Architecture - Nodes and Topics

## Learning Objectives

By the end of this chapter, you will:

- ✅ Understand what ROS 2 is and why it's used in robotics
- ✅ Grasp the concept of nodes and how they communicate
- ✅ Master the publish-subscribe (pub/sub) communication pattern
- ✅ Write your first ROS 2 publisher and subscriber nodes in Python
- ✅ Use ROS 2 CLI tools to inspect and debug a running system
- ✅ Understand message types and QoS settings

**Estimated time**: 8-10 hours
**Difficulty**: Beginner
**Prerequisites**: Chapter 0 (Setup), Python 3.10+, basic Linux terminal knowledge

---

## 1. What is ROS 2?

### History and Evolution

ROS (Robot Operating System) was first released in 2007 as a flexible framework for robot software development. ROS 2, released in 2017, is a complete redesign addressing limitations of ROS 1, most notably:

- **ROS 1 limitations**: Central master node (single point of failure), not suitable for real-time systems, security concerns
- **ROS 2 improvements**: Decentralized architecture using DDS middleware, real-time capable, built-in security

ROS 2 is currently at **Humble** version (Humble Hawksbill), an LTS (Long-Term Support) release supported until 2027.

**Citation**: Open Robotics, "ROS 2 Documentation," [Online]. Available: https://docs.ros.org/en/humble/. [Accessed: Jan. 22, 2026].

### Why Use ROS 2?

Consider a robot system:
- **Perception**: Camera streams, LiDAR scans, IMU data
- **Planning**: Motion planning, path optimization algorithms
- **Control**: Motor controllers, safety monitors, joint controllers
- **Integration**: Bringing all above together seamlessly

Without ROS 2, you'd need:
- Custom networking code (sockets, serialization)
- Error handling for dropped connections
- Message routing and filtering logic
- Debugging tools for each component

ROS 2 provides all this as infrastructure, letting you focus on robot behavior.

### Use Cases

- **Autonomous vehicles**: Communication between perception, planning, and control modules
- **Humanoid robots**: Coordination between multiple joint controllers
- **Manipulator arms**: Real-time control of multi-DOF systems
- **Mobile robots**: Navigation stack, SLAM, collision avoidance
- **Research**: Rapid prototyping of new control algorithms

---

## 2. Nodes: The Computational Units

### What is a Node?

A **node** is a ROS 2 process that performs a specific function and communicates with other nodes via pub/sub, services, or actions.

**Key characteristics**:
- Runs in its own process (typically)
- Has a unique name (e.g., `/camera_driver`)
- Can publish to topics, subscribe to topics, provide services, call services
- Lifecycle: creation → spinning (processing) → shutdown

### Node Examples

In a robot perception pipeline:

```
┌─────────────────┐
│  camera_driver  │  ← Node 1: publishes `/camera/image` topic
└────────┬────────┘
         │ /camera/image
         ▼
┌─────────────────┐
│ image_processor │  ← Node 2: subscribes to `/camera/image`, publishes `/processed_image`
└────────┬────────┘
         │ /processed_image
         ▼
┌─────────────────┐
│  object_detector│  ← Node 3: subscribes to `/processed_image`, publishes `/detections`
└─────────────────┘
```

Each node is independent; if one crashes, others continue running.

### Creating a Node in Python

Using rclpy (ROS 2 Python client library):

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node_name')
        self.get_logger().info('Node created!')

def main():
    rclpy.init()
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 3. Topics: Asynchronous Communication

### What is a Topic?

A **topic** is a named communication channel for one-way message flow:
- **Many-to-many**: Multiple publishers can write; multiple subscribers can read
- **Asynchronous**: Publishers don't wait for subscribers to process
- **Type-safe**: Each topic has a specific message type (e.g., `std_msgs/String`)
- **Decoupled**: Publishers and subscribers don't know about each other

### Publisher-Subscriber Pattern

```
Publisher 1 ──┐
Publisher 2 ──┼→ /sensor_data (String messages) →─┬→ Subscriber 1
Publisher 3 ──┘                                  └→ Subscriber 2
```

**Advantages**:
- Loose coupling: components don't need to know each other's details
- Scalability: add more publishers/subscribers without changing code
- Fault tolerance: if one subscriber crashes, others continue

### Topic Naming Convention

Topic names follow hierarchical conventions:

```
/robot_namespace/component/data_type
/robot/arm/joint_state
/robot/camera/rgb_image
/robot/base/odometry
```

Leading `/` means absolute name; relative names depend on node namespace.

### Running and Inspecting Topics

After you have a ROS 2 system running:

```bash
# List all active topics
ros2 topic list

# Show topic info (message type, number of publishers/subscribers)
ros2 topic info /robot/arm/joint_state

# Subscribe and view messages in real-time
ros2 topic echo /robot/arm/joint_state

# Monitor message rate and bandwidth
ros2 topic hz /robot/arm/joint_state
ros2 topic bw /robot/arm/joint_state
```

---

## 4. Publishers and Subscribers

### Publishers

A publisher sends messages to a topic:

```python
from std_msgs.msg import String

# Create publisher
publisher = node.create_publisher(String, '/my_topic', queue_size=10)

# Publish message
msg = String()
msg.data = 'Hello ROS 2'
publisher.publish(msg)
```

**Parameters**:
- **Message type**: What data structure to publish (`String`, `Int32`, etc.)
- **Topic name**: Where to publish (`/my_topic`)
- **Queue size**: How many messages to buffer if subscribers lag

### Subscribers

A subscriber listens to a topic and processes messages via a callback:

```python
def topic_callback(msg):
    print(f'Received: {msg.data}')

# Create subscriber
subscriber = node.create_subscription(
    String,
    '/my_topic',
    topic_callback,
    queue_size=10
)
```

**How it works**:
1. Node spins (waits for events)
2. When message arrives on `/my_topic`, callback function is called
3. Callback processes the message

### Message Types

ROS 2 has standard message types in packages:

- **std_msgs**: Basic types (`String`, `Int32`, `Float64`, `Bool`)
- **geometry_msgs**: Spatial data (`Twist`, `Pose`, `Vector3`)
- **sensor_msgs**: Sensor data (`Image`, `LaserScan`, `PointCloud2`)
- **nav_msgs**: Navigation (`Odometry`, `Path`)

Example: A velocity command uses `geometry_msgs/Twist`:

```python
from geometry_msgs.msg import Twist

cmd = Twist()
cmd.linear.x = 0.5      # Move forward 0.5 m/s
cmd.angular.z = 0.1     # Rotate 0.1 rad/s
publisher.publish(cmd)
```

### Quality of Service (QoS)

QoS policies control message delivery:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

# Reliable delivery (guaranteed, but slower)
qos_reliable = QoSProfile(reliability=ReliabilityPolicy.RELIABLE)

# Best-effort delivery (fast, may lose messages)
qos_best_effort = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT)

# Create publisher with QoS
publisher = node.create_publisher(String, '/my_topic', qos_profile=qos_reliable)
```

---

## 5. Running and Visualizing ROS 2 Systems

### Creating a Launch

Multiple nodes often start together via a **launch file**:

```xml
<!-- minimal_launch.xml -->
<launch>
  <node pkg="my_package" exec="publisher_node"/>
  <node pkg="my_package" exec="subscriber_node"/>
</launch>
```

Run with:
```bash
ros2 launch my_package minimal_launch.xml
```

### Visualizing the Graph

See all nodes and topics:

```bash
ros2 run rqt_graph rqt_graph
```

This launches a GUI showing:
- All nodes as boxes
- All topics as labeled edges
- Direction of communication (arrows)

### Debugging with CLI Tools

```bash
# Check node details
ros2 node info /my_node

# List all topics with types
ros2 topic list --full

# Check message rate on a topic
ros2 topic hz /sensor_topic

# Get a single message and exit
ros2 topic echo /sensor_topic --once
```

---

## 6. Complete Example: Hello World Publisher-Subscriber

### Publisher Node (1-hello-world-pub.py)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PublisherNode(Node):
    def __init__(self):
        super().__init__('publisher_node')
        self.publisher_ = self.create_publisher(String, 'hello_world_topic', 10)

        # Publish every 1 second
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World #{self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = PublisherNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Subscriber Node (1-hello-world-sub.py)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubscriberNode(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        self.subscription = self.create_subscription(
            String,
            'hello_world_topic',
            self.topic_callback,
            10)
        self.subscription  # Prevent unused variable warning

    def topic_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = SubscriberNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Running the Example

**Terminal 1 - Publisher:**
```bash
source /opt/ros/humble/setup.bash
python3 examples/1-hello-world-pub.py
```

**Terminal 2 - Subscriber:**
```bash
source /opt/ros/humble/setup.bash
python3 examples/1-hello-world-sub.py
```

**Terminal 3 - Monitor (optional):**
```bash
source /opt/ros/humble/setup.bash
ros2 topic echo hello_world_topic
```

Output in Terminal 2:
```
[INFO] [subscriber_node]: Received: Hello World #0
[INFO] [subscriber_node]: Received: Hello World #1
[INFO] [subscriber_node]: Received: Hello World #2
```

---

## Summary

| Concept | Definition | Use When |
|---------|-----------|----------|
| **Node** | ROS 2 process that performs computation | Every component in your system |
| **Topic** | Named communication channel | Broadcasting sensor data, commands |
| **Publisher** | Sends messages to topic | Sensor outputs, command generation |
| **Subscriber** | Listens to topic and processes via callback | Receiving and acting on data |
| **Message** | Typed data structure (String, Int32, etc.) | Specifying what data is communicated |
| **QoS** | Reliability, durability, latency settings | Tuning communication behavior |

---

## Key Takeaways

1. **ROS 2 is a middleware**: It handles networking, type safety, message routing
2. **Nodes are independent processes**: Loose coupling, scalability, fault tolerance
3. **Pub/Sub is asynchronous**: Publishers don't wait; subscribers react via callbacks
4. **CLI tools are powerful**: Use `ros2 topic`, `ros2 node`, `rqt_graph` for debugging
5. **Message types matter**: Standard types exist for common data; custom types can be defined later

---

## Next Steps

- Run the Hello World example yourself
- Modify the example to publish different messages
- Try multiple subscribers on one topic
- Use `ros2 topic echo` to monitor communication
- Proceed to Exercise 1.1: Create a Publisher

---

## Glossary References

- **Node**: See [Glossary: Node](./glossary.md#node)
- **Topic**: See [Glossary: Topic](./glossary.md#topic)
- **Publisher**: See [Glossary: Publisher](./glossary.md#publisher)
- **Subscriber**: See [Glossary: Subscriber](./glossary.md#subscriber)
- **Message**: See [Glossary: Message](./glossary.md#message)
- **QoS**: See [Glossary: QoS](./glossary.md#qos-quality-of-service)

---

**Citation**: Open Robotics. "ROS 2 Concepts." *ROS 2 Documentation*, Jan. 2026. [Online]. Available: https://docs.ros.org/en/humble/Concepts.html. [Accessed: Jan. 22, 2026].

---

*Chapter 1: ROS 2 Architecture* | Version 1.0.0 | Module 1 - ROS 2 Fundamentals
