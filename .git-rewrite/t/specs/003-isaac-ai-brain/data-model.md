# Phase 1 Data Model: Module 3 Key Entities

**Created**: 2026-01-23
**Purpose**: Define core entities, relationships, and validation rules for Module 3 examples and exercises

---

## 1. Isaac Sim Scene

**Represents**: A photorealistic 3D environment with physics simulation, sensors, and asset rendering

**Fields**:
- `scene_id` (string, unique): Identifier for the scene (e.g., "lab-environment-v1")
- `gravity_vector` (float[3]): Gravity acceleration (default: [0, 0, -9.81] m/s²)
- `gravity_tolerance` (float): Calibration tolerance (default: ±0.05 m/s²; ±0.5% of Earth gravity)
- `physics_timestep` (float): Simulation step duration (range: 0.0001–0.01 seconds; default: 0.0083s = 120 Hz)
- `physics_engine` (enum): "PhysX" (NVIDIA default) or "GJK" (legacy; not recommended)
- `renderer_type` (enum): "PathTraced" (high fidelity) or "RealTime" (faster, lower fidelity)
- `render_resolution` (int[2]): Output image resolution (e.g., [1920, 1080] or [1024, 768] for efficiency)
- `assets` (Asset[]): List of 3D models, robots, obstacles loaded in scene
- `sensors` (Sensor[]): List of virtual sensors (cameras, depth, IMU)
- `lights` (Light[]): Directional/spot lights for rendering
- `environment_material` (Material): Terrain/ground friction, restitution, texture

**Relationships**:
- Contains: Robot Models (1..N), Sensors (1..N), Assets (0..N)
- Produces: Synthetic images, depth maps, sensor readings
- Consumes: URDF/USD model files, configuration YAML

**Validation Rules**:
- `gravity_vector` magnitude must be 9.81 ± 0.05 m/s² (calibrated for Earth)
- `physics_timestep` must be in [0.0001, 0.01] seconds (ensures stability, respects Nyquist for dynamics)
- `render_resolution` must be 2D, each dimension ≥512 and ≤4096 (performance/quality trade-off)
- All assets must be valid USD or URDF (fail fast if malformed)
- No duplicate `scene_id` across active simulations

**State Transitions**:
- `uninitialized` → `loading` (when assets are imported)
- `loading` → `ready` (when all physics parameters validated)
- `ready` → `running` (simulation starts)
- `running` → `paused` (on explicit pause)
- `paused` → `running` (on resume) OR `stopped` (on shutdown)

**Example (Chapter 7, Example 7.1)**:
```yaml
scene_id: lab_humanoid_v1
gravity_vector: [0, 0, -9.81]
physics_timestep: 0.0083
renderer_type: PathTraced
render_resolution: [1920, 1080]
assets:
  - type: urdf
    path: /models/humanoid_robot.urdf
    position: [0, 0, 0.5]
  - type: usd
    path: /assets/lab_environment.usd
    position: [0, 0, 0]
sensors:
  - type: camera
    name: rgb_camera
    position: [0.15, 0, 1.7]  # Robot head
  - type: depth
    name: depth_camera
    position: [0.15, 0, 1.7]
```

---

## 2. Robot Model

**Represents**: A URDF-based humanoid robot with kinematic/dynamic properties, collision geometry, and sensor attachments

**Fields**:
- `robot_id` (string, unique): Identifier (e.g., "atlas-humanoid-01")
- `urdf_path` (string): Path to URDF file (must exist and be valid)
- `base_link` (string): Name of root link in URDF
- `total_mass` (float): Sum of all link masses (kg)
- `mass_tolerance` (float): ±10% allowed variance from estimated center of mass
- `joints` (Joint[]): List of actuated joints (name, type, limits, dynamics)
- `links` (Link[]): List of rigid bodies (collision geometry, inertia)
- `collision_geometry` (Geometry[]): Bounding boxes/capsules for collision detection
- `sensor_attachments` (SensorAttachment[]): Cameras, depth, IMU mounted on links
- `gait_parameters` (GaitParams): Stride length, swing height, step frequency (humanoid-specific)
- `center_of_mass` (float[3]): Computed center of mass position

**Relationships**:
- Contains: Joints (1..N), Links (1..N), Sensors (0..N)
- Placed in: Isaac Sim Scene (1..1)
- Navigated by: Nav2 Planner (in Chapter 9)
- Perceived by: Perception Pipeline (in Chapter 8)

