# Chapter 3: URDF & Robot Description - Links, Joints, and Humanoid Robots

## Learning Objectives

By the end of this chapter, you will:

- ✅ Understand URDF (Unified Robot Description Format) and XML syntax
- ✅ Define robot links (rigid bodies with geometry and inertia)
- ✅ Define robot joints (revolute, prismatic, fixed) and their constraints
- ✅ Understand kinematic chains and reference frames
- ✅ Write URDF descriptions for humanoid robots
- ✅ Visualize robots in RViz2
- ✅ Validate URDF syntax and structure
- ✅ Understand the path from URDF to simulation and control

**Estimated time**: 10-12 hours
**Difficulty**: Intermediate
**Prerequisites**: Chapter 1 (Basic ROS 2), understanding of coordinate frames and kinematics

---

## 1. What is URDF?

### The Robot Description Problem

How do you describe a robot to software?

```
Human description: "A robot with a torso, two arms, and two legs"

Computer needs:
- What is the 3D geometry of each part?
- How much does each part weigh?
- How are parts connected?
- How can parts move (joints)?
- Where are sensors mounted?
- What are the coordinate frames?
```

**URDF** (Unified Robot Description Format) solves this with an XML-based specification.

### What is URDF?

URDF is an **XML format** that describes:
- **Links**: Rigid bodies (torso, arm, leg) with geometry and inertia
- **Joints**: Connections between links (how they move)
- **Frames**: Coordinate systems for each link
- **Geometry**: 3D shapes (boxes, cylinders, meshes) for visualization and collision detection
- **Inertia**: Mass and mass distribution (rotational properties)

### URDF vs. Other Formats

| Format | Use | Pros | Cons |
|--------|-----|------|------|
| **URDF** | ROS 2 robot description | Human-readable XML, standard in ROS | Limited collision shapes |
| **STEP/CAD** | Detailed mechanical design | Precise geometry | Not robot-specific |
| **SDF** | Gazebo simulation | More detailed than URDF | More complex |
| **Mesh files** | Detailed geometry | Can import from CAD | Raw geometry only |

**Most common**: URDF for ROS 2 description; CAD/mesh for geometry; SDF for Gazebo simulation.

### Use Cases

- **RViz2 visualization**: See your robot structure
- **TF (Transform Framework)**: Track coordinate frames
- **Motion planning**: Collision checking, joint limits
- **Control**: Understanding kinematic structure
- **Simulation**: Importing to Gazebo

---

## 2. URDF Components: Links

### What is a Link?

A **link** is a rigid body (no internal motion) with:
- **Name**: Unique identifier
- **Geometry**: Visual representation (for viewing in RViz2)
- **Collision**: Collision geometry (for planning)
- **Inertia**: Mass and moment of inertia

### Link XML Structure

```xml
<link name="torso">
  <!-- Visual representation (what you see in RViz2) -->
  <visual>
    <geometry>
      <box size="0.3 0.2 0.5"/>
    </geometry>
    <origin xyz="0 0 0.25" rpy="0 0 0"/>
    <material name="torso_color">
      <color rgba="1 0 0 1"/>  <!-- RGBA: red, opaque -->
    </material>
  </visual>

  <!-- Collision geometry (for planning) -->
  <collision>
    <geometry>
      <box size="0.3 0.2 0.5"/>
    </geometry>
    <origin xyz="0 0 0.25" rpy="0 0 0"/>
  </collision>

  <!-- Physical properties -->
  <inertial>
    <mass value="5.0"/>  <!-- 5 kg -->
    <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.05"/>
  </inertial>
</link>
```

### Geometry Shapes

**Primitive Shapes** (simple, fast):

```xml
<!-- Box (rectangular) -->
<geometry>
  <box size="width height depth"/>
</geometry>

<!-- Cylinder (useful for joints, limbs) -->
<geometry>
  <cylinder radius="0.05" length="0.3"/>
</geometry>

<!-- Sphere (for heads, end-effectors) -->
<geometry>
  <sphere radius="0.1"/>
</geometry>
```

**Mesh** (detailed, imported from CAD):

