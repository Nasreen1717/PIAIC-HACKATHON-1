# Data Model & Entities: Module 2 - The Digital Twin

**Date**: 2026-01-22
**Feature**: Module 2 - The Digital Twin (Gazebo & Unity)
**Status**: Phase 1 Design

---

## Overview

This document defines the core entities, their attributes, relationships, and validation rules for Module 2 content and code.

---

## Core Entities

### 1. GazeboWorld

**Description**: A Gazebo simulation environment containing robots, static objects, sensors, and physics parameters.

**Attributes**:
- `name` (string): Unique identifier for the world (e.g., "default", "warehouse")
- `gravity` (Vector3): Acceleration due to gravity (default: [0, 0, -9.81] m/s²)
- `friction_mu` (float): Coefficient of kinetic friction (range: 0.0-1.0, default: 0.7)
- `collision_enabled` (bool): Enable/disable collision detection (default: true)
- `physics_engine` (enum): "ode", "bullet", "simbody" (default: "ode")
- `timestep` (float): Physics simulation timestep in seconds (default: 0.001, range: 0.0001-0.01)
- `max_contacts_per_body` (int): Collision points per object (default: 10)
- `objects` (List[GazeboObject]): Static and dynamic objects in world
- `robots` (List[SimulatedRobot]): Robots loaded in world
- `lights` (List[Light]): Lighting sources
- `plugins` (List[GazeboPlugin]): World-level plugins (cameras, sensors, controllers)

**Validation Rules**:
- `gravity` magnitude should be ~9.81 m/s² ± 10% (realistic)
- `friction_mu` in range [0.0, 1.0]
- `timestep` > 0 and reasonable (typically 0.0001 to 0.01 seconds)
- All `robots` and `objects` must have unique names

**State Transitions**:
```
Created → Initialized → Running → Paused → Stopped
           (load SDF)  (step)   (pause)  (reset)
```

---

### 2. SimulatedRobot

**Description**: A robot instance in Gazebo with joints, sensors, and ROS 2 interface.

**Attributes**:
- `name` (string): Unique robot identifier (e.g., "humanoid_1")
- `urdf_path` (string): File path to URDF description
- `base_link` (string): Name of root link in kinematic chain (usually "torso")
- `links` (List[Link]): Physical segments of robot
- `joints` (List[Joint]): Articulations between links
- `sensors` (List[GazeboSensor]): Attached sensors (cameras, IMUs, LiDARs)
- `mass` (float): Total mass in kg
- `joint_states` (JointState message): Current position, velocity, effort for all joints
- `odom_frame` (string): Odometry reference frame (usually "odom")
- `base_frame` (string): Robot base coordinate frame (usually "base_link")

**Relationships**:
- Contains multiple `Link` and `Joint` objects (one-to-many)
- Contains multiple `GazeboSensor` objects (one-to-many)
- Published via ROS 2 topics: `/joint_states` (sensor_msgs/JointState), `/odom` (nav_msgs/Odometry)

**Validation Rules**:
- `urdf_path` must be valid and loadable
- All `joints` must reference valid parent/child `links`
- `base_link` must exist in `links` list
- Total mass must be > 0

---

### 3. Link

**Description**: A rigid body segment of a robot (from URDF, inherited from Module 1).

**Attributes**:
- `name` (string): Unique link name within robot (e.g., "torso", "left_arm")
- `mass` (float): Link mass in kg (default: 0 for static links)
- `visual_geometry` (Geometry): 3D shape for rendering (box, cylinder, sphere, mesh)
- `collision_geometry` (Geometry): Collision shape for physics (may differ from visual)
- `inertia` (3x3 Matrix): Inertia tensor [ixx, ixy, ixz; iyx, iyy, iyz; izx, izy, izz]
- `origin_xyz` (Vector3): Position offset from parent frame [x, y, z]
- `origin_rpy` (Vector3): Orientation offset from parent frame [roll, pitch, yaw]
- `material` (Material): Color and texture properties

**Geometry Subtypes**:
- `BoxGeometry`: size (x, y, z)
- `CylinderGeometry`: radius, length
- `SphereGeometry`: radius
- `MeshGeometry`: mesh_path, scale

**Validation Rules**:
- `mass` >= 0
- `inertia` matrix must be symmetric and positive-definite
- `visual_geometry` and `collision_geometry` should be reasonable (not zero-sized)
- `origin_rpy` values: roll, pitch, yaw in radians

---

### 4. Joint

**Description**: Articulation between two links (from URDF, inherited from Module 1).