**Validation Rules**:
- `urdf_path` must point to valid URDF file (checked at import)
- `total_mass` must match URDF (computed automatically; tolerance ±10%)
- All joint limits must be internally consistent (lower < upper)
- Collision geometry must not self-intersect (checked via physics engine)
- Gait parameters must respect joint limits (e.g., stride length < leg link length)
- Center of mass must be within support polygon for stability

**Gait Parameters** (humanoid-specific):
- `stride_length` (float): Distance between consecutive footsteps (0.3–0.8 m)
- `stride_width` (float): Distance between left/right feet (0.1–0.2 m)
- `swing_height` (float): Clearance during swing phase (0.05–0.15 m)
- `step_frequency` (float): Steps per second (1–2 Hz for humanoid bipeds)

**Example (Chapter 7, Example 7.2 - URDF Import)**:
```yaml
robot_id: humanoid-01
urdf_path: /models/humanoid_robot.urdf
base_link: pelvis
total_mass: 80.0  # kg, typical humanoid
collision_geometry:
  - type: capsule
    link: l_foot
    radius: 0.05
    height: 0.25
  - type: capsule
    link: r_foot
    radius: 0.05
    height: 0.25
gait_parameters:
  stride_length: 0.5
  stride_width: 0.15
  swing_height: 0.08
  step_frequency: 1.5
sensor_attachments:
  - type: camera
    link: head
    position: [0.05, 0, 0.1]  # relative to head link
  - type: imu
    link: pelvis
    position: [0, 0, 0]
```

---

## 3. Perception Pipeline

**Represents**: Isaac ROS GPU-accelerated VSLAM and sensor fusion stack

**Fields**:
- `pipeline_id` (string, unique): Identifier (e.g., "vslam-fusion-01")
- `vslam_type` (enum): "V-SLAM" (visual+depth) or "VI-SLAM" (visual+inertial)
- `depth_source` (enum): "camera" (RGB-D), "stereo" (stereo pair), "lidar" (range-based)
- `imu_source` (bool): Whether IMU is integrated (true → sensor fusion enabled)
- `input_topics` (string[]): ROS 2 topic names (e.g., ["/camera/rgb/image", "/camera/depth/image"])
- `output_odometry_topic` (string): ROS 2 topic for 6-DOF odometry (e.g., "/vslam/odometry")
- `output_map_topic` (string): ROS 2 topic for occupancy map (e.g., "/vslam/map")
- `gpu_compute_budget` (float): VRAM allocated (GB; typically 2–4 GB)
- `feature_detector` (enum): "SIFT", "ORB", "SuperPoint" (GPU-accelerated options)
- `tracking_confidence` (float): Threshold for feature matching (0.5–0.9; default 0.75)
- `loop_closure_enabled` (bool): Whether to detect loop closures (improves long-term accuracy)
- `output_frequency` (float): Odometry publication rate (Hz; ≥10 Hz required for Nav2)
- `localization_error` (float): Estimated trajectory error (m; target <5% of path length)

**Relationships**:
- Consumes: Robot sensors (camera, depth, IMU)
- Produces: Odometry (to Nav2 Planner), visual map
- Runs in: ROS 2 Humble environment
- Deployed on: RTX 4070 Ti+ (primary) or AWS cloud

**Validation Rules**:
- `depth_source` must match available sensors (no mismatch)
- `output_frequency` must be ≥10 Hz (Nav2 requirement)
- `gpu_compute_budget` ≤ available VRAM (8GB minimum, 24GB on RTX 4070 Ti+)
- `tracking_confidence` must be in [0.5, 0.9]
- `localization_error` target <5% (checked via Chapter 8 Exercise 1)
- All ROS 2 topics must follow naming conventions (start with "/", no spaces)

**Example (Chapter 8, Example 8.1 - VSLAM Pipeline)**:
```yaml
pipeline_id: vslam-01
vslam_type: VI-SLAM
depth_source: camera  # RGB-D camera
imu_source: true
input_topics:
  - /camera/rgb/image_raw
  - /camera/depth/image_raw
  - /imu/data
output_odometry_topic: /vslam/odometry
output_map_topic: /vslam/map
gpu_compute_budget: 3.0  # GB
feature_detector: SuperPoint
tracking_confidence: 0.75
loop_closure_enabled: true
output_frequency: 15.0  # Hz
localization_error: 0.03  # 3% of typical path
```

---

## 4. Navigation Goal & Path Planning Request

**Represents**: A request to Nav2 planner with start/goal poses and bipedal constraints

