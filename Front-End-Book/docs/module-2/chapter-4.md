# Chapter 4: Physics Simulation with Gazebo

**Duration**: 4-6 days of study (8-12 hours)
**Prerequisites**: Module 1 (ROS 2 Fundamentals), Gazebo 11+ installed
**Learning Outcomes**: Understand Gazebo architecture, load robots, simulate physics, integrate with ROS 2

---

## Learning Objectives

By the end of this chapter, you will be able to:

- **Understand Gazebo architecture** and the client-server model
- **Load URDF robot models** into Gazebo simulations
- **Configure physics parameters** (gravity, friction, collision detection)
- **Simulate realistic physics** including collisions, joint dynamics, and forces
- **Integrate Gazebo with ROS 2** for topic-based control
- **Control simulated robots** via ROS 2 topics and services
- **Debug physics simulations** using tools and common troubleshooting techniques
- **Measure and optimize simulation performance** for real-time applications

---

## Section 1: Gazebo Architecture

### Overview

Gazebo is an open-source physics simulation platform that provides:

1. **Physics Simulation Engine** - Simulates gravity, collisions, joint dynamics, and forces
2. **3D Graphics Rendering** - Visualizes the simulation environment
3. **Sensor Simulation** - Generates realistic sensor data (cameras, lasers, IMUs)
4. **ROS 2 Integration** - Communicates with ROS 2 nodes via topics and services
5. **Plugin System** - Extends functionality with custom controllers and sensors

### Client-Server Architecture

Gazebo uses a client-server model:

```
┌─────────────────────────────────────────────┐
│         Gazebo Architecture                  │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │   Gazebo Server (gzserver)           │  │
│  │  ─────────────────────────────────   │  │
│  │  • Physics simulation (ODE/Bullet)   │  │
│  │  • World state management            │  │
│  │  • Collision detection               │  │
│  │  • ROS 2 interface                   │  │
│  │  • Sensor data generation            │  │
│  └──────────────────────────────────────┘  │
│              △                               │
│              │ (socket communication)       │
│              ▽                               │
│  ┌──────────────────────────────────────┐  │
│  │   Gazebo Client (gzclient)           │  │
│  │  ─────────────────────────────────   │  │
│  │  • 3D visualization (OpenGL)         │  │
│  │  • Interactive controls              │  │
│  │  • Parameter editing                 │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │   ROS 2 Nodes (Your Code)            │  │
│  │  ─────────────────────────────────   │  │
│  │  • Subscribe to /gazebo/* topics     │  │
│  │  • Publish joint commands            │  │
│  │  • Call Gazebo ROS 2 services        │  │
│  └──────────────────────────────────────┘  │
│                                              │
└─────────────────────────────────────────────┘
```

**Key Points**:
- **Server** runs the physics simulation independently (can run headless)
- **Client** connects to server for visualization (optional)
- **ROS 2 nodes** connect to server via gazebo_ros bridge plugins

### Physics Engines

Gazebo supports multiple physics engines:

| Engine | Stability | Speed | Use Case |
|--------|-----------|-------|----------|
| **ODE** (default) | Excellent | Moderate | Most robotics applications |
| **Bullet** | Good | Faster | Large simulations, high performance |
| **DART** | Good | Fast | Humanoids, articulated systems |
| **Simbody** | Experimental | Variable | Research applications |

**For this module**: We use **ODE** (default) for stability and ROS 2 integration.

### Simulation Loop

The Gazebo simulation loop runs at a fixed physics timestep:

```
Physics Timestep: 0.001 seconds (1000 Hz default)

┌─────────────────────────────────────────┐
│ 1. Update sensor readings               │
│    (read joint positions, compute forces)│
├─────────────────────────────────────────┤
│ 2. Apply control inputs                 │
│    (read joint commands from ROS 2)      │
├─────────────────────────────────────────┤
│ 3. Physics step                         │
│    (integrate forces, update positions) │
├─────────────────────────────────────────┤
│ 4. Collision detection                  │
│    (find contact points and forces)     │
├─────────────────────────────────────────┤
│ 5. Publish data                         │
│    (publish joint states, sensor data)  │
├─────────────────────────────────────────┤
│ 6. Render visualization                 │
│    (update 3D view in gzclient)         │
└─────────────────────────────────────────┘
           (repeat every 1ms)
```

**Important**: Physics simulation runs independently of visualization frequency. A simulation can run at 1000 Hz while displaying at 30 FPS.

### Configuration

