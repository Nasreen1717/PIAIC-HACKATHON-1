# Exercise 1.1: Create a Publisher Node

## Problem Statement

Create a ROS 2 publisher node that publishes an integer counter to the `counter_topic` topic, incrementing the counter every 1 second.

**Learning Objectives**:
- Understand how to create a ROS 2 node in Python
- Learn to create and use publishers
- Implement periodic publishing using timers

**Estimated Time**: 20-30 minutes
**Difficulty**: Beginner

---

## Requirements

Your publisher node must:

1. **Node name**: Create a node named `counter_publisher`
2. **Topic**: Publish to a topic named `counter_topic`
3. **Message type**: Use `std_msgs.msg.Int32`
4. **Publishing frequency**: Publish exactly once per second (1 Hz)
5. **Counter behavior**: Start at 0 and increment by 1 each publication
6. **Logging**: Log each message published with the counter value
7. **Graceful shutdown**: Handle Ctrl+C properly (KeyboardInterrupt)

---

## Acceptance Criteria

| Criterion | Measurement | Pass/Fail |
|-----------|-------------|-----------|
| Node initializes without errors | `rclpy.init()` completes | |
| Publisher is created on correct topic | `ros2 topic list` shows `/counter_topic` | |
| Message type is correct | `ros2 topic info /counter_topic` shows `std_msgs/Int32` | |
| Publishing frequency is 1 Hz | `ros2 topic hz /counter_topic` shows ~1 Hz | |
| Counter increments correctly | `ros2 topic echo /counter_topic` shows 0, 1, 2, ... | |
| Node name is correct | `ros2 node list` shows `/counter_publisher` | |

---

## Hints

If you're stuck, try these hints:

**Hint 1**: You need to import these:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
```

**Hint 2**: Node structure:
```python
class CounterPublisher(Node):
    def __init__(self):
        super().__init__('counter_publisher')
        # Create publisher here
        # Create timer here
```

**Hint 3**: Create a publisher with:
```python
self.publisher = self.create_publisher(Int32, 'counter_topic', 10)
```

**Hint 4**: Create a timer that fires every 1 second:
```python
self.timer = self.create_timer(1.0, self.timer_callback)
```

**Hint 5**: In the timer callback, create and publish an Int32 message:
```python
def timer_callback(self):
    msg = Int32()
    msg.data = self.counter
    self.publisher.publish(msg)
```

---

## Template

Here's a template to get started:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterPublisher(Node):
    def __init__(self):
        super().__init__('counter_publisher')

        # TODO: Create a publisher
        # TODO: Create a timer
        # TODO: Initialize counter

    def timer_callback(self):
        # TODO: Create Int32 message
        # TODO: Set message data to counter value
        # TODO: Publish message
        # TODO: Log publication
        # TODO: Increment counter


def main(args=None):
    rclpy.init(args=args)
    node = CounterPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## Testing Your Solution

### Manual Testing

1. **Run your node**:
   ```bash
   python3 exercises/1-1-create-publisher/solution.py
   ```

2. **In another terminal, check topics**:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 topic list
   ros2 topic info /counter_topic
   ```

3. **View published messages**:
   ```bash
   ros2 topic echo /counter_topic
   ```

4. **Check publishing frequency**:
   ```bash
   ros2 topic hz /counter_topic
   ```

### Automated Testing

Run the test suite:
```bash
python3 -m pytest exercises/1-1-create-publisher/test_solution.py -v
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Wrong topic name | Publisher/subscriber can't find each other | Double-check topic name in `create_publisher()` |
| Wrong message type | Type mismatch errors | Use `Int32` from `std_msgs.msg` |
| No timer | Messages only publish once | Create timer with `create_timer(period, callback)` |
| Publishing in `__init__` | Message publishes before spin | Use timer callback, not `__init__` |
| No Ctrl+C handling | Can't stop with Ctrl+C | Use try-except with `KeyboardInterrupt` |

---

## Reference Solution

You can view the reference solution in `solution.py`, but try to solve it yourself first!

**Key points to verify**:
- Node name is `counter_publisher`
- Topic name is `counter_topic`
- Message type is `Int32`
- Timer period is 1.0 second
- Counter increments each callback
- Proper logging and error handling

---

## Extension Challenges

If you finish early, try these extensions:

**Challenge 1**: Make the publishing rate configurable:
```python
# Allow: python3 solution.py --ros-args -p rate:=2.0
# This would publish at 2 Hz instead of 1 Hz
```

**Challenge 2**: Add a reset service:
- Create a ROS 2 service that resets the counter to 0
- When called, counter resets

**Challenge 3**: Monitor and stop at a limit:
- Add parameter `max_count` (default: infinite)
- Stop publishing when counter reaches max_count

---

## Grading Rubric

| Aspect | Points | Criteria |
|--------|--------|----------|
| **Functionality** | 40 | Code runs without errors; publishes to correct topic |
| **Correctness** | 40 | Publishes Int32 messages; counter increments; frequency is 1 Hz |
| **Code Quality** | 10 | Follows PEP 8; includes docstrings |
| **Error Handling** | 10 | Handles Ctrl+C; clean shutdown |
| **Total** | 100 | |

---

## Related Learning

- **Previous**: Chapter 1 - Architecture (Nodes and Topics)
- **Next**: Exercise 1.2 - Create a Subscriber
- **Glossary**: [Publisher](../../docs/module-1/glossary.md#publisher), [Topic](../../docs/module-1/glossary.md#topic)

---

*Exercise 1.1: Create a Publisher* | Module 1 - ROS 2 Fundamentals | Difficulty: Beginner
