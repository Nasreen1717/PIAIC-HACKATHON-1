# Quickstart: Module 2 - The Digital Twin (30 Minutes)

**Objective**: Get your first Gazebo simulation running with ROS 2, visualize in RViz2, and understand the workflow.

**Prerequisites**:
- Ubuntu 22.04 LTS with ROS 2 Humble installed (from Module 1 setup)
- Basic familiarity with ROS 2 CLI tools (`ros2 topic`, `ros2 node`, etc.)
- Gazebo 11+ installed

---

## Step 1: Verify Installation (2 minutes)

```bash
# Check ROS 2
ros2 --version
# Expected: ROS 2 Humble Hawksbill (2022.03.x)

# Check Gazebo
gazebo --version
# Expected: Gazebo version 11.x.x

# Check gazebo_ros integration
ros2 pkg list | grep gazebo_ros
# Expected: gazebo_ros, gazebo_ros2_control, gazebo_ros_pkgs, etc.
```

If any check fails, install missing packages:
```bash
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control
```

---

## Step 2: Download & Examine Example Files (3 minutes)

Get the example files from the course repository:

```bash
# Create a working directory
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Copy example files (you'll clone or download these)
# For now, create them manually:

cat > humanoid.launch.xml << 'EOF'
<?xml version="1.0"?>
<launch>
  <!-- Load humanoid URDF -->
  <param name="robot_description" command="cat /path/to/humanoid.urdf"/>

  <!-- Start Gazebo with empty world -->
  <node pkg="gazebo_ros" exec="gazebo" args="--verbose" output="screen"/>

  <!-- Robot state publisher (publishes transforms) -->
  <node pkg="robot_state_publisher" exec="robot_state_publisher" output="screen">
    <param name="robot_description" command="cat /path/to/humanoid.urdf"/>
  </node>

  <!-- Joint state broadcaster (reads joint states from simulation) -->
  <node pkg="gazebo_ros2_control" exec="gazebo_ros2_control" output="screen"/>
</launch>
EOF
```

---

## Step 3: Start Gazebo Simulation (5 minutes)

**Terminal 1: Launch Gazebo with humanoid robot**

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws

# This launches Gazebo client and robot state publisher
ros2 launch humanoid.launch.xml
```

You should see:
- Gazebo 3D window opening with a humanoid robot
- Console output showing loaded URDF and initialized plugins
- No errors in the terminal (some warnings are OK)

---

## Step 4: Verify ROS 2 Integration (5 minutes)

**Terminal 2: Inspect ROS 2 topics**

```bash
source /opt/ros/humble/setup.bash

# List all active topics
ros2 topic list

# Expected output (includes):
# /gazebo/link_states
# /gazebo/model_states
# /gazebo/set_entity_state
# /joint_states
# /tf
# /tf_static
```

**Terminal 2: Listen to joint state**

```bash
# View current joint positions and velocities
ros2 topic echo /joint_states --once

# Expected output:
# header:
#   stamp:
#     sec: ...
#     nsec: ...
#   frame_id: ''
# name:
# - left_shoulder
# - right_shoulder
# - left_hip
# - right_hip
# position: [0.0, 0.0, 0.0, 0.0]
# velocity: [0.0, 0.0, 0.0, 0.0]
# effort: [0.0, 0.0, 0.0, 0.0]
```

---

## Step 5: Visualize in RViz2 (5 minutes)

**Terminal 3: Start RViz2**

```bash
source /opt/ros/humble/setup.bash
rviz2 -d /opt/ros/humble/share/gazebo_ros/rviz/gazebo.rviz
```

You should see:
- RViz2 window opening
- Robot skeleton displayed with coordinate frames
- TF tree showing link hierarchy
- You can interact with the robot (rotate, zoom)

**Manual RViz2 Setup (if needed)**:

1. Add display: "RobotModel"
   - Set "Robot Description" parameter: `/robot_description`
2. Add display: "TF"
   - Visualize all coordinate frames
3. Add display: "PointCloud2" (for sensor visualization in Chapter 6)

---

## Step 6: Control the Robot (8 minutes)

**Terminal 4: Create a simple controller node**

Create a file `simple_controller.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import math
import time