Gazebo configuration in `~/.gazebo/default.oscrc`:

```xml
<sdf version="1.4">
  <world name="default">
    <!-- Physics Engine Configuration -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>  <!-- Physics timestep (1 ms) -->
      <real_time_factor>1.0</real_time_factor> <!-- Real-time speed -->
      <real_time_update_rate>1000</real_time_update_rate> <!-- Updates per second -->

      <!-- ODE Physics Engine Settings -->
      <ode>
        <solver>
          <type>quick</type>
          <iters>50</iters>  <!-- Solver iterations per step -->
          <sor>1.3</sor>     <!-- Successive Over-Relaxation parameter -->
        </solver>
        <constraints>
          <cfm>0</cfm>       <!-- Constraint force mixing -->
          <erp>0.2</erp>     <!-- Error reduction parameter -->
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>

    <!-- World Properties -->
    <gravity>0 0 -9.81</gravity>           <!-- Gravity (m/s²) -->
    <ambient_light>
      <color>0.5 0.5 0.5 1.0</color>
    </ambient_light>
  </world>
</sdf>
```

---

## Section 2: URDF & SDF - From Robot Description to Simulation

### URDF (Unified Robot Description Format)

URDF (learned in Module 1) describes robot structure:

```xml
<robot name="humanoid">
  <!-- Links: rigid body segments -->
  <link name="torso">
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.1"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
  </link>

  <!-- Joints: connections between links -->
  <joint name="shoulder" type="revolute">
    <parent link="torso"/>
    <child link="upper_arm"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="3.14" effort="100" velocity="2.0"/>
    <dynamics damping="0.1" friction="0.05"/>
  </joint>
</robot>
```

**URDF Limitations for Simulation**:
- No physics engine specification
- No sensor definitions for simulation
- No plugin information
- Limited collision/friction control

### SDF (Simulation Description Format)

SDF extends URDF with simulation-specific properties:

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="humanoid">
    <!-- Link definition -->
    <link name="torso">
      <inertial>
        <mass>10.0</mass>
        <inertia>
          <ixx>0.1</ixx>
          <iyy>0.1</iyy>
          <izz>0.1</izz>
        </inertia>
      </inertial>

      <!-- Visual geometry (for rendering) -->
      <visual name="visual">
        <geometry>
          <box>
            <size>0.3 0.2 0.5</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>file://media/materials/scripts/gazebo.material</uri>
            <name>Gazebo/Red</name>
          </script>
        </material>
      </visual>

      <!-- Collision geometry (for physics) -->
      <collision name="collision">
        <geometry>
          <box>
            <size>0.3 0.2 0.5</size>
          </box>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>0.7</mu>      <!-- Coefficient of friction -->
              <mu2>0.7</mu2>
              <fdir1>0 0 0</fdir1>
            </ode>
          </friction>
          <contact>
            <ode>
              <soft_cfm>0</soft_cfm>
              <soft_erp>0.2</soft_erp>
              <kp>1e13</kp>      <!-- Contact stiffness -->
              <kd>1</kd>         <!-- Contact damping -->
              <max_vel>0.01</max_vel>
              <min_depth>0.001</min_depth>
            </ode>
          </contact>
        </surface>
      </collision>
    </link>

    <!-- Joint with physics properties -->
    <joint name="shoulder" type="revolute">
      <parent link="torso"/>
      <child link="upper_arm"/>
      <axis>
        <xyz>0 1 0</xyz>
        <use_parent_model_frame>0</use_parent_model_frame>
        <limit>
          <lower>0</lower>
          <upper>3.14159</upper>
          <effort>100</effort>
          <velocity>2.0</velocity>
        </limit>
        <dynamics>
          <damping>0.1</damping>     <!-- Viscous friction -->
          <friction>0.05</friction>  <!-- Static friction -->
          <spring_reference>0</spring_reference>
          <spring_stiffness>0</spring_stiffness>
        </dynamics>
      </axis>
    </joint>

    <!-- Gazebo-specific physics -->
    <gazebo reference="torso">
      <material>Gazebo/Red</material>
      <selfCollide>false</selfCollide>
      <friction>
        <rolling>0.1</rolling>
        <torsional>
          <coefficient>1.0</coefficient>
          <use_patch_radius>true</use_patch_radius>
          <patch_radius>0.0</patch_radius>
        </torsional>
      </friction>
    </gazebo>
  </model>
