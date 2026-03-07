# Exercise 4.2: Design Custom Robot World with Physics

**Difficulty**: Semi-open (design choices, rubric-based grading)
**Duration**: 4-5 hours
**Learning Outcomes**: Design realistic simulations, tune physics parameters, justify design decisions

---

## Exercise Overview

In this exercise, you will:

1. **Design a custom Gazebo world** - Create SDF file with obstacles, ground surface
2. **Define physics parameters** - Set gravity, friction, collision properties
3. **Load robot and apply forces** - Place humanoid in designed world, apply external forces
4. **Implement safety constraints** - Add joint limits to prevent collisions
5. **Document design decisions** - Explain physics tuning choices
6. **Validate simulation** - Test stability and realism

---

## Prerequisites

Before starting, you should have:

- ✅ Completed Exercise 4.1
- ✅ Read Chapter 4 thoroughly
- ✅ Understood SDF format (Section 2)
- ✅ Experimented with physics parameters using 4-physics-tuning.py
- ✅ Reviewed example worlds in 4-simple-world.world

---

## Design Requirements

### Functional Requirements

Your custom world MUST include:

1. **Ground Plane** - Flat surface at Z=0 (using plane geometry)
2. **Obstacles** - At least 3 objects (boxes, spheres, cylinders) at different heights
3. **Physics Parameters**:
   - Defined gravity (Earth-like: -9.81 m/s²)
   - Friction coefficient (realistic: 0.3-0.8)
   - Physics engine (ODE or Bullet)
   - Collision detection enabled
4. **Humanoid Robot** - Placed above ground (Z > 0.5m)
5. **Lighting** - Directional light for visibility
6. **Safety** - World must be stable (no physics explosions)

### Design Quality

Your design will be evaluated on:

- **Structure & Correctness** (40 points):
  - Valid SDF syntax (no parse errors)
  - Correct element hierarchy
  - Proper physics configuration
  - Realistic collision geometry
  - Clear code comments

- **Functionality** (30 points):
  - Simulation runs without crashes
  - Gravity effect is visible
  - Obstacles are reachable/observable
  - Robot can interact with environment
  - Joint limits prevent collision

- **Documentation** (30 points):
  - Design rationale explained
  - Physics parameter choices justified
  - Implementation notes for future changes
  - Lessons learned documented

---

## Step 1: Plan Your Design (30 minutes)

### 1.1 Sketch Your World

On paper or in a text file, sketch:

```
Top View:

  ┌─────────────────────────────┐
  │                             │
  │    Obstacle 1 (Box)         │
  │        ╔════╗               │
  │        ║    ║               │
  │        ╚════╝               │
  │                             │
  │    Humanoid          Obstacle 2  │
  │      ╔╗╔╗              ╭─╮   │
  │     ╔╝╚╝╚╗           ╰───╯   │
  │     ║ ⭐  ║       Obstacle 3  │
  │     ║     ║          ╔═════╗ │
  │     ╚═╤═══╝          ║     ║ │
  │       │              ╚═════╝ │
  │   Ground Plane               │
  │   (friction: 0.7)            │
  └─────────────────────────────┘
```

### 1.2 Physics Design Decisions

Choose answers for:

**Gravity**:
- [ ] Earth (9.81 m/s²) - realistic
- [ ] Moon (1.62 m/s²) - bouncy
- [ ] Mars (3.71 m/s²) - medium

**Friction**:
- [ ] Low (0.2) - icy/slippery
- [ ] Medium (0.5) - concrete
- [ ] High (0.8) - rubber

**Physics Engine**:
- [ ] ODE - stable, standard
- [ ] Bullet - faster, less stable

**Timestep**:
- [ ] 0.001s (1000 Hz) - very accurate
- [ ] 0.002s (500 Hz) - moderate
- [ ] 0.005s (200 Hz) - fast but rough

---

## Step 2: Create Custom SDF World (90 minutes)

### 2.1 Start with Template

Create `my_custom_world.sdf`:

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="custom_humanoid_world">

    <!-- Physics configuration -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Gravity and lighting -->
    <gravity>0 0 -9.81</gravity>
    <ambient_light><color>0.5 0.5 0.5 1</color></ambient_light>

    <!-- TODO: Add light, ground plane, obstacles, humanoid -->

  </world>