```xml
<!-- Load from STL or DAE file -->
<geometry>
  <mesh filename="file:///path/to/model.stl" scale="0.001 0.001 0.001"/>
</geometry>
```

### Origin (Position and Orientation)

Links and geometry have **origin** (offset from parent):

```xml
<origin xyz="x y z" rpy="roll pitch yaw"/>
```

- **xyz**: Position offset in meters (x, y, z)
- **rpy**: Rotation in radians (roll, pitch, yaw)

Example: Offset torso 0.5m above ground:
```xml
<origin xyz="0 0 0.5" rpy="0 0 0"/>
```

### Complete Simple Link Example

```xml
<link name="left_arm">
  <visual>
    <geometry>
      <cylinder radius="0.04" length="0.4"/>
    </geometry>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <material name="arm_color">
      <color rgba="0.8 0.8 0.8 1"/>
    </material>
  </visual>

  <collision>
    <geometry>
      <cylinder radius="0.04" length="0.4"/>
    </geometry>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
  </collision>

  <inertial>
    <mass value="1.5"/>
    <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.001"/>
  </inertial>
</link>
```

---

## 3. URDF Components: Joints

### What is a Joint?

A **joint** connects two links and defines how they move:
- **Parent**: Link being connected from
- **Child**: Link being connected to
- **Type**: How the joint moves (revolute, prismatic, fixed, etc.)
- **Limits**: Position and velocity constraints
- **Axis**: Direction of motion (x, y, or z)

### Joint Types

#### Revolute Joint (Rotational)

Rotates around an axis with limits:

```xml
<joint name="shoulder_joint" type="revolute">
  <parent link="torso"/>
  <child link="left_arm"/>
  <origin xyz="0.1 0.15 0.4" rpy="0 0 0"/>

  <!-- Axis of rotation (unit vector) -->
  <axis xyz="0 1 0"/>  <!-- Rotate around Y-axis -->

  <!-- Limits: min/max angle, max velocity, max effort/torque -->
  <limit lower="-1.57" upper="1.57" velocity="2.0" effort="10"/>

  <!-- Friction/damping -->
  <dynamics damping="0.1" friction="0.0"/>
</joint>
```

**Common limits**:
- `lower="-1.57" upper="1.57"`: ±90 degrees
- `lower="0" upper="3.14"`: 0-180 degrees
- `velocity="2.0"`: Max 2 rad/s
- `effort="10"`: Max 10 N⋅m torque

#### Prismatic Joint (Linear)

Slides along an axis:

```xml
<joint name="elevator_joint" type="prismatic">
  <parent link="base"/>
  <child link="lift_platform"/>
  <origin xyz="0 0 0" rpy="0 0 0"/>

  <!-- Axis of motion -->
  <axis xyz="0 0 1"/>  <!-- Move along Z-axis (up/down) -->

  <!-- Linear limits: min/max distance -->
  <limit lower="0" upper="1.0" velocity="0.5" effort="100"/>
</joint>
```

#### Fixed Joint

No motion - permanently connects two links:

```xml
<joint name="camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>
```

### Joint Axes

```xml
<!-- Common axes -->
<axis xyz="1 0 0"/>  <!-- X-axis (pitch for forward/backward) -->
<axis xyz="0 1 0"/>  <!-- Y-axis (roll for left/right tilt) -->
<axis xyz="0 0 1"/>  <!-- Z-axis (yaw for rotation) -->
```

---

## 4. Humanoid Robot Anatomy

### Humanoid Structure

A basic humanoid robot has:

```
        [Head]
          |
       [Torso]
       /    \
    [L Arm] [R Arm]
      /|      \|
     [Elbow]  [Elbow]
      /        \
    [L Leg]  [R Leg]
    /   \    /   \
[Knee] [Hip][Hip] [Knee]
  /       \   /      \
[Ankle]  [Ankle] [Ankle] [Ankle]
```

### Typical Humanoid Joints

