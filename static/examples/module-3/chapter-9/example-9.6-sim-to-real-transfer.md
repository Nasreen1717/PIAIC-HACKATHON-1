# Example 9.6: Sim-to-Real Transfer Protocol for Bipedal Navigation

## Overview

This document describes the complete protocol for transferring Nav2 navigation behaviors
from Isaac Sim to physical hardware. It includes parameter mapping, validation procedures,
hardware testing phases, and failure recovery procedures.

**Duration**: 4-6 weeks total (phased approach)
**Team**: 2-3 engineers, 1 safety supervisor

---

## Part 1: Pre-Transfer Preparation

### 1.1 Parameter Validation in Simulation

Before any hardware testing, validate all parameters in Isaac Sim with realistic physics:

**Step 1: Load realistic simulation parameters**
```python
# Sim parameter file: sim_params.yaml
robot:
  mass: 12.5  # kg (humanoid H1)
  com_height: 0.55  # meters
  foot_length: 0.25  # meters
  foot_width: 0.10   # meters
  joint_friction: 0.01  # Default friction
  sensor_noise:
    imu_accel: 0.05  # m/s² standard deviation
    imu_gyro: 0.01   # rad/s
    camera_blur: 2   # pixels
    lidar_noise: 0.02  # meters

environment:
  gravity: 9.81  # m/s²
  ground_friction: 0.7  # Coefficient of friction (rubber on vinyl)
  air_resistance: 0.001
  simulation_timestep: 0.001  # 1ms
```

**Step 2: Run sensitivity analysis**
- Vary mass by ±10% → measure impact on balance margin
- Vary friction by ±20% → measure max stable slope
- Add sensor noise → measure navigation accuracy degradation
- Target: <5% performance loss with realistic parameters

**Step 3: Benchmark perception in sim**
```python
# Example: VSLAM accuracy test
for trial in range(100):
    # Initialize VSLAM
    # Walk 5m straight path
    # Measure final pose error vs. ground truth
    error = abs(final_x_estimate - final_x_truth)
    print(f"Trial {trial}: pose error = {error:.3f}m")
# Target: Mean error <0.1m over 5m walk
```

**Step 4: Costmap configuration validation**
- Load real office map into Isaac Sim
- Run 20 navigation missions to random waypoints
- Target: >95% success rate, <0.3m goal error

### 1.2 Hardware Specifications Document

Create a reference document with exact hardware parameters:

```yaml
# hardware_specs.yaml
humanoid_h1:
  dimensions:
    height: 1.71  # meters
    width: 0.35   # meters
    foot_length: 0.25  # meters
    foot_width: 0.10   # meters

  mass:
    total: 12.5   # kg
    torso: 4.5
    each_leg: 3.5
    head: 0.8

  actuators:
    hip_roll_motor:
      max_torque: 50  # Nm
      max_velocity: 2.0  # rad/s
      reduction_ratio: 6
    hip_pitch_motor:
      max_torque: 60  # Nm
      max_velocity: 2.0  # rad/s
    knee_motor:
      max_torque: 70  # Nm
      max_velocity: 2.5  # rad/s

  sensors:
    imu:
      type: BNO055
      calibration_status: FULLY_CALIBRATED  # Done in phase 2
      zero_g_offset: [0.05, -0.03, 0.0]  # m/s²
    camera:
      type: RealSense D455
      resolution: 1280×720
      fps: 30
      depth_range: 0.1-6.0 meters
    lidar:
      type: RPLiDAR A2M30
      scan_range: 0.15-8.0 meters
      scan_frequency: 10 Hz
    contact_sensors:
      left_foot: CAPACITIVE
      right_foot: CAPACITIVE
      threshold_voltage: 2.5  # Adjust in phase 2

  power:
    battery: 2S LiPo (7.4V nominal)
    capacity: 2200 mAh
    max_continuous_current: 50A
    warning_threshold: 5%  # Battery low warning
```

---

## Part 2: Hardware Bringup Phase (Week 1)

### 2.1 Pre-flight Checklist

**Mechanical Inspection** (30 min)
- [ ] All joints move freely without grinding/squeaking
- [ ] Actuator limits programmed in firmware (-30° to +120° for knee)
- [ ] Foot sensors respond to press (low/high voltage when pressed)
- [ ] Brake systems engaged/disengaged correctly
- [ ] No loose cables or connectors