</sdf>
```

**Key SDF Additions**:
- **Friction/contact models** - Detailed surface interaction properties
- **Visual materials** - Rendering appearance (color, texture)
- **Gazebo plugins** - Extensions for sensors, controllers
- **Physics tuning** - Contact stiffness, damping parameters

### URDF to SDF Conversion

Gazebo automatically converts URDF to SDF internally, but you can also convert manually:

```bash
# Convert URDF to SDF
gz sdf -p humanoid.urdf > humanoid.sdf

# Validate SDF syntax
gz sdf humanoid.sdf
```

---

## Section 3: Loading & Running Simulations

### Gazebo World Files

A world file (.world or .sdf) defines the complete simulation environment:

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <!-- Physics engine configuration -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Gravity -->
    <gravity>0 0 -9.81</gravity>

    <!-- Ambient lighting -->
    <ambient_light>
      <color>0.5 0.5 0.5 1</color>
    </ambient_light>

    <!-- Light sources -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.9 0.9 0.9 1</specular>
      <attenuation>
        <range>20</range>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Include robot model -->
    <model name="humanoid">
      <include>
        <uri>model://humanoid</uri>
        <pose>0 0 1 0 0 0</pose>  <!-- Position robot above ground -->
      </include>
    </model>

    <!-- Optional: objects for interaction -->
    <model name="box">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.01</ixx>
            <iyy>0.01</iyy>
            <izz>0.01</izz>
          </inertia>
        </inertial>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 0.1 0.1</size>
            </box>
          </geometry>
        </visual>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 0.1 0.1</size>
            </box>
          </geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>
```

### Launching Gazebo with ROS 2

Create a ROS 2 launch file to start Gazebo with a robot:

```xml
<?xml version="1.0"?>
<launch>
  <!-- Arguments -->
  <arg name="world" default="default.world"/>
  <arg name="paused" default="false"/>
  <arg name="gui" default="true"/>
  <arg name="headless" default="false"/>

  <!-- Set gazebo environment variable -->
  <env name="GAZEBO_RESOURCE_PATH" value="$(find-pkg-share my_robot)/worlds:$GAZEBO_RESOURCE_PATH"/>

  <!-- Start Gazebo server -->
  <node pkg="gazebo_ros" exec="gzserver" args="-s libgazebo_ros_factory.so -s libgazebo_ros_init.so --verbose $(find-pkg-share my_robot)/worlds/$(var world)" output="screen"/>

  <!-- Start Gazebo client (GUI) -->
  <node if="$(var gui)" pkg="gazebo_ros" exec="gzclient" output="screen"/>

  <!-- Load URDF onto parameter server -->
  <param name="robot_description" command="cat $(find-pkg-share my_robot)/urdf/humanoid.urdf"/>

  <!-- Spawn robot in Gazebo -->
  <node pkg="gazebo_ros" exec="spawn_entity.py" args="-topic robot_description -entity humanoid -x 0 -y 0 -z 1"/>

  <!-- Robot state publisher -->
  <node pkg="robot_state_publisher" exec="robot_state_publisher">
    <param name="robot_description" command="cat $(find-pkg-share my_robot)/urdf/humanoid.urdf"/>
  </node>
</launch>
```

**Launch from command line**:

```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Launch Gazebo with robot
ros2 launch my_robot gazebo.launch.xml

# Or start Gazebo directly
gazebo $(find-pkg-share my_robot)/worlds/default.world
```

### Headless Simulation

For cloud deployment or CI/CD, run Gazebo without GUI:

```bash
# Headless (server only)
gzserver $(find-pkg-share my_robot)/worlds/default.world --verbose

# In another terminal, control via ROS 2
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 1.0}}"
```

---

## Section 4: Joint Control & Feedback

### ROS 2 Joint Control Interface

Control simulated joints via ROS 2 topics. Standard messages:

**1. Joint State (Feedback)**

Subscribe to `/joint_states` to read current joint state:

```python
from sensor_msgs.msg import JointState

def joint_state_callback(msg: JointState):
    # msg.name: list of joint names
    # msg.position: list of current positions (radians)
    # msg.velocity: list of current velocities (rad/s)
    # msg.effort: list of current efforts (N⋅m or N)

    for i, name in enumerate(msg.name):
        print(f"{name}: pos={msg.position[i]:.3f}, vel={msg.velocity[i]:.3f}")

node.create_subscription(JointState, '/joint_states', joint_state_callback, 10)
```

**2. Joint Commands**

Publish joint targets to control the robot:

```python
from std_msgs.msg import Float64MultiArray

# Publish joint commands (one target per joint)
msg = Float64MultiArray()
msg.data = [0.5, 0.3, 0.0, 0.0]  # Target positions in radians

publisher = node.create_publisher(Float64MultiArray, '/gazebo/*/cmd_pos', 10)
publisher.publish(msg)
```

**3. Joint Limits & Safety**

Always respect joint limits to prevent simulation instability:

```python
import math

class JointLimits:
    def __init__(self):
        self.names = ["shoulder", "elbow", "hip", "knee"]
        self.lower = [0.0, -math.pi, -math.pi/2, -math.pi/2]
        self.upper = [math.pi, 0.0, math.pi/2, 0.0]
        self.max_velocity = [2.0, 2.0, 2.0, 2.0]
        self.max_effort = [100, 100, 100, 100]

    def clamp_position(self, joint_idx: int, target: float) -> float:
        """Clamp target position to joint limits."""
        return max(self.lower[joint_idx],
                   min(self.upper[joint_idx], target))

    def is_safe(self, joint_idx: int, position: float) -> bool:
        """Check if position is within safe limits."""
        return self.lower[joint_idx] <= position <= self.upper[joint_idx]
```

### PID Control Loop

Implement a simple feedback control loop:

```python
import math
import time

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain

        self.integral = 0.0
        self.last_error = 0.0

    def update(self, error: float, dt: float) -> float:
        """Compute PID control output."""
        # Proportional term
        p_term = self.kp * error

        # Integral term (with anti-windup)
        self.integral += error * dt
        if abs(self.integral) > 10.0:
            self.integral = 10.0 if self.integral > 0 else -10.0
        i_term = self.ki * self.integral

        # Derivative term
        d_term = self.kd * (error - self.last_error) / dt if dt > 0 else 0
        self.last_error = error

        # Total output
        output = p_term + i_term + d_term
        return output

# Example: Move joint to target position
class JointController:
    def __init__(self, node, joint_name: str):
        self.node = node
        self.joint_name = joint_name
        self.target_position = 0.0
        self.current_position = 0.0
        self.pid = PIDController(kp=10.0, ki=0.1, kd=1.0)

        # Subscribe to joint states
        self.node.create_subscription(
            JointState, '/joint_states', self.update_state, 10
        )

        # Publish joint commands
        self.publisher = self.node.create_publisher(
            Float64MultiArray, '/gazebo/humanoid/cmd_pos', 10
        )

        # Control loop timer (10 Hz)
        self.node.create_timer(0.1, self.control_loop)

    def update_state(self, msg: JointState):
        """Update current joint position from feedback."""
        if self.joint_name in msg.name:
            idx = msg.name.index(self.joint_name)
            self.current_position = msg.position[idx]

    def control_loop(self):
        """PID control loop."""
        error = self.target_position - self.current_position
        control_effort = self.pid.update(error, dt=0.1)

        # Publish command
        msg = Float64MultiArray()
        msg.data = [control_effort]
        self.publisher.publish(msg)

        self.node.get_logger().info(
            f"{self.joint_name}: target={self.target_position:.3f}, "
            f"current={self.current_position:.3f}, error={error:.3f}"
        )
```

---

## Section 5: Sensor Simulation Basics

### Built-in Sensor Types

Gazebo supports multiple simulated sensors:

| Type | Output Message | Update Rate | Use |
|------|-----------------|-------------|-----|
| **Camera** | sensor_msgs/Image | 30-60 Hz | RGB-D vision |
| **Laser Scan (2D)** | sensor_msgs/LaserScan | 10-40 Hz | Range measurement |
| **Laser3D/Lidar** | sensor_msgs/PointCloud2 | 10-30 Hz | 3D point clouds |
| **IMU** | sensor_msgs/Imu | 100+ Hz | Acceleration, rotation |
| **Contact** | gazebo_msgs/ContactsState | 100 Hz | Collision forces |

### Adding Sensors to URDF

Example: Add an IMU sensor to the humanoid torso:

```xml
<robot name="humanoid">
  <link name="torso">
    <!-- existing geometry -->
  </link>

  <!-- IMU sensor attached to torso -->
  <joint name="imu_joint" type="fixed">
    <parent link="torso"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <link name="imu_link">
    <inertial>
      <mass value="0.01"/>
      <inertia ixx="0.000001" iyy="0.000001" izz="0.000001"/>
    </inertial>
  </link>

  <!-- Gazebo plugin for IMU simulation -->
  <gazebo reference="imu_link">
    <sensor type="imu" name="imu_sensor">
      <always_on>true</always_on>
      <update_rate>100</update_rate>  <!-- 100 Hz -->
      <visualize>false</visualize>

      <imu>
        <!-- Noise characteristics -->
        <noise>
          <type>gaussian</type>
          <rate>
            <mean>0.0</mean>
            <stddev>0.0</stddev>
            <bias_mean>0.0</bias_mean>
            <bias_stddev>0.0</bias_stddev>
          </rate>
          <accel>
            <mean>0.0</mean>
            <stddev>0.017</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </accel>
        </noise>
      </imu>

      <plugin filename="libgazebo_ros_imu_sensor.so" name="imu_plugin">
        <ros>
          <namespace>/humanoid</namespace>
          <remapping>~/out:=/humanoid/imu</remapping>
        </ros>
        <initial_orientation_as_reference>false</initial_orientation_as_reference>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

### Realistic Sensor Noise

Gazebo can simulate sensor noise to match real hardware:

```xml
<!-- Realistic noise model for camera -->
<sensor type="camera" name="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.02</near>
      <far>300</far>
    </clip>
  </camera>

  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.007</stddev>  <!-- Standard deviation of noise -->
  </noise>

  <update_rate>30</update_rate>
</sensor>
```

---

## Section 6: Common Issues & Debugging

### Physics Instability

**Symptom**: Robot shakes, vibrates, or explodes during simulation

**Causes & Solutions**:

1. **Too-large physics timestep**: Increase simulation accuracy
   ```bash
   # In world file: decrease max_step_size
   <max_step_size>0.0005</max_step_size>  <!-- More accurate -->
   ```

2. **Incorrect inertia matrix**: Ensure inertia is positive-definite
   ```bash
   # Validate URDF inertia
   check_urdf humanoid.urdf
   ```

3. **High friction coefficients**: May cause instability
   ```xml
   <!-- Reduce friction -->
   <mu>0.5</mu>  <!-- Standard rubber-on-concrete -->
   <mu2>0.5</mu2>
   ```

4. **Gravity too high**: Verify gravity is realistic
   ```bash
   # Gazebo default: -9.81 m/s²
   # If simulating on Moon: -1.62 m/s²
   <gravity>0 0 -9.81</gravity>
   ```

### URDF Loading Errors

**Symptom**: `Error: xml/model.sdf cannot load robot description`

**Solutions**:

1. **Validate URDF syntax**:
   ```bash
   check_urdf humanoid.urdf
   ```

2. **Check file paths** (relative vs absolute):
   ```bash
   # Use absolute paths or ${HOME} variables
   <mesh filename="file:///home/user/humanoid/meshes/torso.dae"/>
   ```

3. **Verify mesh files exist**:
   ```bash
   find . -name "*.dae" -o -name "*.stl"
   ```

### ROS 2 Topic Issues

**Symptom**: `/joint_states` topic not appearing

**Debugging**:

```bash
# List all ROS 2 topics
ros2 topic list | grep gazebo

# Check Gazebo plugins loaded
ros2 node list | grep gazebo

