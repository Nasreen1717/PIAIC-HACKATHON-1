# Chapter 2: Communication Patterns - Services, Actions, and Custom Messages

## Learning Objectives

By the end of this chapter, you will:

- ✅ Understand service-based synchronous request-reply communication
- ✅ Implement ROS 2 service servers and clients
- ✅ Understand action-based goal communication with feedback
- ✅ Implement ROS 2 action servers and clients
- ✅ Define and use custom message types with `.msg` files
- ✅ Write and use launch files with parameters
- ✅ Integrate AI/ML code with ROS 2 control systems
- ✅ Understand QoS policies and their practical impact

**Estimated time**: 12-14 hours
**Difficulty**: Intermediate
**Prerequisites**: Chapter 1 (Nodes and Topics), Python 3.10+, understanding of async/sync patterns

---

## 1. Topic Patterns Deep Dive

### When to Use Topics vs. Services vs. Actions

From Chapter 1, you learned that **topics** are asynchronous, one-way communication channels. Let's expand on topic usage patterns:

#### Pattern 1: Sensor Broadcasting

A sensor node publishes data continuously; multiple nodes may subscribe:

```python
# Single publisher, multiple subscribers
sensor_node → /camera/image → processor_1
           → /camera/image → processor_2
           → /camera/image → processor_3
```

**Example**: LiDAR publishes point clouds; both SLAM and collision avoidance nodes subscribe.

```python
publisher = node.create_publisher(PointCloud2, '/lidar/points', 10)
```

#### Pattern 2: Command Broadcasting

A controller publishes desired states; actuators subscribe and execute:

```python
# One controller publishes goals to multiple actuators
goal_publisher → /joint_goals → arm_controller
              → /joint_goals → leg_controller
              → /joint_goals → base_controller
```

#### Pattern 3: Feedback Loops with Topics

Multiple sensors feed back their state to a central controller:

```python
# Multiple sensors → Central controller → Actions
joint_1_state → /joint_states → controller → /joint_commands → actuators
joint_2_state → /joint_states → controller → /joint_commands → actuators
joint_3_state → /joint_states → controller → /joint_commands → actuators
```

### QoS Patterns for Different Scenarios

**Best-Effort Delivery** (fast, may lose messages):
```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

# Video streaming, sensor data with high frequency
qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT)
publisher = node.create_publisher(Image, '/camera/rgb', 10, qos_profile=qos)
```

**Reliable Delivery** (guaranteed but slower):
```python
# Critical commands, state information
qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE)
publisher = node.create_publisher(JointTrajectory, '/arm/trajectory', 10, qos_profile=qos)
```

**Citation**: Open Robotics, "ROS 2 QoS Policies," ROS 2 Documentation, [Online]. Available: https://docs.ros.org/en/humble/Concepts/About-ROS2-QoS.html. [Accessed: Jan. 22, 2026].

---

## 2. Services: Synchronous Request-Reply Communication

### What is a Service?

A **service** is a synchronous, request-reply communication pattern:
- **Client** sends a request and **waits** for a response
- **Server** receives request, processes it, sends back response
- **Blocking**: Client is blocked until response arrives
- **One-to-one**: One client calls one server (though multiple clients can call same server sequentially)

**When to use services**:
- Computations that need immediate results (e.g., "Is path collision-free?")
- Configuration queries (e.g., "Get current sensor settings")
- One-time operations (e.g., "Take a photo and return it")

### Service Definition

Services use `.srv` files (similar to message files):

```srv
# Example: AddTwoInts.srv (arithmetic service)
int64 a
int64 b
---
int64 sum
```

The `---` separator divides **request** (top) from **response** (bottom).

### Service Server Implementation

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ArithmeticServer(Node):
    def __init__(self):
        super().__init__('arithmetic_server')

        # Create service
        self.service = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )
        self.get_logger().info('Service server ready')

    def add_two_ints_callback(self, request, response):
        """Process incoming service request"""
        response.sum = request.a + request.b
        self.get_logger().info(f'Request: {request.a} + {request.b} = {response.sum}')
        return response