class SimpleController(Node):
    def __init__(self):
        super().__init__('simple_controller')

        # Publisher for joint commands
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/joint_commands',
            10
        )

        self.get_logger().info('Controller initialized')

        # Timer for control loop (10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.counter = 0

    def control_loop(self):
        """Simple sinusoidal joint control."""
        msg = Float64MultiArray()

        # Apply sinusoidal motion to joints
        amplitude = 0.5  # radians (±28 degrees)
        frequency = 0.5  # Hz
        time_val = self.counter * 0.1

        angle = amplitude * math.sin(2 * math.pi * frequency * time_val)

        # Four joints: left_shoulder, right_shoulder, left_hip, right_hip
        msg.data = [angle, -angle, angle * 0.5, -angle * 0.5]

        self.publisher.publish(msg)
        self.get_logger().info(f'Published joint commands: {[round(a, 3) for a in msg.data]}')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    controller = SimpleController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Run the controller:**

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
python3 simple_controller.py
```

**Observe the result:**
- Robot in Gazebo begins moving arms and legs in sinusoidal pattern
- RViz2 shows skeleton moving in sync
- Terminal outputs joint commands being sent

---

## Step 7: Verify the Complete Workflow (2 minutes)

In a new terminal, visualize the communication:

```bash
source /opt/ros/humble/setup.bash

# View the message rate on /joint_states (should be ~50 Hz)
ros2 topic hz /joint_states

# View node graph (visual dependency diagram)
ros2 run rqt_graph rqt_graph

# Expected graph:
# simple_controller → /joint_commands
# gazebo (simulator) → /joint_states, /tf, /tf_static
# robot_state_publisher → /tf
# rviz2 (visualizer) reads all topics
```

---

## Cleanup (1 minute)

When done, stop all terminals:

```bash
# In each terminal:
Ctrl+C
```

---

## What You've Learned

✅ **Gazebo Setup**: Loaded a robot URDF in Gazebo simulation
✅ **ROS 2 Integration**: Published/subscribed to joint state topics
✅ **Visualization**: Visualized robot in RViz2 with coordinate frames
✅ **Control Loop**: Implemented a simple joint controller node
✅ **Complete Workflow**: Gazebo → ROS 2 → Control → RViz2

---

## Next Steps

1. **Chapter 4**: Learn Gazebo architecture, physics simulation, sensor setup
2. **Chapter 5**: Export this robot to Unity and render it with realistic lighting
3. **Chapter 6**: Add LiDAR and depth camera sensors; process sensor data
4. **Capstone**: Integrate all three (physics + rendering + perception) in one pipeline

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "gazebo: command not found" | Install: `sudo apt install ros-humble-gazebo-ros-pkgs` |
| "robot_description parameter not found" | Verify launch file loads URDF correctly; check file path |
| RViz2 doesn't show robot | Add "RobotModel" display; set `/robot_description` parameter |
| Joint commands not working | Verify gazebo_ros2_control plugin is loaded in URDF |
| No /joint_states topic | Check Gazebo console for plugin load errors |

---

## Key Commands Reference

```bash
# List all topics
ros2 topic list

# Echo a topic (print messages)
ros2 topic echo /joint_states

# Measure publishing frequency (Hz)
ros2 topic hz /joint_states

# Check node information
ros2 node info /gazebo

# View ROS 2 node graph
ros2 run rqt_graph rqt_graph

# Launch Gazebo with custom world
ros2 launch gazebo_ros gazebo.launch.xml world:=~/my_world.world

# Record rosbag (capture all topics)
ros2 bag record -a

# Playback rosbag
ros2 bag play rosbag2_2026_01_22-10_00_00
```

---

**Status**: ✅ **QUICKSTART COMPLETE**

You now have a working Gazebo + ROS 2 + RViz2 setup. Ready to proceed to Chapter 4 detailed material.

---

**Citation**: Open Robotics, "ROS 2 Humble Launch," *ROS 2 Documentation*, [Online]. Available: https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-system.html. [Accessed: Jan. 22, 2026].

Open Source Robotics Foundation, "Gazebo Documentation," [Online]. Available: https://gazebosim.org/docs/. [Accessed: Jan. 22, 2026].
