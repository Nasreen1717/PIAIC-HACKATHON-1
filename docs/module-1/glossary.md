# ROS 2 Glossary

A comprehensive reference for ROS 2 terminology used throughout Module 1. Each term includes a definition, context, and practical example.

---

## Action

**Definition**: A ROS 2 communication pattern for long-running tasks that provides goal, feedback, and result.

**Use when**: You need a task that takes time, provides periodic updates, and can be preempted.

**Example**: A robot arm moving to a joint position is an action—you send a goal (target position), receive periodic feedback (current position), and get a result (success/failure).

```python
# Sending an action goal
goal_msg = MoveJoint.Goal()
goal_msg.target_position = 1.57
future = action_client.send_goal_async(goal_msg)
```

---

## Callback

**Definition**: A Python function that is called when an event occurs (e.g., a message is received).

**Use when**: You want to react to messages or events asynchronously.

**Example**: Define a callback that runs whenever a subscriber receives a message.

```python
def message_callback(msg):
    print(f"Received: {msg.data}")

subscriber = node.create_subscription(
    String,
    '/my_topic',
    message_callback,
    10
)
```

---

## Client (Service Client)

**Definition**: A ROS 2 node that sends a request to a service and waits for a response.

**Use when**: You need synchronous, request-reply communication.

**Example**: A client calls a service to compute the sum of two numbers.

```python
future = client.call_async(AddTwoInts.Request(a=3, b=4))
response = future.result()
print(f"Sum: {response.sum}")
```

---

## Colcon

**Definition**: Build system for ROS 2 packages. Stands for "collective construction."

**Use when**: Building ROS 2 packages from source.

**Example**: Build all packages in your workspace.

```bash
colcon build
```

---

## DDS (Data Distribution Service)

**Definition**: Middleware protocol used by ROS 2 for communication between nodes.

**Context**: Unlike ROS 1 which used a master node, ROS 2 uses DDS for decentralized communication.

**Note**: You typically don't interact with DDS directly—ROS 2 abstracts it away.

---

## Domain ID

**Definition**: A ROS 2 network partition number (0-232). Nodes with different domain IDs don't see each other.

**Use when**: Running multiple ROS 2 networks on the same physical network.

**Example**: Set domain ID via environment variable.

```bash
export ROS_DOMAIN_ID=1
ros2 run my_package my_node
```

---

## Executor

**Definition**: ROS 2 component that manages callbacks and spinning logic.

**Context**: Executors decide which callbacks to invoke and in what order.

**Note**: In simple scripts, you typically don't interact with executors directly.

---

## Graph

**Definition**: Visualization of ROS 2 system showing all nodes, topics, and connections.

**Use when**: Debugging complex systems or understanding communication patterns.

**Example**: View the computational graph.

```bash
rqt_graph
```

---

## Joint (URDF)

**Definition**: A connection between two rigid bodies (links) in a robot, allowing relative motion.

**Types**:
- **revolute**: Rotational movement around an axis (like a hinge)
- **prismatic**: Linear movement along an axis (like a piston)
- **fixed**: No movement (rigid connection)
- **floating**: 6 DOF (used for free-floating base)

**Example**: A shoulder joint connecting the torso to an arm (revolute, 3 DOF).

---

## Launch File

**Definition**: XML or Python file that starts multiple ROS 2 nodes with specific configurations.

**Use when**: Running complex systems with many nodes, parameters, and topic remappings.

**Example**: Launch a robot perception stack.

```bash
ros2 launch my_package robot_launch.xml
```

---

## Link (URDF)

**Definition**: A rigid body in a robot with associated geometry, inertia, and collision properties.

**Components**:
- **visual**: What the robot looks like
- **collision**: What boundaries to use for collision checking
- **inertial**: Mass and moment of inertia

**Example**: A robot has links for torso, arms, and legs.

---

## Message

**Definition**: ROS 2 data structure sent between nodes. Defined in `.msg` files.

**Types**: std_msgs (String, Int32, Float64, etc.), geometry_msgs (Twist, Pose, etc.), sensor_msgs (Image, PointCloud2, etc.)

**Example**: Publish a string message.

```python
msg = String()
msg.data = "Hello ROS 2"
publisher.publish(msg)
```

---

## Middleware (rmw)

**Definition**: ROS 2 middleware abstraction layer enabling different DDS implementations (FastRTPS, Cyclone DDS, etc.).

