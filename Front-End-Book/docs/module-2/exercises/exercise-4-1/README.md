# Exercise 4.1: Load & Simulate Humanoid Robot in Gazebo

**Difficulty**: Guided (step-by-step instructions)
**Duration**: 2-3 hours
**Learning Outcomes**: Load URDF in Gazebo, control via ROS 2, observe physics behavior

---

## Exercise Overview

In this exercise, you will:

1. **Set up the simulation environment** - Verify Gazebo and ROS 2 are installed
2. **Load a humanoid robot** - Use ROS 2 services to spawn robot in Gazebo
3. **Verify ROS 2 integration** - Check that `/joint_states` topic is publishing
4. **Control the robot** - Apply sinusoidal joint commands via ROS 2
5. **Observe physics** - Watch gravity and collisions in action
6. **Measure performance** - Check simulation FPS and latency

---

## Prerequisites

Before starting, verify you have:

- ✅ Ubuntu 22.04 LTS (or equivalent)
- ✅ ROS 2 Humble installed and sourced
- ✅ Gazebo 11+ installed
- ✅ Chapter 4 content read
- ✅ Quiz 4 passed (≥70%)
- ✅ Code examples reviewed (4-simple-world.world, 4-load-robot.py, etc.)

---

## Step 1: Environment Setup (15 minutes)

### 1.1 Verify Installation

Open a terminal and run:

```bash
# Check ROS 2
ros2 --version
# Expected: ROS 2 Humble ...

# Check Gazebo
gazebo --version
# Expected: Gazebo version 11.x.x

# Check gazebo_ros integration
ros2 pkg list | grep gazebo_ros
# Expected: gazebo_ros (and related packages)

# Check Python 3
python3 --version
# Expected: Python 3.10+
```

**Troubleshooting**:
- If Gazebo not found: `sudo apt install gazebo11 libgazebo11-dev`
- If gazebo_ros not found: `sudo apt install ros-humble-gazebo-ros-pkgs`

### 1.2 Set up Working Directory

```bash
# Create workspace
mkdir -p ~/module2_ex4_1
cd ~/module2_ex4_1

# Copy example files from chapter
cp /path/to/chapter-4-gazebo/4-*.py .
cp /path/to/chapter-4-gazebo/4-*.world .

# Make Python scripts executable
chmod +x 4-*.py
```

---

## Step 2: Start Gazebo & Load Robot (30 minutes)

### 2.1 Launch Gazebo Server

**Terminal 1** - Start physics simulation:

```bash
source /opt/ros/humble/setup.bash
cd ~/module2_ex4_1

# Start Gazebo server (headless, just physics)
gzserver --verbose 4-simple-world.world
```

**Expected output**:
```
[Msg] Loaded as XML from [...]
[Msg] Factory plugin loaded
...
```

### 2.2 Launch Gazebo Client (Optional)

**Terminal 2** - Start visualization (optional, helpful for debugging):

```bash
source /opt/ros/humble/setup.bash

# In another terminal on same machine, start client
gzclient
```

**Expected**: Gazebo window opens showing empty world with ground plane.

### 2.3 Spawn Humanoid Robot

**Terminal 3** - Load robot into simulation:

```bash
source /opt/ros/humble/setup.bash
cd ~/module2_ex4_1

# Run robot loader
python3 4-load-robot.py --urdf humanoid.urdf --name humanoid --z 1.0 --verify
```

**Expected output**:
```
✅ Service available: /spawn_entity
📄 Loading URDF: humanoid.urdf
✅ URDF loaded (2434 bytes)
🤖 Spawning robot 'humanoid' at (0.00, 0.00, 1.00)
✅ Robot spawned successfully: humanoid
✅ Joint states received! Joints: ['shoulder_left', 'shoulder_right', ...]
```

**In Gazebo client** (if open): Humanoid robot should appear above ground.

---

## Step 3: Verify ROS 2 Integration (15 minutes)

### 3.1 Check Topics

**Terminal 4** - List ROS 2 topics:

```bash
ros2 topic list | grep -E "(gazebo|joint)"
```

**Expected output**:
```
/gazebo/link_states
/gazebo/model_states
/gazebo/set_entity_state
/joint_states
/tf
/tf_static
```

### 3.2 Monitor Joint States

**Terminal 4** - Echo joint state messages:

```bash
ros2 topic echo /joint_states --once
```

**Expected output**:
```
header:
  stamp:
    sec: 123
    nsec: 456789012
  frame_id: ''
name:
- shoulder_left
- shoulder_right
- hip_left
- hip_right
position: [0.0, 0.0, 0.0, 0.0]
velocity: [0.0, 0.0, 0.0, 0.0]
effort: [0.0, 0.0, 0.0, 0.0]
```

### 3.3 Measure Publishing Rate

```bash
ros2 topic hz /joint_states
```

**Expected**: ~50 Hz publishing rate

---

## Step 4: Control the Robot (45 minutes)

### 4.1 Apply Sinusoidal Motion

**Terminal 5** - Run joint controller:

```bash
source /opt/ros/humble/setup.bash
cd ~/module2_ex4_1

python3 4-joint-controller.py --amplitude 0.3 --frequency 0.5
```

**Expected**:
- Robot in Gazebo begins moving arms/legs in smooth wave pattern
- Console shows joint commands being sent
- Robot moves smoothly (no jerking)

### 4.2 Observe Gravity

While controller is running:

1. **In Gazebo client**: Watch robot move
2. **Notice**:
   - Joints oscillate smoothly
   - No sudden jerks or instability
   - Motion continues indefinitely until stopped

### 4.3 Experiment with Parameters

Try different motion patterns:

```bash
# Fast motion
python3 4-joint-controller.py --amplitude 0.5 --frequency 2.0

# Slow, wide motion
python3 4-joint-controller.py --amplitude 1.0 --frequency 0.2

# Small, fast twitches
python3 4-joint-controller.py --amplitude 0.1 --frequency 5.0
```

**Observations**:
- ✅ Amplitude controls how far joints move
- ✅ Frequency controls how fast motion occurs
- ✅ Physics keeps motion smooth and realistic

---

## Step 5: Observe Physics Behavior (30 minutes)

### 5.1 Check Gravity Effect

The humanoid stays upright because gravity pulls downward (-9.81 m/s² on Z axis).

Try modifying gravity temporarily:

**Terminal 6** - Run physics tuner:

```bash
source /opt/ros/humble/setup.bash
cd ~/module2_ex4_1

python3 4-physics-tuning.py --gravity moon
```

**Expected**: Humanoid becomes "bouncier" (lower gravity = weaker downward force)

### 5.2 Collision Demonstration

**Terminal 7** - Monitor collisions:

```bash
source /opt/ros/humble/setup.bash
cd ~/module2_ex4_1

python3 4-collision-demo.py
```

**Try**:
1. In Gazebo client, move robot to ground plane → collision detected
2. Move humanoid to collide with obstacles → see contact forces

---

## Step 6: Measure Performance (15 minutes)

### 6.1 FPS Measurement

```bash
# From Terminal with gzserver running
# Gazebo prints statistics at shutdown

# For detailed metrics:
ros2 topic hz /gazebo/model_states
```

**Expected**: ~50 Hz topic publishing (2× control loop rate)

### 6.2 Latency Measurement

```bash
# Measure time from command to joint state update
# Typical: <100ms latency (acceptable for real-time control)
```

---

## Acceptance Criteria

To successfully complete this exercise, you must:

- [ ] **Environment Setup**: Gazebo and ROS 2 verified working
- [ ] **Robot Loaded**: Humanoid appears in Gazebo and publishes /joint_states at >10 Hz
- [ ] **Joint Control**: Robot moves in smooth sinusoidal pattern when controller running
- [ ] **Gravity**: Robot is affected by gravity (doesn't float away)
- [ ] **Collision**: Robot collides realistically with ground plane and obstacles
- [ ] **Performance**: Simulation runs at ≥30 FPS without errors
- [ ] **Shutdown**: Graceful shutdown (Ctrl+C) without crashes

---

## Starter Code Template

See `starter_code/exercise_4_1_template.py` for a template with TODOs to complete.

---

## Automated Test Suite

Run the test suite to validate your setup:

```bash
cd ~/module2_ex4_1
pytest test_exercise_4_1.py -v
```

**Tests Check**:
- ✅ Gazebo running and accessible
- ✅ /joint_states topic exists and publishes
- ✅ Message frequency >10 Hz
- ✅ Joint positions change over time (robot moving)
- ✅ Gravity effect present (robot doesn't float)
- ✅ No simulation errors

---

## Debugging Guide

### Problem: "gazebo: command not found"

**Solution**:
```bash
sudo apt install gazebo11 libgazebo11-dev
```

### Problem: "/spawn_entity service not available"

**Solution**: Gazebo server not running with gazebo_ros plugins
```bash
gzserver --verbose 4-simple-world.world
# Verify "Factory plugin loaded" message
```

### Problem: "No /joint_states topic"

**Solution**: Robot not spawned correctly
```bash
# Check spawn succeeded
python3 4-load-robot.py --urdf humanoid.urdf --verify

# Check Gazebo logs for errors
```

### Problem: Robot moves jerky or unstable

**Solution**: Physics timestep too large
```bash
# In 4-simple-world.world, change:
# <max_step_size>0.001</max_step_size>
# to:
# <max_step_size>0.0005</max_step_size>  # Smaller = more stable
```

---

## Submission Checklist

- [ ] All steps completed (1-6)
- [ ] Acceptance criteria met (all 7 items)
- [ ] Test suite passing: `pytest test_exercise_4_1.py -v`
- [ ] No terminal errors or warnings
- [ ] Robot visible in Gazebo (if using client)
- [ ] Joint controller shows moving robot

---

## Next Steps

After completing Exercise 4.1:

1. **Move to Exercise 4.2** - Design custom world with physics tuning
2. **Explore parameters** - Try different:
   - Physics timesteps (smaller = more stable)
   - Friction coefficients (higher = stickier)
   - Gravity values (try Moon/Mars)
3. **Read ahead** - Start [Chapter 5: Unity Rendering](../../chapter-5.md)

---

## Resources

- **Gazebo Docs**: https://classic.gazebosim.org/tutorials
- **ROS 2 Docs**: https://docs.ros.org/en/humble/
- **Chapter 4**: [Physics Simulation with Gazebo](../../chapter-4.md)
- **Code Examples**: [4-load-robot.py](../../../static/examples/module-2/chapter-4-gazebo/4-load-robot.py)

---

**Exercise Status**: ✅ **Ready to Start**

**Date**: 2026-01-22
**Module**: 002-digital-twin
**Estimated Completion**: 2-3 hours