| Joint | Parent | Child | Type | Axis | Range | Purpose |
|-------|--------|-------|------|------|-------|---------|
| Neck | Torso | Head | Revolute | Z | ±π/2 | Look around |
| Shoulder L | Torso | Arm L | Revolute | Y | ±π | Raise/lower arm |
| Elbow L | Arm L | Forearm L | Revolute | Y | 0 to π | Bend arm |
| Hip L | Torso | Leg L | Revolute | X | ±π/4 | Move leg forward/back |
| Knee L | Leg L | Shin L | Revolute | Y | 0 to π | Bend knee |
| Ankle L | Shin L | Foot L | Revolute | X | ±π/6 | Tilt foot |

### Simple Humanoid URDF Example

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">

  <!-- BASE LINK (World reference) -->
  <link name="world"/>

  <!-- TORSO -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <material name="torso_color">
        <color rgba="1 0 0 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.05"/>
    </inertial>
  </link>

  <!-- Connect base to torso -->
  <joint name="base_torso_joint" type="fixed">
    <parent link="world"/>
    <child link="torso"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <!-- LEFT ARM -->
  <link name="left_arm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.4"/>
      </geometry>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <material name="arm_color">
        <color rgba="0.8 0.8 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.4"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Shoulder joint (left) -->
  <joint name="left_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="left_arm"/>
    <origin xyz="0.15 0.15 0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" velocity="2.0" effort="10"/>
    <dynamics damping="0.1" friction="0.0"/>
  </joint>

  <!-- RIGHT ARM -->
  <link name="right_arm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.4"/>
      </geometry>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <material name="arm_color">
        <color rgba="0.8 0.8 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.4"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <!-- Shoulder joint (right) -->
  <joint name="right_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="right_arm"/>
    <origin xyz="-0.15 0.15 0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" velocity="2.0" effort="10"/>
    <dynamics damping="0.1" friction="0.0"/>
  </joint>

  <!-- LEFT LEG -->
  <link name="left_leg">
    <visual>
      <geometry>
        <box size="0.1 0.1 0.5"/>
      </geometry>
      <origin xyz="0 0 -0.25" rpy="0 0 0"/>
      <material name="leg_color">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.1 0.1 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Hip joint (left) -->
  <joint name="left_hip" type="revolute">
    <parent link="torso"/>
    <child link="left_leg"/>
    <origin xyz="0.1 0.05 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.785" upper="0.785" velocity="1.5" effort="15"/>
    <dynamics damping="0.1" friction="0.0"/>
  </joint>

  <!-- RIGHT LEG -->
  <link name="right_leg">
    <visual>
      <geometry>
        <box size="0.1 0.1 0.5"/>
      </geometry>
      <origin xyz="0 0 -0.25" rpy="0 0 0"/>
      <material name="leg_color">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.1 0.1 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Hip joint (right) -->
  <joint name="right_hip" type="revolute">
    <parent link="torso"/>
    <child link="right_leg"/>
    <origin xyz="-0.1 0.05 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.785" upper="0.785" velocity="1.5" effort="15"/>
    <dynamics damping="0.1" friction="0.0"/>
  </joint>

</robot>
```

---

## 5. Visualization in RViz2

### Loading and Viewing URDF

Once you have a URDF file, visualize it in RViz2:

```bash
# Method 1: Direct URDF loading (simple)
rviz2 -d $(ros2 pkg prefix rviz2)/share/rviz2/config/default.rviz

# Then File → Open URDF → select your file
```

### Launch File for URDF Visualization

```xml
<!-- urdf_viz_launch.xml -->
<launch>
  <!-- Load URDF from file -->
  <arg name="urdf_file" default="$(find my_package)/urdf/humanoid.urdf"/>

  <!-- Read and publish URDF -->
  <param name="robot_description" command="cat $(var urdf_file)"/>

  <!-- Start RViz2 -->
  <node pkg="rviz2" exec="rviz2" name="rviz2" output="screen">
    <param name="display_config" value="$(find my_package)/config/display.rviz"/>
  </node>

  <!-- Publish fixed transform (required for RViz2) -->
  <node pkg="tf2_ros" exec="static_transform_publisher" args="0 0 0 0 0 0 world torso"/>

  <!-- Publish robot state (optional - for animation) -->
  <node pkg="robot_state_publisher" exec="robot_state_publisher" output="screen">
    <param name="robot_description" value="$(command cat $(var urdf_file))"/>
  </node>