**Context**: You don't typically change this, but it's important for deployment flexibility.

---

## Node

**Definition**: A ROS 2 process that performs computation and communicates with other nodes.

**Characteristics**:
- Executes continuously in a loop
- Has a unique name
- Can have publishers, subscribers, services, actions
- Runs in its own process (typically)

**Example**: A robot arm control node publishes joint angles and subscribes to goal positions.

---

## Parameters

**Definition**: Configuration values passed to ROS 2 nodes at runtime.

**Use when**: You want to change behavior without recompiling code.

**Example**: Set a robot's speed parameter.

```bash
ros2 run my_package my_node --ros-args -p max_speed:=5.0
```

---

## Publisher

**Definition**: ROS 2 entity that sends messages to a topic.

**Characteristics**:
- Sends asynchronously (doesn't wait for receivers)
- Can have many subscribers listening
- Specified with a message type and topic name

**Example**: A sensor publishes readings to a topic.

```python
publisher = node.create_publisher(Float64, '/sensor_reading', 10)
publisher.publish(Float64(data=42.5))
```

---

## QoS (Quality of Service)

**Definition**: Policy controlling message delivery reliability, latency, and bandwidth.

**Common profiles**:
- **RELIABLE**: Guarantee all messages arrive (slower, more overhead)
- **BEST_EFFORT**: Deliver if possible (faster, may lose messages)

**Example**: Set QoS for a publisher.

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy
qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE)
publisher = node.create_publisher(String, '/my_topic', qos)
```

---

## rclpy

**Definition**: ROS 2 Python client library for writing ROS 2 nodes in Python.

**Install**: `pip install rclpy`

**Usage**: Import and use to create nodes, publishers, subscribers, etc.

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
```

---

## Remapping

**Definition**: Runtime substitution of topic/service/action names without code changes.

**Use when**: Same code runs on different robots with different topic names.

**Example**: Remap a topic name at launch time.

```bash
ros2 run my_package my_node --ros-args --remap /original_topic:=/new_topic
```

---

## ROS 2 (Robot Operating System 2)

**Definition**: Flexible middleware for building distributed robot software systems.

**Key features**:
- Decentralized (no master node)
- Type-safe
- DDS-based communication
- Multi-platform (Ubuntu, Windows, macOS)
- Large ecosystem of packages

**Current version**: Humble (LTS, supported until 2027)

---

## RViz2 (ROS Visualization)

**Definition**: 3D visualization tool for ROS 2 systems, sensors, and robot models.

**Use when**: Debugging perception systems, visualizing robot trajectories, or viewing sensor data.

**Example**: View a robot URDF model.

```bash
rviz2
```

Then load a URDF file using the RViz2 GUI.

---

## Service

**Definition**: ROS 2 communication pattern for synchronous, request-reply interactions.

**Characteristics**:
- Client sends request, waits for response (blocking)
- Server receives request and sends response
- Suitable for queries, computations, state changes

**Example**: A client requests the current time from a service.

```python
# Client side
response = client.call(GetTime.Request())

# Server side
def handle_request(request):
    return GetTime.Response(current_time=time.time())
```

---

## Setup Script

**Definition**: Shell script that configures ROS 2 environment variables (created by colcon).

**Location**: `install/setup.bash` in a colcon workspace

**Use**: Source before running nodes to configure paths and environment.

```bash
source install/setup.bash
```

---

## Spin

**Definition**: ROS 2 executor loop that processes callbacks and keeps the node running.

**Function**: `rclpy.spin(node)` blocks and processes incoming messages/events.

**Example**: Keep node running indefinitely.

```python
rclpy.spin(node)
```

---

## Subscriber

**Definition**: ROS 2 entity that listens to messages on a topic.

**Characteristics**:
- Receives messages asynchronously via callback
- Multiple subscribers can listen to same topic
- Specified with message type and topic name

**Example**: A robot controller subscribes to goal positions.

```python
def goal_callback(msg):
    print(f"Goal: {msg.position}")

subscriber = node.create_subscription(GoalMsg, '/goal', goal_callback, 10)
```

---

## Topic

**Definition**: Named communication channel where publishers send messages and subscribers receive them.

**Characteristics**:
- Many-to-many: Multiple publishers can write, multiple subscribers can read
- Asynchronous: Publishers don't wait for subscribers
- Type-safe: Specific message type per topic