**Fields**:
- `goal_id` (string, unique): Identifier (e.g., "goal-kitchen-20240123")
- `start_pose` (Pose3D): Initial robot position and orientation (x, y, z, roll, pitch, yaw)
- `goal_pose` (Pose3D): Target position and orientation
- `costmap_resolution` (float): Costmap grid resolution (m; typically 0.05 m)
- `costmap_inflation_radius` (float): Obstacle inflation (m; humanoid footprint ≈0.3 m)
- `planner_type` (enum): "SMAC" (State Lattice), "NavFn" (Dijkstra), "THeta*" (optimal)
- `footstep_geometry` (Footprint): Polygon defining foot shape (for collision avoidance)
- `balance_constraints` (BalanceParams): Center of mass limits, friction requirements
- `max_planning_time` (float): Timeout for planning (s; default 2.0 s)
- `path_success` (bool): Whether planning succeeded (output)
- `planned_path` (Pose3D[]): Sequence of planned footstep poses (output)
- `execution_status` (enum): "planned", "executing", "succeeded", "failed" (output)
- `collision_free` (bool): Whether path is collision-free (output)

**Relationships**:
- Requested by: Nav2 client (navigation task)
- Consumes: VSLAM odometry (current pose)
- Produces: Collision-free path, velocity commands
- Validates against: Isaac Sim environment (Chapter 9)

**Validation Rules**:
- `costmap_inflation_radius` ≥ 0.25 m (minimum humanoid footprint)
- `max_planning_time` ≤ 5.0 s (real-time requirement)
- `path_success` = true when `collision_free` = true AND path leads to `goal_pose`
- All poses must be within environment bounds (checked against Isaac Sim scene)
- Footstep spacing must respect stride geometry (from Robot Model gait parameters)

**Example (Chapter 9, Example 9.3 - Global Planning)**:
```yaml
goal_id: goal-nav-001
start_pose:
  position: [0.0, 0.0, 0.0]
  orientation: [0.0, 0.0, 0.0]  # yaw=0 (facing forward)
goal_pose:
  position: [5.0, 3.0, 0.0]
  orientation: [0.0, 0.0, 0.785]  # yaw=45°
costmap_resolution: 0.05
costmap_inflation_radius: 0.3
planner_type: SMAC
footstep_geometry:
  foot_length: 0.25  # m
  foot_width: 0.10   # m
balance_constraints:
  max_slope: 20.0  # degrees
  min_friction: 0.5
max_planning_time: 2.0
# Outputs (filled by Nav2):
path_success: true
collision_free: true
execution_status: planned
planned_path:
  - position: [0.0, 0.0, 0.0]
  - position: [0.5, 0.3, 0.0]
  - position: [1.0, 0.6, 0.0]
  # ... more steps ...
  - position: [5.0, 3.0, 0.0]
```

---

## 5. Sensor & Measurement

**Represents**: Virtual sensor (camera, depth, IMU) attached to robot, producing measurements

**Fields**:
- `sensor_id` (string, unique): Identifier (e.g., "camera-head-1")
- `sensor_type` (enum): "camera" (RGB), "depth" (depth map), "imu" (accelerometer + gyro), "lidar"
- `parent_link` (string): Robot link to which sensor is attached
- `position_relative` (float[3]): Position relative to parent link (m)
- `orientation_relative` (float[4]): Orientation relative to parent link (quaternion)
- `output_topic` (string): ROS 2 topic name (e.g., "/camera/rgb/image_raw")
- `frame_id` (string): TF frame name (e.g., "camera_optical_frame")
- `publish_rate` (float): Publication frequency (Hz)

**Camera-Specific**:
- `image_resolution` (int[2]): [width, height] pixels
- `fov` (float): Horizontal field of view (degrees)
- `focal_length` (float): Intrinsic camera parameter (pixels)
- `lens_distortion` (bool): Whether to apply realistic distortion

**Depth-Specific**:
- `depth_range` (float[2]): [min, max] sensing distance (m)
- `depth_noise_stddev` (float): Standard deviation of depth noise (m; realistic: 0.01–0.05)

**IMU-Specific**:
- `accel_range` (float): Maximum acceleration measurement (m/s²; typ: 20–100)
- `gyro_range` (float): Maximum angular velocity (rad/s; typ: 10–200)
- `accel_noise_stddev` (float): Accelerometer noise (m/s²; typ: 0.01–0.1)
- `gyro_noise_stddev` (float): Gyroscope noise (rad/s; typ: 0.001–0.01)

**Example (Chapter 8, Example 8.2 - Depth Perception)**:
```yaml
sensor_id: depth-camera-1
sensor_type: depth
parent_link: head
position_relative: [0.05, 0.0, 0.0]
orientation_relative: [0, 0, 0, 1]  # identity
output_topic: /camera/depth/image_raw
frame_id: camera_depth_optical_frame
publish_rate: 30.0
depth_range: [0.1, 10.0]  # 10cm to 10m
depth_noise_stddev: 0.02  # 2cm standard deviation
```

