# Module 1 Code Examples

This directory contains working code examples for Module 1 - ROS 2 Fundamentals. All examples are tested on Ubuntu 22.04 with ROS 2 Humble.

## Setup Instructions

Before running any examples, ensure:

1. **ROS 2 Humble is installed:**
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 --version
   ```

2. **rclpy and colcon are installed:**
   ```bash
   pip install rclpy
   sudo apt install python3-colcon-common-extensions
   ```

3. **All tests pass:**
   ```bash
   cd /path/to/Hackathon-1
   pytest tests/ -v
   ```

## Examples by Chapter

### Chapter 1: ROS 2 Architecture

**Learning outcomes**: Understand nodes, topics, pub/sub communication, ROS 2 CLI tools

| Example | File | Concepts | Time |
|---------|------|----------|------|
| Hello World Publisher | `1-hello-world-pub.py` | Nodes, publishers, message types | 10 min |
| Hello World Subscriber | `1-hello-world-sub.py` | Nodes, subscribers, callbacks | 10 min |
| Topic Introspection | `1-topic-introspection.sh` | ros2 CLI tools, topic inspection | 5 min |

**Running Example 1:**
```bash
# Terminal 1: Run publisher
python3 examples/1-hello-world-pub.py

# Terminal 2: Run subscriber
python3 examples/1-hello-world-sub.py

# Terminal 3: Inspect topic (optional)
source /opt/ros/humble/setup.bash
ros2 topic list
ros2 topic echo /hello_world_topic
```

---

### Chapter 2: Communication Patterns

**Learning outcomes**: Services, actions, custom messages, launch files, AI/ML integration

| Example | File | Concepts | Time |
|---------|------|----------|------|
| Service Server | `2-service-server.py` | Services, server pattern, request-reply | 10 min |
| Service Client | `2-service-client.py` | Services, client pattern, blocking calls | 10 min |
| Custom Message | `2-custom-message.msg` | Message definition, .msg syntax | 5 min |
| Action Server | `2-action-server.py` | Actions, long-running tasks, feedback | 15 min |
| Action Client | `2-action-client.py` | Actions, goal submission, result handling | 15 min |
| Joint Controller | `2-joint-controller.py` | Integration pattern, pub/sub feedback loop | 15 min |

**Running Example 2 (Service):**
```bash
# Terminal 1: Run service server
python3 examples/2-service-server.py

# Terminal 2: Run service client
python3 examples/2-service-client.py
```

**Running Example 2 (Action):**
```bash
# Terminal 1: Run action server
python3 examples/2-action-server.py

# Terminal 2: Run action client
python3 examples/2-action-client.py
```

---

### Chapter 3: URDF & Robot Description

**Learning outcomes**: URDF syntax, robot modeling, visualization in RViz2

| Example | File | Concepts | Time |
|---------|------|----------|------|
| Simple Humanoid URDF | `3-simple-humanoid.urdf` | URDF syntax, links, joints, visual/collision geometry | 10 min |
| Extended Humanoid URDF | `3-humanoid-extended.urdf` | Complex kinematics, joint hierarchies | 15 min |
| RViz2 Visualization | `3-urdf-viz-launch.xml` | Launch files, RViz2 configuration | 10 min |

**Running Example 3:**
```bash
# Validate URDF syntax
python3 -m pytest tests/test_chapter_3.py -v

# Visualize in RViz2 (if installed)
ros2 launch /path/to/3-urdf-viz-launch.xml
```

---

## Example Naming Convention

Examples follow the pattern: `<chapter>-<concept>-<type>`

- **chapter**: Chapter number (1, 2, 3)
- **concept**: Main topic (hello-world, service, urdf, etc.)
- **type**: File type (pub, sub, py, msg, urdf, xml, sh)

Example: `2-service-server.py` = Chapter 2, Service pattern, Server implementation (Python)

---

## Testing Examples

All examples include automated tests. To run:

```bash
# Test all examples
pytest tests/test_chapter_1.py tests/test_chapter_2.py tests/test_chapter_3.py -v

# Test specific chapter
pytest tests/test_chapter_1.py -v

# Run with coverage
pytest tests/ --cov=examples --cov-report=html
```

---

## Performance Targets

- **Example startup**: < 5 seconds
- **Example execution**: < 30 seconds
- **Message latency**: < 100ms (for pub/sub examples)
- **Service call latency**: < 50ms
- **URDF parsing**: < 1 second

---

## Troubleshooting

### "ros2: command not found"
```bash
source /opt/ros/humble/setup.bash
```

### "No module named 'rclpy'"
```bash
pip install rclpy
```

### "Cannot import ROS 2 message types"
- Ensure ROS 2 environment is sourced
- Verify message packages are installed: `ros2 pkg list`

### Examples time out or hang
- Check that ROS 2 daemon is running: `ros2 daemon status`
- Restart if needed: `ros2 daemon kill && sleep 1 && ros2 daemon start`

### URDF visualization not working
- Install RViz2: `sudo apt install ros-humble-rviz2`
- Verify URDF syntax: `python3 -m urdf_parser_py.urdf_parser <urdf-file>`

---

## Additional Resources

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [URDF Documentation](http://wiki.ros.org/urdf)
- [RViz2 Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/About-RViz2.html)

---

**Version**: 1.0.0
**Tested on**: Ubuntu 22.04 + ROS 2 Humble
**Last updated**: 2026-01-22