def main(args=None):
    rclpy.init(args=args)
    server = ArithmeticServer()
    rclpy.spin(server)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service Client Implementation

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ArithmeticClient(Node):
    def __init__(self):
        super().__init__('arithmetic_client')

        # Create client
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for server to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

    def call_service(self, a, b):
        """Call the service"""
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # Blocking call - waits for response
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(f'Result: {a} + {b} = {response.sum}')
            return response.sum
        else:
            self.get_logger().error('Service call failed')
            return None

def main(args=None):
    rclpy.init(args=args)
    client = ArithmeticClient()

    # Call service with 5 and 3
    result = client.call_service(5, 3)
    print(f'Result: {result}')

    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service vs. Topic: When to Choose

| Scenario | Topic | Service |
|----------|-------|---------|
| Stream sensor data | ✅ Use | ❌ No |
| Query current state | ❌ No | ✅ Use |
| One-time computation | ❌ No | ✅ Use |
| Multiple consumers | ✅ Use | ⚠️ Sequential only |
| Real-time loop control | ✅ Use | ❌ Too slow |
| Configuration change | ❌ No | ✅ Use |

---

## 3. Actions: Goal-Based Communication with Feedback

### What is an Action?

An **action** is for long-running tasks with intermediate feedback:
- **Client** sends a **goal** and monitors progress
- **Server** processes goal, sends periodic **feedback**, then returns **result**
- **Preemption**: Client can cancel mid-execution
- **Use when**: Task takes time and client needs updates (e.g., motion planning, navigation)

**Action components**:
1. **Goal**: What the client wants (e.g., "Move to position (1, 2, 3)")
2. **Feedback**: Periodic updates from server (e.g., "Currently at (0.5, 1, 1.5)")
3. **Result**: Final outcome when complete (e.g., "Success" or "Failure")

### Action Definition

Actions use `.action` files:

```action
# Example: Fibonacci.action
int32 order
---
sequence<int32> sequence
---
int32 partial_sequence
```

Three sections (separated by `---`):
- **Goal** (top): What client requests
- **Result** (middle): Final output
- **Feedback** (bottom): Updates during execution

### Action Server Implementation

```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import time

from example_interfaces.action import Fibonacci

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback
        )
        self.get_logger().info('Fibonacci action server ready')

    def execute_callback(self, goal_handle):
        """Execute the fibonacci action"""
        self.get_logger().info(f'Executing fibonacci with order: {goal_handle.request.order}')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        # Generate fibonacci sequence
        for i in range(2, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Fibonacci was canceled')
                return Fibonacci.Result()

            # Add next fibonacci number
            feedback_msg.partial_sequence.append(
                feedback_msg.partial_sequence[i-1] + feedback_msg.partial_sequence[i-2]
            )

            # Send feedback
            self.get_logger().info(f'Publishing feedback: {feedback_msg.partial_sequence}')
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(0.1)  # Simulate processing

        # Complete action
        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence
        goal_handle.succeed()

        self.get_logger().info(f'Final result: {result.sequence}')
        return result

def main(args=None):
    rclpy.init(args=args)
    server = FibonacciActionServer()

    # Use multi-threaded executor for action servers
    executor = MultiThreadedExecutor()
    rclpy.spin(server, executor=executor)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Action Client Implementation

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_client')

        # Create action client
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

        # Wait for server
        while not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info('Action server not available, waiting...')

    def send_goal(self, order):
        """Send fibonacci goal"""
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info(f'Sending goal: order={order}')

        # Send goal and get handle
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Wait for goal acceptance
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # Wait for result
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.partial_sequence}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Final result: {result.sequence}')

def main(args=None):
    rclpy.init(args=args)
    client = FibonacciActionClient()

    client.send_goal(10)

    # Spin to process callbacks
    rclpy.spin(client)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Communication Pattern Comparison

```
TOPIC (One-way, async):
Publisher → /topic → Subscriber
                   → Subscriber
                   → Subscriber

SERVICE (Request-reply, sync):
Client → /service → Server
      ← response ←

ACTION (Goal with feedback, async):
Client → GOAL
      ← FEEDBACK (multiple times)
      ← RESULT
```

---

## 4. Custom Message Types

### Why Custom Messages?

Standard message types (String, Int32, Pose) don't always fit your data:

```python
# Bad: Try to fit robot joint state in String
joint_info = "Joint1:45.3,Joint2:90.1,Joint3:-10.5"  # Hard to parse