**Electrical Inspection** (20 min)
- [ ] Battery voltage in range: 8.4-10.2V (2S LiPo nominal: 7.4-8.4V)
- [ ] Motor controllers firmware version verified
- [ ] IMU responds to pitch/roll input
- [ ] Wireless remote pairs and receives commands
- [ ] All LED indicators functioning

**Software Verification** (30 min)
```bash
# Verify ROS 2 nodes start
ros2 launch humanoid_nav2 nav2_bringup.launch.py \
  robot_model:=humanoid_h1 \
  use_sim_time:=false

# Check topics
ros2 topic list | grep -E "imu|odom|scan|depth"

# Verify services
ros2 service list | grep -E "estop|reset"

# Verify TF tree
ros2 run tf2_tools view_frames  # Check all transforms
```

### 2.2 Sensor Calibration

**IMU Calibration** (15 min)
1. Place robot on flat surface
2. Keep perfectly still for 30 seconds
3. Run calibration routine:
```python
# Measure gravity vector offset
import rospy
from sensor_msgs.msg import Imu

accel_data = []

def imu_callback(msg):
    accel_data.append([msg.linear_acceleration.x,
                      msg.linear_acceleration.y,
                      msg.linear_acceleration.z])

sub = rospy.Subscriber("/imu/data", Imu, imu_callback)
rospy.sleep(10)  # Collect 10 seconds

# Calculate mean
mean_accel = np.mean(accel_data, axis=0)
print(f"Calibrated offset: {mean_accel}")
# Should be close to [0, 0, 9.81] when flat
```

**Contact Sensor Calibration** (10 min)
1. Measure voltage when foot pressed: V_pressed
2. Measure voltage when foot raised: V_released
3. Set threshold: V_threshold = (V_pressed + V_released) / 2
```python
# Calibration procedure
def calibrate_contact_sensors():
    print("Press left foot and hold...")
    v_pressed_left = read_voltage("left_foot")

    print("Raise left foot...")
    v_released_left = read_voltage("left_foot")

    threshold_left = (v_pressed_left + v_released_left) / 2
    return threshold_left
```

**Wireless Communication Test** (10 min)
- Send 100 commands from remote
- Measure latency: < 100ms required
- Measure loss rate: < 1% allowed
```bash
# ROS 2 command latency test
# Publish commands and measure /cmd_vel subscription latency
ros2 topic hz /cmd_vel  # Should be ~10-20 Hz
```

### 2.3 Static Balance Test

**Objective**: Verify robot can stand without falling

**Procedure**:
1. Power on all actuators
2. Engage all motor brakes
3. Run balance controller at 1 Hz
4. Monitor IMU for sustained acceleration > 1.5g (fall indicator)
5. Duration: 60 seconds

**Pass criteria**:
- No falling
- IMU acceleration < 0.5g (steady state)
- Motor currents stable (< 20A per motor)

**Code**:
```python
def static_balance_test(duration_sec=60):
    start_time = time.time()
    max_accel = 0
    fall_detected = False

    while time.time() - start_time < duration_sec:
        # Read IMU
        imu_data = get_imu()
        accel = np.linalg.norm(imu_data.linear_acceleration - [0, 0, 9.81])
        max_accel = max(max_accel, accel)

        if accel > 1.5:
            print("FALL DETECTED!")
            emergency_stop()
            fall_detected = True
            break

        # Send zero velocity command (maintain position)
        cmd = Twist(linear=Vector3(0, 0, 0), angular=Vector3(0, 0, 0))
        publish_cmd_vel(cmd)

        time.sleep(0.1)

    print(f"Balance test: max_accel={max_accel:.2f}g")
    return not fall_detected
```

---

## Part 3: Locomotion Testing Phase (Week 2)

### 3.1 Walking in a Straight Line

**Objective**: Validate basic forward walking motion

**Setup**:
- Clear hallway, minimum 5m length
- Mark start line and 5m target line
- Use tape or chalk

**Procedure**:
1. Place robot at start line
2. Send goal 5m ahead
3. Monitor VSLAM odometry
4. Record final position

**Pass criteria**:
- No falls
- Final position within 0.3m of 5m target
- VSLAM tracking stable (variance < 0.1m)
- Motor temperatures < 60°C

**Success metrics** (run 10 trials):
| Metric | Target |
|--------|--------|
| Success rate | ≥ 90% (9/10 trials) |
| Final position error | < 0.3m |
| Mean motor current | 15 ± 5A |
| Mean temperature | < 50°C |