</launch>
```

Run with:
```bash
ros2 launch my_package urdf_viz_launch.xml urdf_file:=path/to/humanoid.urdf
```

### Transform (TF) Frames

URDF defines a **transform tree** - the hierarchy of coordinate frames:

```
world (global reference)
  ├─ torso
  ├─ left_arm
  ├─ right_arm
  ├─ left_leg
  └─ right_leg
```

Use `ros2 run tf2_tools view_frames` to visualize the tree.

---

## 6. Validating URDF

### Common URDF Errors

**1. XML Syntax Error**:
```xml
<link name="torso">
  <!-- Missing closing tag -->
  <visual>
```

**Error message**: XML parsing failed

**2. Undefined Link Reference**:
```xml
<joint name="shoulder">
  <parent link="torso"/>
  <child link="nonexistent_arm"/>  <!-- This link doesn't exist -->
</joint>
```

**3. Cyclic Dependency**:
```xml
A → B → A  <!-- Creates a loop -->
```

### Validation Tools

**Python URDF Parser** (catches syntax errors):
```python
from urdf_parser_py.urdf import URDF

# Load and parse URDF
robot = URDF.from_file('humanoid.urdf')

# Access elements
for joint in robot.joints:
    print(f'Joint: {joint.name}, Type: {joint.type}')

for link in robot.links:
    print(f'Link: {link.name}')
```

**ROS 2 Validation**:
```bash
# Check URDF syntax
python3 -c "from urdf_parser_py.urdf import URDF; URDF.from_file('humanoid.urdf')"

# No output = valid; error message = invalid
```

---

## 7. From URDF to Simulation (Preview)

### Next Steps: Gazebo Simulation

With a working URDF, you can import it into **Gazebo** (physics simulator):

```xml
<!-- Additional Gazebo-specific elements needed -->
<gazebo reference="torso">
  <material>Gazebo/Red</material>
  <mu1>0.8</mu1>
  <mu2>0.8</mu2>
</gazebo>
```

Topics available in Gazebo:
- `/gazebo/model_states`: Position of all objects
- `/joint_states`: Joint positions and velocities
- `/cmd_vel`: Send velocity commands

### From URDF to Simulation Pipeline

```
Your URDF  →  RViz2 (Visualization)
     ↓
Add physics ←→ Gazebo (Simulation)
     ↓
Add controllers ←→ Joint controllers + sensors
     ↓
Your robot simulation is ready for AI/ML
```

---

## 8. Complete Extended Humanoid Example

```xml
<?xml version="1.0"?>
<robot name="extended_humanoid">

  <!-- TORSO + HEAD -->
  <link name="world"/>
  <link name="torso">
    <visual>
      <geometry><box size="0.3 0.2 0.5"/></geometry>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <material name="red"><color rgba="1 0 0 0.8"/></material>
    </visual>
    <collision>
      <geometry><box size="0.3 0.2 0.5"/></geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="base_torso" type="fixed">
    <parent link="world"/>
    <child link="torso"/>
  </joint>

  <link name="head">
    <visual>
      <geometry><sphere radius="0.1"/></geometry>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <material name="skin"><color rgba="1 0.8 0.6 1"/></material>
    </visual>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="neck" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" velocity="2.0" effort="5"/>
  </joint>

  <!-- ARMS WITH MULTIPLE JOINTS -->
  <link name="left_upper_arm">
    <visual>
      <geometry><cylinder radius="0.035" length="0.4"/></geometry>
      <origin xyz="0 0 -0.2" rpy="0 0 0"/>
      <material name="gray"><color rgba="0.8 0.8 0.8 1"/></material>
    </visual>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="left_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.15 0.15 0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" velocity="2.0" effort="10"/>
  </joint>

  <link name="left_forearm">
    <visual>
      <geometry><cylinder radius="0.03" length="0.35"/></geometry>
      <origin xyz="0 0 -0.175" rpy="0 0 0"/>
      <material name="gray"><color rgba="0.8 0.8 0.8 1"/></material>
    </visual>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.0005"/>
    </inertial>
  </link>

  <joint name="left_elbow" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_forearm"/>
    <origin xyz="0 0 -0.4" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="3.14" velocity="2.0" effort="8"/>
  </joint>

  <!-- RIGHT ARM (symmetric) -->
  <!-- ... similar structure mirrored across Y axis ... -->

  <!-- LEGS WITH MULTIPLE JOINTS -->
  <link name="left_thigh">
    <visual>
      <geometry><box size="0.12 0.12 0.5"/></geometry>
      <origin xyz="0 0 -0.25" rpy="0 0 0"/>
      <material name="dark_gray"><color rgba="0.3 0.3 0.3 1"/></material>
    </visual>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.08" ixy="0" ixz="0" iyy="0.08" iyz="0" izz="0.02"/>
    </inertial>
  </link>

  <joint name="left_hip" type="revolute">
    <parent link="torso"/>
    <child link="left_thigh"/>
    <origin xyz="0.1 0.05 0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.785" upper="0.785" velocity="1.5" effort="20"/>
  </joint>

  <link name="left_calf">
    <visual>
      <geometry><box size="0.1 0.1 0.45"/></geometry>
      <origin xyz="0 0 -0.225" rpy="0 0 0"/>
      <material name="dark_gray"><color rgba="0.3 0.3 0.3 1"/></material>
    </visual>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="left_knee" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_calf"/>
    <origin xyz="0 0 -0.5" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="2.35" velocity="2.0" effort="15"/>
  </joint>

  <!-- RIGHT LEG (symmetric) -->
  <!-- ... similar structure mirrored across Y axis ... -->