# Good: Use custom JointState message
msg.positions = [45.3, 90.1, -10.5]
msg.velocities = [0.5, 0.2, -0.1]
msg.effort = [10, 5, 2]
```

### Defining Custom Messages

Create a `.msg` file (plain text, similar to struct):

```msg
# Point3D.msg - A 3D point
float64 x
float64 y
float64 z
```

Used in code:

```python
from my_package.msg import Point3D

msg = Point3D()
msg.x = 1.5
msg.y = 2.3
msg.z = -0.7
publisher.publish(msg)
```

### Complex Custom Messages

```msg
# Robot3DPosition.msg - Robot's full 3D state
float64 x
float64 y
float64 z
float64 roll
float64 pitch
float64 yaw
string frame_id
```

```python
from my_package.msg import Robot3DPosition

state = Robot3DPosition()
state.x = 10.0
state.y = 20.0
state.z = 0.5
state.roll = 0.0
state.pitch = 0.0
state.yaw = 3.14159
state.frame_id = "world"
```

### Message Field Types

| Type | Python Example | Notes |
|------|---|---|
| `float32`, `float64` | `1.5` | Floating point |
| `int8`, `int16`, `int32`, `int64` | `42` | Signed integers |
| `uint8`, `uint16`, `uint32`, `uint64` | `42` | Unsigned integers |
| `bool` | `True` | Boolean |
| `string` | `"hello"` | Text |
| `MyMsg` | `msg_obj` | Other message types (nested) |
| `MyMsg[]` | `[msg1, msg2]` | Arrays of messages |
| `MyMsg[10]` | `[msg1, ..., msg10]` | Fixed-size arrays |

---

## 5. Launch Files and Parameter Configuration

### Launch File Basics

Instead of manually starting multiple nodes, use a **launch file** to start them all at once:

```xml
<!-- src/my_package/launch/full_system.launch.xml -->
<launch>
  <!-- Start publisher node -->
  <node pkg="my_package" exec="publisher_node" name="pub"/>

  <!-- Start subscriber node -->
  <node pkg="my_package" exec="subscriber_node" name="sub"/>

  <!-- Start service server -->
  <node pkg="my_package" exec="service_server" name="server"/>
</launch>
```

Run with:
```bash
ros2 launch my_package full_system.launch.xml
```

### Parameters in Launch Files

ROS 2 allows **parameters** - configuration values passed to nodes:

```xml
<!-- launch/configurable_system.launch.xml -->
<launch>
  <!-- Parameter definition -->
  <arg name="robot_name" default="robot_1"/>
  <arg name="update_rate" default="100"/>

  <!-- Node with parameters -->
  <node pkg="my_package" exec="controller" name="controller">
    <param name="robot_name" value="$(var robot_name)"/>
    <param name="update_rate" value="$(var update_rate)"/>
  </node>
</launch>
```

### Accessing Parameters in Python Nodes

```python
class ConfigurableNode(Node):
    def __init__(self):
        super().__init__('configurable_node')

        # Declare parameter with default
        self.declare_parameter('robot_name', 'default_robot')
        self.declare_parameter('update_rate', 100)

        # Get parameter value
        robot_name = self.get_parameter('robot_name').value
        update_rate = self.get_parameter('update_rate').value

        self.get_logger().info(f'Robot: {robot_name}, Rate: {update_rate} Hz')
```

### Running with Custom Parameters

```bash
# Override parameters on command line
ros2 run my_package my_node --ros-args -p robot_name:="my_robot" -p update_rate:=50
```

---

## 6. Integrating AI/ML Code with ROS Control

### Architecture: AI → ROS → Actuators

A common pattern in robotics involves:
1. **Perception**: Sensor input (topics)
2. **AI/ML**: Process input, generate commands (pure Python)
3. **Control**: Send commands to actuators (topics/services/actions)

```
Sensor Topic    →  AI Node  →  Control Topic
/joint_state         [ML        /joint_commands
/camera/image        Model]
/object_detection        ↓
                    Commands