### 3.2 Turning and Direction Change

**Objective**: Validate yaw control and balance during turns

**Procedure**:
1. Start at origin
2. Execute 90° left turn
3. Walk 2m
4. Execute 90° right turn
5. Walk 2m back to origin
6. Record final pose error

**Expected**: Closed-loop error < 0.3m and ±15° heading

**Run 5 trials**, record each success

### 3.3 Obstacle Avoidance (Static)

**Setup**:
- Place traffic cone at 2m distance in front of robot
- Start robot 1m away

**Procedure**:
1. Send navigation goal beyond cone
2. Nav2 should detect obstacle and plan around it
3. Monitor costmap inflation distance (should be 0.20-0.25m)
4. Verify robot maintains >0.5m clearance

**Pass criteria**:
- No collision
- Successful avoidance in >80% of trials
- Robot returns to original path after obstacle

### 3.4 Slope Walking

**Setup**:
- 5° ramp (0.5m rise over 5.7m length) or equivalent
- Safety net at bottom

**Procedure**:
1. Walk up slope: 2 meters
2. Walk down slope: 2 meters
3. Record IMU data and motor current

**Pass criteria**:
- No falls
- Motor current increase < 50% vs. flat
- Stride length decrease < 20% (due to effort)

---

## Part 4: Navigation Testing Phase (Week 3-4)

### 4.1 VSLAM Initialization and Tracking

**Objective**: Validate vision-based localization in office environment

**Setup**:
- Office room (~10m × 5m) with features (posters, furniture)
- Well-lit (> 300 lux)

**Procedure**:
```python
def vslam_validation():
    # 1. Initialize VSLAM by scanning environment
    scan_duration = 10  # seconds
    feature_count = []

    while time.time() - start < scan_duration:
        frame = get_camera_frame()
        features = count_features(frame)
        feature_count.append(features)
        time.sleep(0.1)

    mean_features = np.mean(feature_count)
    print(f"Mean features: {mean_features:.0f}/frame")

    # Target: > 10 features/frame
    assert mean_features > 10, "VSLAM initialization failed"

    # 2. Walk loop and check closure error
    start_pose = get_odometry()
    walk_loop(length=10)  # 10m walk
    end_pose = get_odometry()
    closure_error = distance(start_pose, end_pose)
    print(f"Loop closure error: {closure_error:.3f}m")

    # Target: < 0.5m error for 10m loop
    assert closure_error < 0.5, "VSLAM tracking degraded"
```

**Pass criteria**:
- Feature count > 10 per frame
- Loop closure error < 0.5m for 10m loop
- Tracking uptime > 95%

### 4.2 Autonomous Navigation to Waypoint

**Objective**: End-to-end navigation task

**Setup**:
- Mark start and goal positions (minimum 2m apart)
- Ensure at least 1m clearance from obstacles

**Procedure**:
```python
def navigate_to_waypoint(goal_x, goal_y, goal_theta):
    # Send goal via Nav2
    send_goal(goal_x, goal_y, goal_theta)

    # Monitor progress
    start_time = time.time()
    timeout = 120  # seconds

    while time.time() - start_time < timeout:
        current_pose = get_odometry()
        error = distance(current_pose, goal)

        print(f"Progress: {error:.2f}m to goal")

        if error < 0.25:
            print("Goal reached!")
            return True

        if error > 2.0 and time.time() - start_time > 30:
            print("Navigation failed - stuck")
            return False

        time.sleep(0.5)

    return False
```

**Pass criteria**:
- Reaches goal within 0.5m
- No collisions with obstacles
- Completes in < 2 minutes
- Success rate > 80% across 10 attempts

### 4.3 Dynamic Obstacle Avoidance

**Setup**:
- Moving obstacle (person) at ~1 m/s
- Robot must maintain > 0.5m clearance

**Procedure**:
1. Start robot navigation to goal
2. After robot is walking, introduce moving obstacle
3. Obstacle moves toward robot from left
4. Monitor costmap update rate
5. Verify robot replans and avoids

**Pass criteria**:
- Costmap updates every 100ms
- Robot detects obstacle within 1 second
- Robot replans and avoids (>80% success)
- No collision occurs

### 4.4 Sensor Failure Recovery

**Objective**: Graceful handling of sensor loss

**Tests**:

**Test A: VSLAM Loss**
- During navigation, disconnect camera (software)
- Robot should fall back to odometry-only navigation
- Expect reduced accuracy (>1m error possible)
- But should continue moving safely

**Test B: LiDAR Loss**
- During navigation, disable LiDAR
- Robot should reduce speed and rely on obstacle layers
- Should still avoid detected obstacles
- Expected behavior: conservative movement

**Test C: Wireless Timeout**
- Disconnect wireless remote connection
- Robot should trigger E-stop within 5 seconds
- All motors brake immediately
- Safe shutdown procedure

---

## Part 5: Production Deployment Validation (Week 4-6)

### 5.1 Endurance Test (1-Hour Operation)

**Objective**: Verify system stability over extended operation

**Procedure**:
```python
def endurance_test(duration_hours=1):
    start_time = time.time()
    end_time = start_time + duration_hours * 3600

    failures = []
    metrics = {
        'walks': 0,
        'obstacles_avoided': 0,
        'avg_motor_temp': [],
        'battery_voltage_log': [],
        'crashes': 0
    }

    while time.time() < end_time:
        # Every 5 minutes: autonomous navigation task
        goal = random_waypoint()

        try:
            if navigate_to_waypoint(goal):
                metrics['walks'] += 1
            else:
                failures.append(f"Navigation failed at {time.time()}")

        except Exception as e:
            metrics['crashes'] += 1
            failures.append(str(e))
            recover_from_failure()

        # Log metrics
        metrics['avg_motor_temp'].append(get_motor_temperature())
        metrics['battery_voltage_log'].append(get_battery_voltage())

        # Safety check every iteration
        if get_battery_voltage() < 7.0:
            print("Battery too low - charging")
            break

    # Print results
    print(f"\nEndurance test results (1 hour):")
    print(f"  Successful walks: {metrics['walks']}")
    print(f"  Failures: {len(failures)}")
    print(f"  Crashes: {metrics['crashes']}")
    print(f"  Mean motor temp: {np.mean(metrics['avg_motor_temp']):.1f}°C")
    print(f"  Battery end: {metrics['battery_voltage_log'][-1]:.2f}V")

    return len(failures) == 0
```

**Pass criteria**:
- ≥ 10 successful navigation tasks
- 0 crashes
- Mean motor temperature < 70°C
- Battery voltage > 7.0V (end of test)
- No unplanned E-stops

### 5.2 Production Checklist

**Before field deployment:**

- [ ] **Documentation**
  - [ ] Safety manual reviewed by team
  - [ ] Emergency procedures posted
  - [ ] Calibration checklist signed off
  - [ ] All parameters locked in production config

- [ ] **Hardware**
  - [ ] All actuators tested individually
  - [ ] IMU/camera/lidar verified to spec
  - [ ] Wireless range tested (>20m)
  - [ ] Battery health: <20% capacity loss
  - [ ] Brake systems functional

- [ ] **Software**
  - [ ] Nav2 costmap accuracy validated
  - [ ] VSLAM tracking reliable (>90% uptime)
  - [ ] E-stop latency < 50ms
  - [ ] Log files saved correctly
  - [ ] Firmware version locked

- [ ] **Safety**
  - [ ] Medical team trained and present
  - [ ] Safety perimeter established
  - [ ] Spotters assigned (2 people minimum)
  - [ ] Incident response plan confirmed
  - [ ] Emergency phone numbers posted

---

## Part 6: Failure Modes & Recovery

| Failure Mode | Signature | Recovery |
|--------------|-----------|----------|
| **VSLAM loss** | /odometry stale (>1s) | Switch to EKF odometry, reduce speed 50% |
| **Costmap lag** | Occupancy grid age > 1s | Pause navigation, wait for update |
| **Motor overheat** | Temperature > 80°C | Halt, cool for 30s, retry |
| **Battery low** | Voltage < 7.0V | Return to dock, switch battery |
| **Sensor dropout** | Topic timeout | Switch to fallback sensor |
| **Controller hang** | /cmd_vel stale > 2s | E-stop, hard reset |
| **Fall detected** | IMU accel > 1.5g sustained | Engage brakes, shutdown |

---

## Conclusion

Following this protocol ensures safe and reliable transfer of simulation-based navigation
to physical hardware. The phased approach allows early detection of issues while maintaining
safety throughout.

**Expected timeline**: 4-6 weeks total
**Success rate**: >95% autonomous navigation missions
**Safety incidents**: 0 (target)