# Monitor topic data
ros2 topic echo /joint_states --rate 1
```

### Performance Troubleshooting

**Symptom**: Low FPS (< 30), laggy simulation

**Optimization Tips**:

1. **Reduce collision mesh complexity**:
   ```xml
   <!-- Use simple shapes instead of meshes -->
   <collision>
     <geometry>
       <cylinder>
         <radius>0.05</radius>
         <length>0.1</length>
       </cylinder>
     </geometry>
   </collision>
   ```

2. **Disable unnecessary physics**:
   ```xml
   <link name="visual_only">
     <!-- Rendering only, no physics -->
     <inertial>
       <mass>0</mass>
     </inertial>
   </link>
   ```

3. **Run headless** (no visualization):
   ```bash
   gzserver humanoid.world  # No GUI = faster
   ```

4. **Increase physics timestep** (less accurate but faster):
   ```xml
   <max_step_size>0.002</max_step_size>  <!-- 2ms instead of 1ms -->
   ```

5. **Profile simulation**:
   ```bash
   # Gazebo Stats plugin shows performance metrics
   # Enable in GUI: Tools → Window → Physics
   ```

---

## Code Examples

### Example 1: Simple World File (4-simple-world.world)

Create a basic Gazebo world with humanoid robot:

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="humanoid_world">
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    <gravity>0 0 -9.81</gravity>

    <ambient_light>
      <color>0.5 0.5 0.5 1</color>
    </ambient_light>

    <light name="sun" type="directional">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>1 1 1 1</specular>
      <direction>-0.5 0.5 -1</direction>
      <cast_shadows>true</cast_shadows>
    </light>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

See complete code examples in:
- [4-simple-world.world](../../static/examples/module-2/chapter-4-gazebo/4-simple-world.world)
- [4-load-robot.py](../../static/examples/module-2/chapter-4-gazebo/4-load-robot.py)
- [4-joint-controller.py](../../static/examples/module-2/chapter-4-gazebo/4-joint-controller.py)
- [4-collision-demo.py](../../static/examples/module-2/chapter-4-gazebo/4-collision-demo.py)
- [4-physics-tuning.py](../../static/examples/module-2/chapter-4-gazebo/4-physics-tuning.py)

---

## Exercises

Complete the hands-on exercises to practice:

1. **[Exercise 4.1: Load & Simulate Humanoid Robot](../exercises/exercise-4-1/)** (Guided)
   - Install and verify Gazebo/ROS 2
   - Load humanoid.urdf in Gazebo
   - Verify ROS 2 topics publishing
   - Apply forces and observe physics
   - Estimated time: 2-3 hours

2. **[Exercise 4.2: Design Custom Robot World](../exercises/exercise-4-2/)** (Semi-open)
   - Create custom SDF world file
   - Define custom physics parameters
   - Load robot with obstacles
   - Implement safe joint limits
   - Estimated time: 4-5 hours

---

## Assessment

**[Quiz 4: Gazebo Physics](../assessments/quiz-4.md)** - Test your understanding

- 12 questions covering chapter concepts
- Passing score: ≥ 70% (9/12 correct)
- Estimated time: 15-20 minutes

---

## Key Takeaways

✅ **Gazebo Architecture**: Client-server model with physics engine, ROS 2 bridge, visualization

✅ **Physics Simulation**: ODE engine at 1000 Hz internal timestep, independent of visualization

✅ **URDF vs SDF**: URDF for robot structure, SDF adds physics/sensors/plugins

✅ **ROS 2 Integration**: `/joint_states` for feedback, `/*/cmd_pos` for control

✅ **Joint Control**: Implement PID loops, respect joint limits, handle feedback

✅ **Sensor Simulation**: Realistic noise modeling for training robust algorithms

✅ **Debugging**: Use ROS 2 tools, check topics, validate physics parameters

---

## Further Reading

- **[Gazebo 11 Documentation](https://classic.gazebosim.org/tutorials)** - Official tutorials
- **[ROS 2 Gazebo Integration](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html)** - ROS 2 guide
- **[ODE Physics Engine](http://opende.sourceforge.net/)** - Physics simulation details
- **[URDF Specification](http://wiki.ros.org/urdf/XML)** - Robot description format
- **[SDF Format](http://sdformat.org/)** - Simulation description format

---

## Glossary

| Term | Definition |
|------|-----------|
| **Gazebo** | Open-source physics simulation and rendering platform |
| **SDF** | Simulation Description Format, extends URDF with physics properties |
| **URDF** | Unified Robot Description Format, describes robot structure |
| **Physics Timestep** | Time interval for physics simulation (default 0.001s = 1000 Hz) |
| **Joint State** | Current position, velocity, effort of robot joints |
| **Collision Detection** | Process of identifying and computing contact forces between objects |
| **ROS 2 Bridge** | gazebo_ros plugins providing ROS 2 interface to Gazebo |
| **ODE** | Open Dynamics Engine, default physics engine |
| **Inertia** | Resistance to rotational acceleration, represented as 3×3 matrix |
| **Joint Limits** | Lower/upper position bounds and maximum velocity/effort for joint |

See [Module 2 Glossary](../glossary.md) for complete terminology.

---

## Citation

Open Robotics, "Gazebo Tutorials," *Gazebo Documentation*, [Online]. Available: https://classic.gazebosim.org/tutorials. [Accessed: Jan. 22, 2026].

Open Robotics, "ROS 2 Humble Documentation," *ROS 2*, [Online]. Available: https://docs.ros.org/en/humble/. [Accessed: Jan. 22, 2026].

---

**Chapter 4 Status**: ✅ **COMPLETE**

**Next Chapter**: [Chapter 5: High-Fidelity Rendering with Unity](chapter-5.md)

---

*Last Updated: 2026-01-22*
*Module: 002-digital-twin*
*Status: Ready for student use*