</sdf>
```

### 2.2 Design Your Obstacles

Add 3+ obstacles with different properties:

```xml
<!-- Obstacle 1: Wooden Box (movable) -->
<model name="wooden_box">
  <pose>2 0 0.5 0 0 0</pose>  <!-- Position: x=2, y=0, z=0.5 -->
  <link name="link">
    <inertial>
      <mass>1.0</mass>  <!-- 1 kg -->
      <inertia>
        <ixx>0.01</ixx>
        <iyy>0.01</iyy>
        <izz>0.01</izz>
      </inertia>
    </inertial>

    <visual name="visual">
      <geometry>
        <box><size>0.1 0.1 0.1</size></box>
      </geometry>
      <material>
        <script>
          <uri>file://media/materials/scripts/gazebo.material</uri>
          <name>Gazebo/Wood</name>
        </script>
      </material>
    </visual>

    <collision name="collision">
      <geometry>
        <box><size>0.1 0.1 0.1</size></box>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.5</mu>
            <mu2>0.5</mu2>
          </ode>
        </friction>
      </surface>
    </collision>
  </link>
</model>

<!-- Obstacle 2: Metal Sphere (rolls) -->
<model name="metal_sphere">
  <pose>-2 0 1.0 0 0 0</pose>
  <link name="link">
    <inertial>
      <mass>2.0</mass>
      <inertia>
        <ixx>0.004</ixx>
        <iyy>0.004</iyy>
        <izz>0.004</izz>
      </inertia>
    </inertial>

    <visual name="visual">
      <geometry>
        <sphere><radius>0.05</radius></sphere>
      </geometry>
      <material>
        <script>
          <uri>file://media/materials/scripts/gazebo.material</uri>
          <name>Gazebo/Chrome</name>
        </script>
      </material>
    </visual>

    <collision name="collision">
      <geometry>
        <sphere><radius>0.05</radius></sphere>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.1</mu>      <!-- Low friction (rolls easily) -->
            <mu2>0.1</mu2>
          </ode>
        </friction>
      </surface>
    </collision>
  </link>
</model>

<!-- Obstacle 3: Cylinder (tall object) -->
<model name="concrete_cylinder">
  <pose>0 2 0.5 0 0 0</pose>
  <link name="link">
    <inertial>
      <mass>3.0</mass>
      <inertia>
        <ixx>0.05</ixx>
        <iyy>0.05</iyy>
        <izz>0.01</izz>
      </inertia>
    </inertial>

    <visual name="visual">
      <geometry>
        <cylinder>
          <radius>0.05</radius>
          <length>1.0</length>
        </cylinder>
      </geometry>
      <material>
        <script>
          <uri>file://media/materials/scripts/gazebo.material</uri>
          <name>Gazebo/Grey</name>
        </script>
      </material>
    </visual>

    <collision name="collision">
      <geometry>
        <cylinder>
          <radius>0.05</radius>
          <length>1.0</length>
        </cylinder>
      </geometry>
    </collision>
  </link>
</model>
```

### 2.3 Load Humanoid Robot

```xml
<!-- Humanoid Robot -->
<model name="humanoid">
  <include>
    <uri>file://./humanoid.sdf</uri>  <!-- Must have humanoid.sdf file -->
    <pose>0 0 1.0 0 0 0</pose>  <!-- Position above obstacles -->
  </include>
</model>
```

### 2.4 Add Lighting and Ground

```xml
<!-- Directional Light (Sun) -->
<light name="sun" type="directional">
  <pose>0 0 10 0 0 0</pose>
  <diffuse>0.8 0.8 0.8 1</diffuse>
  <specular>0.9 0.9 0.9 1</specular>
  <direction>-0.5 0.5 -1</direction>
  <cast_shadows>true</cast_shadows>
</light>