**Attributes**:
- `name` (string): Unique joint name (e.g., "left_shoulder")
- `type` (enum): "revolute", "prismatic", "fixed", "floating", "planar" (default: "revolute")
- `parent_link` (string): Name of parent link
- `child_link` (string): Name of child link
- `axis_xyz` (Vector3): Axis of motion (unit vector, e.g., [0, 1, 0] for Y-axis)
- `origin_xyz` (Vector3): Joint position relative to parent [x, y, z]
- `origin_rpy` (Vector3): Joint orientation relative to parent [roll, pitch, yaw]
- `limits_lower` (float): Lower position limit (rad for revolute, m for prismatic)
- `limits_upper` (float): Upper position limit
- `limits_velocity` (float): Maximum velocity (rad/s or m/s)
- `limits_effort` (float): Maximum force/torque (N or N⋅m)
- `damping` (float): Friction coefficient (default: 0.0)
- `friction` (float): Static friction (default: 0.0)
- `current_position` (float): Current angle/displacement (rad or m)
- `current_velocity` (float): Current angular/linear velocity (rad/s or m/s)
- `current_effort` (float): Current applied torque/force (N⋅m or N)

**Validation Rules**:
- `limits_lower` <= `current_position` <= `limits_upper`
- `type` must be one of allowed enum values
- `parent_link` and `child_link` must exist in robot
- `axis_xyz` must be normalized (magnitude ≈ 1.0)
- `limits_velocity` and `limits_effort` > 0

---

### 5. GazeboSensor

**Description**: A sensor attached to a robot link, publishing data via ROS 2 topics.

**Attributes**:
- `name` (string): Unique sensor name (e.g., "lidar_front")
- `type` (enum): "camera", "laser", "imu", "contact", "air_pressure", etc.
- `parent_link` (string): Link to which sensor is attached
- `origin_xyz` (Vector3): Position relative to parent link
- `origin_rpy` (Vector3): Orientation relative to parent link
- `update_rate` (float): Publishing frequency in Hz (default: 30.0)
- `topic_name` (string): ROS 2 topic to publish to (e.g., "/camera/rgb/image_raw")
- `ros_message_type` (string): ROS 2 message type (e.g., "sensor_msgs/Image")

**Sensor-Specific Attributes**:

**Camera**:
- `width` (int): Image width in pixels (default: 640)
- `height` (int): Image height in pixels (default: 480)
- `fov` (float): Field of view in radians (default: 1.5708, ~90°)
- `near_clip` (float): Near clipping plane distance (m, default: 0.01)
- `far_clip` (float): Far clipping plane distance (m, default: 100.0)
- `cx`, `cy` (float): Principal point (pixel coordinates)
- `fx`, `fy` (float): Focal length (pixels)
- `publish_depth` (bool): Also publish depth frames (default: true)

**Laser (2D LiDAR)**:
- `samples` (int): Number of range measurements per scan (default: 360)
- `min_angle` (float): Minimum scanning angle (rad, default: -π)
- `max_angle` (float): Maximum scanning angle (rad, default: π)
- `min_range` (float): Minimum detectable range (m, default: 0.05)
- `max_range` (float): Maximum range (m, default: 10.0)
- `noise_stddev` (float): Standard deviation of range noise (m, default: 0.01)

**Laser3D (3D LiDAR)**:
- `vertical_samples` (int): Vertical measurement points (default: 32)
- `horizontal_samples` (int): Horizontal measurements (default: 1024)
- `min_range`, `max_range`, `noise_stddev` (same as 2D laser)

**IMU**:
- `accel_noise_stddev` (float): Accelerometer noise (m/s², default: 0.01)
- `gyro_noise_stddev` (float): Gyroscope noise (rad/s, default: 0.01)
- `accel_bias_range` (float): Accelerometer bias drift (m/s², default: 0.05)
- `gyro_bias_range` (float): Gyroscope bias drift (rad/s, default: 0.05)

**Validation Rules**:
- `update_rate` > 0 and reasonable (1-100 Hz typical)
- `parent_link` must exist in robot
- Camera intrinsics (fx, fy, cx, cy) must be positive and reasonable
- Laser angles: `min_angle` < `max_angle`
- Range: `min_range` < `max_range`
- Noise parameters >= 0

---

### 6. JointState (ROS 2 Message)

**Description**: Standard ROS 2 message containing joint positions, velocities, and efforts (from Module 1).

**Attributes** (sensor_msgs/JointState):
- `header` (Header): Timestamp and frame ID
- `name` (List[string]): Joint names in order
- `position` (List[float]): Current angle/displacement (rad or m)
- `velocity` (List[float]): Current velocity (rad/s or m/s)
- `effort` (List[float]): Applied torque/force (N⋅m or N)

**Validation Rules**:
- All lists must have same length
- Positions must be within joint limits
- Velocities and efforts should be continuous (no sudden jumps > physically reasonable)

**Publishing Frequency**:
- Gazebo publishes at robot update rate (typically 50 Hz)
- ROS 2 topic: `/joint_states`

---