```

### Example: Joint Controller with Feedback Loop

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState

class JointController(Node):
    def __init__(self):
        super().__init__('joint_controller')

        # Subscribe to actual joint state
        self.state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.state_callback,
            10
        )

        # Publish desired commands
        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        # Control loop
        self.timer = self.create_timer(0.01, self.control_loop)
        self.current_state = None

    def state_callback(self, msg):
        """Store current joint state"""
        self.current_state = msg

    def control_loop(self):
        """Main control algorithm"""
        if self.current_state is None:
            return

        # Example AI logic: Simple P-controller
        # Goal: Move all joints to 45 degrees
        goal_position = [0.785, 0.785, 0.785]  # 45 degrees in radians

        # Calculate error
        positions = list(self.current_state.position)
        errors = [goal_position[i] - positions[i] for i in range(len(positions))]

        # P-controller gain
        kp = 0.5
        commands = [kp * error for error in errors]

        # Publish commands
        cmd_msg = Float64MultiArray()
        cmd_msg.data = commands
        self.cmd_pub.publish(cmd_msg)

        self.get_logger().info(f'State: {positions}, Error: {errors}, Cmd: {commands}')

def main(args=None):
    rclpy.init(args=args)
    controller = JointController()
    rclpy.spin(controller)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Best Practices for AI Integration

1. **Separate computation from communication**: Do heavy processing in batch, send results via topics
2. **Use appropriate QoS**: Vision → BEST_EFFORT; control → RELIABLE
3. **Monitor latency**: Use `ros2 topic hz` to verify update rates
4. **Graceful degradation**: Handle sensor failures, missing data
5. **Test in simulation first**: Use RViz2 or Gazebo before real hardware

---

## 7. Complete Examples: Service and Action

### Service Example: Collision Check

```python
# collision_check_server.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from example_interfaces.srv import SetBool

class CollisionChecker(Node):
    def __init__(self):
        super().__init__('collision_checker')
        self.service = self.create_service(
            SetBool,
            'check_collision',
            self.check_collision_callback
        )

    def check_collision_callback(self, request, response):
        # Simulate collision check
        # In real system, would query planning library
        response.success = False
        response.message = "Path is collision-free"
        self.get_logger().info(f'Collision check: {response.message}')
        return response

def main(args=None):
    rclpy.init(args=args)
    server = CollisionChecker()
    rclpy.spin(server)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Action Example: Navigation Goal

Complete action for robot navigation (Goal → Feedback → Result):

- **Goal**: Target position (x, y)
- **Feedback**: Current progress (distance to goal)
- **Result**: Success/Failure

---

## Summary

| Concept | Use Case | Blocking | Feedback |
|---------|----------|----------|----------|
| **Topic** | Streaming, continuous data | No | N/A |
| **Service** | One-time queries, configuration | Yes | N/A |
| **Action** | Long-running tasks, navigation | No | Yes |
| **Custom Message** | Complex data structures | N/A | N/A |
| **Launch File** | Multi-node startup, parameters | N/A | N/A |

---

## Key Takeaways

1. **Topics** are for continuous data flow; **services** for synchronous queries; **actions** for long-running tasks
2. **Custom messages** allow type-safe communication of complex data
3. **Launch files** enable reproducible multi-node startup
4. **AI/ML integration** requires careful attention to communication latency and QoS
5. **Parameters** make nodes configurable without code changes

---

## Next Steps

- Implement the service examples yourself
- Create a custom message for your domain
- Build an action-based controller for feedback
- Proceed to Exercise 2.1: Service Integration

---

## Glossary References

- **Service**: See [Glossary: Service](./glossary.md#service)
- **Action**: See [Glossary: Action](./glossary.md#action)
- **Custom Message**: See [Glossary: Message](./glossary.md#message)
- **Launch File**: See [Glossary: Launch-File](./glossary.md#launch-file)
- **Parameter**: See [Glossary: Parameter](./glossary.md#parameter)

---

**Citation**: Open Robotics. "ROS 2 Services." *ROS 2 Documentation*, Jan. 2026. [Online]. Available: https://docs.ros.org/en/humble/Tutorials/Services/Understanding-ROS2-Services.html. [Accessed: Jan. 22, 2026].

Open Robotics. "ROS 2 Actions." *ROS 2 Documentation*, Jan. 2026. [Online]. Available: https://docs.ros.org/en/humble/Tutorials/Actions/Understanding-ROS2-Actions.html. [Accessed: Jan. 22, 2026].

---

*Chapter 2: Communication Patterns* | Version 1.0.0 | Module 1 - ROS 2 Fundamentals