<!-- Ground Plane -->
<model name="ground_plane">
  <static>true</static>
  <link name="link">
    <collision name="collision">
      <geometry>
        <plane><normal>0 0 1</normal><size>100 100</size></plane>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>0.7</mu>      <!-- Rubber-on-concrete -->
            <mu2>0.7</mu2>
          </ode>
        </friction>
      </surface>
    </collision>

    <visual name="visual">
      <geometry>
        <plane><normal>0 0 1</normal><size>100 100</size></plane>
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
```

---

## Step 3: Implement Safety Constraints (45 minutes)

### 3.1 Create Safety Controller

Create `safety_controller.py`:

```python
#!/usr/bin/env python3
"""
Safety controller to prevent robot joint collisions.

Reads /joint_states and enforces limits to prevent:
- Self-collision
- Collision with obstacles
- Joint overextension
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class SafetyController(Node):
    def __init__(self):
        super().__init__('safety_controller')

        # Define safe limits for each joint (in radians)
        # Adjust based on your obstacles
        self.joint_limits = {
            'shoulder_left': [-0.5, 1.5],     # rad
            'shoulder_right': [-1.5, 0.5],
            'hip_left': [-0.8, 0.8],
            'hip_right': [-0.8, 0.8],
        }

        # Subscribe to joint states
        self.create_subscription(JointState, '/joint_states', self.callback, 10)

        # Publish safe commands
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/gazebo/humanoid/cmd_pos', 10)

    def callback(self, msg: JointState):
        """Enforce joint limits on incoming state."""
        safe_positions = []

        for i, name in enumerate(msg.name):
            if name in self.joint_limits:
                limits = self.joint_limits[name]
                pos = msg.position[i]

                # Clamp to limits
                safe_pos = max(limits[0], min(limits[1], pos))
                safe_positions.append(safe_pos)

        # Publish safe commands
        cmd_msg = Float64MultiArray()
        cmd_msg.data = safe_positions
        self.cmd_pub.publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    controller = SafetyController()
    rclpy.spin(controller)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3.2 Test Safety Controller

```bash
# In one terminal
gzserver my_custom_world.sdf

# In another
python3 4-joint-controller.py

# In third
python3 safety_controller.py
```

**Verify**: Robot joints don't exceed safe limits.

---

## Step 4: Document Your Design (45 minutes)

### 4.1 Design Rationale Document

Create `DESIGN.md`:

```markdown
# Custom World Design Rationale

## Physics Parameters

### Gravity: 9.81 m/s² (Earth)
**Justification**: Realistic simulation matching real-world conditions

**Alternatives Considered**:
- Moon gravity (1.62): Too bouncy for physics testing
- Mars gravity (3.71): Unnecessarily exotic

### Friction: 0.7
**Justification**: Rubber on concrete, realistic for robot locomotion

**Effect**: Objects don't slide easily, emphasizing gravity and inertia

### Physics Engine: ODE
**Justification**: Better stability than Bullet, industry standard

### Timestep: 0.001s
**Justification**: Accurate simulation for control algorithms

**Trade-off**: Slower than 0.002s but necessary for safety testing

## Obstacle Design

### Obstacle 1 (Wooden Box)
- Mass: 1.0 kg
- Friction: 0.5 (medium)
- Position: (2, 0, 0.5)
- Purpose: Testcase for robot interaction

### Obstacle 2 (Metal Sphere)
- Mass: 2.0 kg
- Friction: 0.1 (low, rolls)
- Position: (-2, 0, 1.0)
- Purpose: Test collision with moving object

### Obstacle 3 (Concrete Cylinder)
- Mass: 3.0 kg
- Friction: 0.5 (medium)
- Position: (0, 2, 0.5)
- Purpose: Tall obstacle for arm interaction

## Safety Constraints

Joint limits (radians):
- Shoulder: [-0.5, 1.5] ← prevents overextension
- Hip: [-0.8, 0.8] ← prevents self-collision

## Lessons Learned

1. Physics timestep below 0.001s makes simulation very slow
2. Friction > 0.8 causes objects to get stuck
3. Light obstacles (< 0.5 kg) can be pushed by robot
4. Tall obstacles help test arm reach

## Future Improvements

- Add wall boundaries
- Implement sensor feedback
- Add more complex obstacles
- Test with different gravity values
```

### 4.2 Implementation Notes

Create `IMPLEMENTATION_NOTES.md`:

```markdown
# Implementation Notes

## Successful Elements
✅ SDF syntax valid (validated with: `gz sdf my_custom_world.sdf`)
✅ Physics stable (no explosions or instability)
✅ Obstacles properly collide with ground and robot
✅ Gravity effect clearly visible

## Challenges & Solutions

### Challenge: Objects falling through ground
**Solution**: Added proper collision geometry to all models

### Challenge: Physics instability
**Solution**: Increased solver iterations from 20 to 50

### Challenge: Friction too high
**Solution**: Adjusted from 0.9 to 0.7

## Commands to Run

```bash
# Launch with Gazebo GUI
gzserver --verbose my_custom_world.sdf
gzclient

# Load robot
python3 4-load-robot.py --urdf humanoid.urdf --name humanoid

# Test control
python3 4-joint-controller.py

# Monitor collisions
python3 4-collision-demo.py
```

## Performance

- FPS: 60 (acceptable)
- Physics time: 1.2ms (1000 Hz)
- Latency: `<50ms`
```

---

## Step 5: Validate Your Simulation (30 minutes)

### 5.1 Test Stability

```bash
# Run for 30 seconds without errors
gzserver my_custom_world.sdf &
sleep 30
pkill gzserver
```

**Check**: No instability, objects stay in reasonable positions.

### 5.2 Visual Verification

With Gazebo GUI:

```bash
gzserver my_custom_world.sdf
gzclient
```

**Verify**:
- [ ] Ground plane visible
- [ ] All 3 obstacles visible
- [ ] Lighting visible (not dark)
- [ ] Humanoid appears above obstacles
- [ ] No physics errors in console

### 5.3 Collision Testing

```bash
# Load robot and test collisions
python3 4-load-robot.py --urdf humanoid.urdf
python3 4-collision-demo.py

# Move robot to test obstacles
# Watch for collision events
```

---

## Submission Requirements

Prepare and submit:

1. **`my_custom_world.sdf`** - Your custom world file
2. **`DESIGN.md`** - Design rationale (45+ points)
3. **`IMPLEMENTATION_NOTES.md`** - Implementation details
4. **`safety_controller.py`** - Safety constraint enforcement
5. **Screenshots** (optional but helpful):
   - Gazebo view with all obstacles
   - Console output showing successful load
   - Physics measurements

---

## Grading Rubric

### Structure & Correctness (40 points)

| Criterion | Points | Your Score |
|-----------|--------|------------|
| SDF syntax valid | 10 | ___ |
| Physics configuration correct | 10 | ___ |
| 3+ obstacles properly defined | 10 | ___ |
| Proper comments & documentation | 10 | ___ |
| **Total** | **40** | **___** |

### Functionality (30 points)

| Criterion | Points | Your Score |
|-----------|--------|------------|
| Simulation runs without errors | 10 | ___ |
| Robot loads and functions | 10 | ___ |
| Gravity/collisions working | 10 | ___ |
| **Total** | **30** | **___** |

### Documentation (30 points)

| Criterion | Points | Your Score |
|-----------|--------|------------|
| Design rationale clear | 10 | ___ |
| Physics choices justified | 10 | ___ |
| Implementation notes complete | 10 | ___ |
| **Total** | **30** | **___** |

**Grand Total: _____ / 100**

---

## Debugging Tips

- **Physics explosion**: Reduce timestep or increase solver iterations
- **Objects stuck**: Lower friction coefficient
- **Performance slow**: Increase timestep or simplify collision geometry
- **SDF parse error**: Use `gz sdf my_custom_world.sdf` to validate

---

## Resources

- [Gazebo SDF Tutorial](https://classic.gazebosim.org/tutorials?tut=build_world)
- [Chapter 4: URDF & SDF](../../chapter-4.md#section-2-urdf--sdf)
- [4-physics-tuning.py](../../../static/examples/module-2/chapter-4-gazebo/4-physics-tuning.py)

---

**Exercise Status**: ✅ **Ready to Start**

**Date**: 2026-01-22
**Duration**: 4-5 hours
**Difficulty**: Semi-open (design + engineering)