### 7. PointCloud2 (ROS 2 Message)

**Description**: Standard ROS 2 message for 3D point cloud data (from LiDAR/depth cameras).

**Attributes** (sensor_msgs/PointCloud2):
- `header` (Header): Timestamp and frame ID
- `width` (int): Number of points in horizontal direction
- `height` (int): Number of points in vertical direction (1 for unorganized clouds)
- `fields` (List[PointField]): Description of point fields (x, y, z, intensity, etc.)
- `point_step` (int): Bytes per point
- `row_step` (int): Bytes per row
- `data` (List[uint8]): Raw point data (binary)
- `is_dense` (bool): No invalid points (default: false, some points may be NaN)

**Common Fields**:
- `x`, `y`, `z` (float32): 3D coordinates
- `intensity` (float32): Laser return intensity (0-1 or 0-255)
- `rgb` (uint32): Color encoding

**Validation Rules**:
- Total points = `width` × `height`
- Data buffer size = `width` × `row_step`
- Fields must be valid (x, y, z present)

---

### 8. Image (ROS 2 Message)

**Description**: Standard ROS 2 message for camera images (depth, RGB, thermal).

**Attributes** (sensor_msgs/Image):
- `header` (Header): Timestamp and frame ID
- `height` (int): Image height in pixels
- `width` (int): Image width in pixels
- `encoding` (string): Pixel format (e.g., "rgb8", "bgra8", "mono8", "32FC1" for depth)
- `is_bigendian` (bool): Byte order (default: false)
- `step` (int): Bytes per row
- `data` (List[uint8]): Raw image data (binary)

**Common Encodings**:
- `rgb8`: 8-bit RGB, 3 channels
- `bgra8`: 8-bit BGRA, 4 channels
- `mono8`: 8-bit grayscale
- `32FC1`: 32-bit float (for depth/disparity)

**Validation Rules**:
- Total data size = `height` × `step`
- Encoding must be recognized
- Height, width > 0

---

### 9. Imu (ROS 2 Message)

**Description**: Standard ROS 2 message for inertial measurement unit (accelerometer + gyroscope).

**Attributes** (sensor_msgs/Imu):
- `header` (Header): Timestamp and frame ID
- `orientation` (Quaternion): Estimated orientation [x, y, z, w]
- `angular_velocity` (Vector3): Angular velocity [x, y, z] in rad/s
- `linear_acceleration` (Vector3): Linear acceleration [x, y, z] in m/s²
- `orientation_covariance`, `angular_velocity_covariance`, `linear_acceleration_covariance` (6x6 matrices): Measurement uncertainty

**Validation Rules**:
- Quaternion should be normalized (|q| ≈ 1.0)
- Angular velocity: reasonable range (-2π to 2π rad/s typical)
- Linear acceleration: reasonable range (-30 to 30 m/s² typical, includes gravity ~9.81 m/s²)
- Covariance matrices should be symmetric and positive-definite

---

### 10. UnityRobot (C# Class)

**Description**: Unity representation of a simulated robot, synchronized with ROS 2 joint state.

**Attributes**:
- `robotName` (string): Unique identifier (matches Gazebo SimulatedRobot name)
- `baseLink` (Transform): Root node of robot hierarchy (usually "torso")
- `joints` (Dictionary<string, Joint>): Mapping of joint names to Unity Joint objects
- `animators` (Dictionary<string, Animator>): Joint-specific animation controllers
- `materials` (Dictionary<string, Material>): Material assignments for rendering
- `ros2Subscriber` (ROS2Subscriber): Subscription to `/joint_states` topic
- `isAnimating` (bool): Whether robot is currently being animated
- `animationSmoothing` (float): Smoothing factor for joint interpolation (0-1)

**Methods**:
- `UpdateFromJointState(JointState msg)`: Consume ROS 2 JointState message and update robot pose
- `SetJointTarget(string jointName, float targetAngle)`: Set target angle for joint animation
- `GetCurrentJointPosition(string jointName)`: Query current joint angle
- `EnablePhysics()`: Activate Rigidbody components
- `DisablePhysics()`: Deactivate Rigidbody (for animation-only mode)

**Validation Rules**:
- `robotName` must match a loaded URDF
- Joint names in message must match declared joints
- Target angles must be within joint limits
- Animation smoothing in [0.0, 1.0]

---

### 11. GazeboPlugin

**Description**: Gazebo world or robot plugin extending simulation capabilities.

**Attributes**:
- `name` (string): Plugin identifier (e.g., "gazebo_ros_state_publisher")
- `type` (string): Plugin class name (e.g., "gazebo_ros::NodeState")
- `params` (Dictionary<string, string>): Configuration parameters