---

## 6. Exercise Submission (Optional, for Learning Management)

**Represents**: Student submission of exercise code + results (for gradebook tracking)

**Fields**:
- `submission_id` (string, unique): Identifier (e.g., "student-001-ex7.1")
- `student_id` (string): Student identifier
- `exercise_id` (string): Reference to exercise (e.g., "chapter-7-ex-1")
- `chapter` (int): Chapter number (7, 8, or 9)
- `code_submission` (string): Student-written code (or file path)
- `execution_status` (enum): "success", "runtime_error", "validation_error"
- `execution_output` (string): stdout/stderr from test execution
- `metrics` (Metrics): Performance metrics (time, accuracy, etc.)
- `score` (float): Graded score (0.0–1.0)
- `timestamp` (datetime): Submission time
- `feedback` (string): Instructor feedback (optional)

**Metrics** (exercise-dependent):
- Chapter 7 Exercise 1: `physics_accuracy` (how closely simulation matches expected URDF)
- Chapter 7 Exercise 2: `dataset_size` (number of images generated), `export_time` (seconds)
- Chapter 8 Exercise 1: `trajectory_error` (absolute error in meters), `tracking_frequency` (Hz)
- Chapter 8 Exercise 2: `sensor_fusion_improvement` (% accuracy gain vs. single-sensor)
- Chapter 9 Exercise 1: `path_collision_free` (bool), `path_efficiency` (% of optimal length)
- Chapter 9 Exercise 2: `sim_to_real_success_rate` (% of behaviors that transferred)

**Validation Rules**:
- `execution_output` contains expected key phrases (e.g., "successful", "complete")
- `metrics` values within acceptable range (e.g., `trajectory_error` < 5% path length)
- `score` = 1.0 if all validation passes; 0.5 if partial; 0.0 if failed
- `timestamp` must be recent (within course window)

**Example (Chapter 7, Exercise 7.1 Submission)**:
```yaml
submission_id: student-001-ex7.1
student_id: student-001
exercise_id: chapter-7-ex-1
chapter: 7
code_submission: |
  # Student modifies physics parameters
  gravity = [0, 0, -9.81]
  friction = 0.8  # tuned value
  # ... rest of code
execution_status: success
metrics:
  physics_accuracy: 0.95  # 95% match to expected
  runtime_seconds: 12.3
timestamp: 2024-02-15T14:30:00Z
score: 0.95
feedback: "Great! Physics tuning matches expected behavior within tolerance."
```

---

## Entity Relationship Diagram (Conceptual)

```
┌─────────────────┐
│  Isaac Sim      │
│  Scene          │
└────────┬────────┘
         │ contains
         ├─► ┌──────────────┐
         │   │ Robot Model  │
         │   │ (URDF-based) │
         │   └──────┬───────┘
         │          │ has
         │          ├─► Joint (1..N)
         │          ├─► Link (1..N)
         │          └─► Sensor Attachment (0..N)
         │               │ mounted on
         │               └─► Sensor (camera, depth, IMU)
         │
         ├─► Sensor (camera, depth, IMU) ─┐
         │   (direct to scene)              │
         │                                  │
         └─► Asset (environmental)         │
             (obstacles, furniture, etc.)  │
                                           │
    ┌──────────────────────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Perception Pipeline  │
│ (Isaac ROS VSLAM)    │
└─────────┬────────────┘
          │ consumes
          ├─► Camera feed ─►
          ├─► Depth feed ──► Odometry (6-DOF)
          └─► IMU feed ────► Visual Map

    ┌─────────────────────┐
    │ Nav2 Planner        │
    └─────────┬───────────┘
              │ consumes
              ├─► Odometry (from VSLAM)
              ├─► Costmap (from environment)
              │ plans with
              └─► Navigation Goal
                  │ produces
                  └─► Collision-Free Path
                      │ executes via
                      └─► Robot Model (motor commands)
```

---

## Validation Checklist (Phase 1 Complete)

- [x] All entities have unique identifier fields
- [x] All relationships clearly defined
- [x] All validation rules traceable to specification requirements
- [x] Examples provided for each entity (from corresponding chapter/example)
- [x] Supports all 15-18 examples across Chapters 7, 8, 9
- [x] Data model compatible with ROS 2 Humble, Isaac Sim 2023.8+, Nav2 Humble
- [x] No circular dependencies; clear data flow

**Gate**: ✅ Phase 1 Data Model Complete. Ready for contracts/ and quickstart.md generation.