**Example**: Sensor publishes `/temperature` topic; controller subscribes to it.

```bash
ros2 topic list           # List all topics
ros2 topic echo /topic    # View messages on a topic
ros2 topic info /topic    # Info about a topic
```

---

## Transform (TF)

**Definition**: ROS 2 library for managing coordinate frame relationships (position and orientation).

**Use when**: You need to know the relationship between frames (e.g., robot base to end effector).

**Note**: Advanced topic; not covered in Module 1.

---

## URDF (Unified Robot Description Format)

**Definition**: XML format for describing robot structure (links, joints, geometry, sensors).

**Use when**: Defining robot models for visualization, physics, and planning.

**File extension**: `.urdf` or `.urdf.xacro` (with macros)

**Example**: Simple two-link robot.

```xml
<robot name="simple_robot">
  <link name="base"/>
  <link name="arm"/>
  <joint name="shoulder" type="revolute">
    <parent link="base"/>
    <child link="arm"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>
```

---

## Xacro

**Definition**: XML macro language for URDF—adds variables, loops, and includes for code reuse.

**Use when**: URDF gets repetitive (multiple identical links/joints).

**Note**: Xacro files must be processed before use; ROS 2 provides tools for this.

**Example**: URDF with xacro macros.

```xml
<xacro:macro name="leg" params="name">
  <link name="${name}_link"/>
  <joint name="${name}_joint" type="revolute">
    <!-- ... -->
  </joint>
</xacro:macro>

<xacro:leg name="left"/>
<xacro:leg name="right"/>
```

---

## Logging

**Definition**: ROS 2 logging system for debug messages, warnings, and errors.

**Levels**: DEBUG, INFO, WARN, ERROR, FATAL

**Example**: Log a message in a node.

```python
self.get_logger().info(f"Message: {msg.data}")
self.get_logger().error("An error occurred!")
```

---

## Frame / Coordinate Frame

**Definition**: A coordinate system with origin, axes, and orientation.

**Context**: Robots typically have many frames (base, links, sensors).

**Common frames**: `base_link` (root), `world` (global reference)

---

## Inertia (URDF)

**Definition**: Mass and moment of inertia properties of a robot link.

**Use when**: Creating physics-accurate models for simulation or dynamics calculations.

**Note**: Required for simulation; often simplified for visualization-only models.

---

## QoS Profile

**Definition**: Configuration specifying DDS middleware behavior (reliability, durability, latency, etc.).

**Common settings**: Reliability policy, history policy, depth

---

## Message Type / Msg Class

**Definition**: Python class representing a ROS 2 message structure.

**Examples**: `std_msgs.String`, `geometry_msgs.Twist`, `sensor_msgs.Image`

**Location**: Defined in `.msg` files, generated as Python classes

---

## Package

**Definition**: Directory containing ROS 2 code, configuration, and metadata (package.xml).

**Structure**: A package contains nodes, launch files, messages, and tests.

**Command**: List installed packages.

```bash
ros2 pkg list
```

---

## Gazebo

**Definition**: Physics simulation engine often used with ROS 2 (not covered in Module 1).

**Note**: Part of ROS ecosystem but belongs to Module 2+.

---

## Docker

**Definition**: Containerization technology for ensuring reproducible ROS 2 environments.

**Note**: Optional; helpful for deployment but not required for learning.

---

---

## Index: Glossary Terms by Category

### Communication Patterns
- Topic
- Publisher
- Subscriber
- Message
- Service
- Client (Service Client)
- Action
- QoS (Quality of Service)
- Callback
- Remapping

### ROS 2 Core
- Node
- rclpy
- ROS 2 (Robot Operating System 2)
- Spin
- Parameters
- Logging

### Build & Deployment
- Colcon
- Package
- Setup Script
- Launch File
- Domain ID

### Networking
- DDS (Data Distribution Service)
- Middleware (rmw)
- Executor

### Robotics & Visualization
- URDF (Unified Robot Description Format)
- Xacro
- Link (URDF)
- Joint (URDF)
- Frame / Coordinate Frame
- Inertia (URDF)
- Transform (TF)
- RViz2 (ROS Visualization)

### Advanced Topics (Module 2+)
- Gazebo
- Docker

---

**Version**: 1.0.0 | **Last updated**: 2026-01-22 | **Module**: 1 - ROS 2 Fundamentals