**Common Plugins**:
- `gazebo_ros2_control`: Robot actuator control via ROS 2
- `gazebo_ros_state_publisher`: Publish robot state (joint states, transforms)
- `gazebo_ros_camera`: RGB camera simulation
- `gazebo_ros_laserscan`: 2D LiDAR simulation
- `gazebo_ros_gpu_laser`: 3D LiDAR (GPU accelerated)
- `gazebo_ros_imu_sensor`: IMU simulation

**Validation Rules**:
- Plugin type must exist in Gazebo plugin registry
- Parameters must be valid for plugin type

---

## Relationships & Dependencies

```
GazeboWorld
├── contains → SimulatedRobot (1..*)
│   ├── has-base-link → Link
│   ├── has-joints → Joint (1..*)
│   │   └── connects → Link (parent) + Link (child)
│   ├── has-sensors → GazeboSensor (1..*)
│   │   └── publishes → (JointState | PointCloud2 | Image | Imu)
│   └── has-plugin → GazeboPlugin (1..*)
├── contains → GazeboObject (static objects)
├── has-plugin → GazeboPlugin (world-level)
└── publishes → JointState, PointCloud2, Image, Imu (ROS 2 topics)

UnityRobot
├── represents → SimulatedRobot (1:1 sync)
├── has-base → Transform (base link)
├── has-joints → Joint (1..*, Unity Joint components)
├── has-materials → Material (1..*)
├── subscribes-to → /joint_states (ROS 2 topic)
└── reads-from → GazeboSensor (via ROS 2 messages)
```

---

## Data Flow Diagram

```
Gazebo Simulation (Backend)
│
├─ SimulatedRobot
│  ├─ Joint 1 (angle) ──┐
│  ├─ Joint 2 (angle) ──┤
│  └─ Joint N (angle) ──┤
│                       │
│  Sensor: LiDAR ───────┼──→ Point Cloud Data
│  Sensor: Camera ──────┼──→ Depth/RGB Image
│  Sensor: IMU ─────────┘──→ Acceleration/Rotation
│
└─ Publishes: /joint_states (sensor_msgs/JointState)
   Publishes: /scan (sensor_msgs/LaserScan)
   Publishes: /camera/depth/image_raw (sensor_msgs/Image)
   Publishes: /imu/data (sensor_msgs/Imu)

        ↓ ROS 2 Middleware ↓

ROS 2 Nodes (Processing)
│
├─ 6-sensor-fusion.py
│  ├─ Subscribe: /joint_states → JointState
│  ├─ Subscribe: /scan → PointCloud2
│  ├─ Subscribe: /imu/data → Imu
│  └─ Process: EKF fusion
│
└─ Publish: /robot_pose (estimated state)

        ↓ ROS 2 Middleware ↓

Unity Frontend
│
└─ UnityRobot
   ├─ Subscribe: /joint_states → Animator.SetFloat()
   ├─ Read: /robot_pose → Visual feedback
   └─ Render: 60+ FPS
```

---

## Validation & Testing

### Entity Validation Functions (Pseudo-code)

```python
def validate_gazebo_world(world: GazeboWorld) -> bool:
    """Validate world configuration."""
    assert world.gravity.magnitude() ≈ 9.81  # Within 10%
    assert world.timestep > 0 and world.timestep <= 0.01
    assert all(r.name unique for r in world.robots)
    return True

def validate_simulated_robot(robot: SimulatedRobot, world: GazeboWorld) -> bool:
    """Validate robot within world context."""
    assert load_urdf(robot.urdf_path) succeeds
    assert robot.base_link in [l.name for l in robot.links]
    for joint in robot.joints:
        assert joint.parent_link in [l.name for l in robot.links]
        assert joint.child_link in [l.name for l in robot.links]
        assert joint.limits_lower <= joint.current_position <= joint.limits_upper
    for sensor in robot.sensors:
        assert sensor.parent_link in [l.name for l in robot.links]
    return True

def validate_unity_robot(unity_robot: UnityRobot, ros2_message: JointState) -> bool:
    """Validate synchronization between Unity and ROS 2."""
    assert unity_robot.robotName == ros2_message.source_robot
    assert set(unity_robot.joints.keys()) == set(ros2_message.name)
    for joint_name, position in zip(ros2_message.name, ros2_message.position):
        joint = unity_robot.joints[joint_name]
        assert joint.lower_limit <= position <= joint.upper_limit
    return True
```

### Test Coverage

- ✅ Unit tests for each entity class
- ✅ Integration tests for GazeboWorld + SimulatedRobot + ROS 2 pub/sub
- ✅ Synchronization tests for UnityRobot + JointState messages
- ✅ Sensor simulation tests for PointCloud2, Image, Imu messages

---

**Status**: ✅ **DATA MODEL COMPLETE**

All entities defined with validation rules, relationships documented, and data flow illustrated. Ready for contract generation and quickstart documentation.