</robot>
```

---

## Summary

| Concept | Purpose | Example |
|---------|---------|---------|
| **Link** | Rigid body in robot | Torso, arm, leg |
| **Joint** | Connection between links | Shoulder, elbow, hip |
| **Geometry** | 3D shape (visual + collision) | Box, cylinder, sphere, mesh |
| **Inertia** | Mass and mass distribution | ixx, iyy, izz values |
| **Origin** | Position and orientation offset | xyz="0 0 0.5" rpy="0 0 0" |
| **Axis** | Direction of joint motion | xyz="0 1 0" (Y-axis rotation) |
| **Limits** | Joint constraints | lower="-1.57" upper="1.57" |
| **Transform** | Coordinate frame tree | World → Torso → Arm → Forearm |

---

## Key Takeaways

1. **URDF is XML**: Human-readable, version-controllable, standard in ROS 2
2. **Links and Joints**: Two core elements - every robot part and motion
3. **Coordinate frames matter**: Careful with xyz/rpy offsets to avoid visualization errors
4. **Humanoid robots**: Typically 10-20 links and 9-15 joints; scale up from simple to complex
5. **Always visualize**: RViz2 helps catch URDF errors immediately
6. **Validation first**: Use Python parser to catch syntax errors before simulation

---

## Next Steps

- Write a simple 2-DOF robot URDF from scratch
- Load your URDF in RViz2 and verify it looks correct
- Extend your humanoid with additional joints (wrists, ankles)
- Proceed to Exercise 3.1: Write Basic URDF

---

## Glossary References

- **Link**: See [Glossary: Link](./glossary.md#link)
- **Joint**: See [Glossary: Joint](./glossary.md#joint)
- **URDF**: See [Glossary: URDF](./glossary.md#urdf)
- **Transform**: See [Glossary: Transform](./glossary.md#transform)
- **Inertia**: See [Glossary: Inertia](./glossary.md#inertia)

---

**Citation**: ROS Industrial. "URDF Tutorial." *ROS 2 Documentation*, Jan. 2026. [Online]. Available: https://docs.ros.org/en/humble/Tutorials/URDF/URDF-Main.html. [Accessed: Jan. 22, 2026].

Willow Garage. "URDF Specification." *ROS Documentation*, Jan. 2026. [Online]. Available: http://wiki.ros.org/urdf/XML/robot. [Accessed: Jan. 22, 2026].

---

*Chapter 3: URDF & Robot Description* | Version 1.0.0 | Module 1 - ROS 2 Fundamentals
