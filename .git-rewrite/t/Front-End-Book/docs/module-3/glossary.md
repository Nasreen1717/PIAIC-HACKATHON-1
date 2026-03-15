# Module 3 Glossary

## Isaac Sim Terms

**Omniverse**: NVIDIA's platform for connecting graphics, simulation, and collaboration. Isaac Sim runs on Omniverse.

**USD (Universal Scene Description)**: Open-source file format for describing 3D scenes, assets, and animations. URDF robots are converted to USD for Isaac Sim.

**Physics Timestep**: Simulation step duration (typically 0.0083 seconds = 120 Hz). Smaller timesteps are more accurate but slower.

**Restitution**: Coefficient of elasticity (0-1). 0 = no bounce (inelastic), 1 = perfect bounce (elastic).

**Friction**: Material property defining resistance to sliding (0-1). Higher values increase grip.

**Gravity**: Acceleration due to gravity (default: 9.81 m/s² downward). Affects all objects in the scene.

**Synthetic Data**: Training data generated in simulation rather than collected from real-world sensors.

**Ground Truth**: Accurate reference values (e.g., robot pose, object location) known from simulation.

## ROS 2 & Isaac ROS Terms

**Topic**: One-way communication channel for publishing and subscribing to data streams.

**Service**: Request-response communication pattern in ROS 2.

**VSLAM (Visual SLAM)**: Visual Simultaneous Localization and Mapping using camera images for robot pose estimation and map building.

**VI-SLAM**: Visual-Inertial SLAM combining camera with IMU (accelerometer + gyroscope).

**Odometry**: Estimated robot pose from dead reckoning (sensors like wheels, cameras, IMU).

**Loop Closure**: Detection that robot has returned to previously visited location, correcting accumulated drift.

**TensorRT**: NVIDIA's inference optimization platform for deep learning models on GPU.

**GPU Acceleration**: Using GPU (graphics processor) for computation instead of CPU, typically 5-10x faster for perception tasks.

**Feature Detection**: Finding distinctive visual points in images (e.g., corners, edges) for tracking and SLAM.

**Depth Sensor**: Camera that measures distance to objects (e.g., RGB-D cameras, LiDAR).

## Nav2 & Navigation Terms

**Costmap**: 2D grid representing traversability of environment. Higher cost = less favorable path.

**Global Planner**: Computes optimal path from start to goal using costmap (relatively slower, less reactive).

**Local Planner**: Computes immediate motion commands to follow global path while avoiding obstacles (faster, reactive).

**Inflation**: Buffer zone around obstacles in costmap. Larger radius = safer but more constrained paths.

**Footstep Planning**: Discrete planning over valid foot placements, respecting stride and balance constraints.

**Bipedal**: Two-legged locomotion (humans, humanoid robots) vs. wheeled or quadruped robots.

**Balance Constraint**: Requirement that center of mass stays within support polygon (feet in contact with ground).

**Swing Phase**: Period when foot is not in contact with ground, moving from one step to next.

**Stance Phase**: Period when foot is in contact with ground, supporting robot weight.

## Robotics & Simulation Terms

**URDF (Unified Robot Description Format)**: XML format describing robot structure, joints, masses, and sensors.

**SDF (Simulation Description Format)**: Alternative robot description format (more detailed than URDF).

**Collision Detection**: Computing which objects are in contact and handling responses.

**Physics Engine**: Software simulating physical forces (gravity, friction, collisions) in virtual environment.

**Forward Kinematics**: Computing end-effector position from joint angles.

**Inverse Kinematics**: Computing joint angles needed to reach desired end-effector position.

**Sim-to-Real Transfer**: Deploying algorithms trained in simulation to real robots.

**Domain Randomization**: Varying simulation parameters randomly during training to improve robustness on real hardware.

**Hardware-in-the-Loop (HITL)**: Testing with real hardware components in simulation.

## Perception Terms

**RGB Image**: Red-Green-Blue color image from camera.

**Depth Map**: Image where pixel values represent distance to camera (grayscale or false color).

**Segmentation**: Labeling each pixel with semantic category (e.g., robot, obstacle, ground).

**Bounding Box**: Rectangle (xmin, ymin, xmax, ymax) around detected object in image.

**Intrinsic Parameters**: Camera properties (focal length, principal point) defining projection of 3D points to 2D pixels.

**Pose Estimation**: Computing 6-DOF position and orientation of object in 3D space.

**Optical Flow**: Apparent motion of pixels between consecutive images, useful for odometry.

**Feature Descriptor**: Vector representation of image patch for matching and tracking.

## GPU & Performance Terms

**VRAM (Video RAM)**: Memory on GPU, typically 8-48 GB for training/inference. Limited for batch processing.

**Throughput**: Number of samples processed per unit time (e.g., images per second).

**Latency**: Time delay from input to output (e.g., inference time in milliseconds).

**GPU Utilization**: Percentage of GPU compute capacity in use (0-100%).

**Memory Bandwidth**: Rate of data transfer to/from GPU memory (GB/s).

**Batching**: Processing multiple samples together for efficiency (higher throughput, higher latency).

**Mixed Precision**: Using lower precision (float16) for some operations to save memory and time.

## Safety & Real-World Terms

**Safety Factor**: Margin below hardware limits to ensure safe operation (e.g., velocity limits 20% below maximum).

**Emergency Stop (E-Stop)**: Hardware button immediately halting all motion.

**Tether**: Physical safety cable restraining robot during testing.

**Collision Detection**: Real-time sensing of unexpected contact with environment.

**Graceful Degradation**: System continues safe operation when components fail (e.g., fall safely, stop gracefully).

**Validation Protocol**: Systematic testing to ensure behaviors match expectations before hardware deployment.

## Module-Specific Terminology

**Boston Dynamics Atlas**: Humanoid robot used as reference for bipedal planning (2-legged, 6 DOF per leg).

**RTX 4070 Ti+**: High-end NVIDIA GPU with 24GB VRAM, suitable for real-time Isaac Sim and perception.

**AWS g5.2xlarge**: Cloud GPU instance with NVIDIA L40S GPU, ~90% performance of RTX 4070 Ti+ at lower cost.

**NVIDIA Isaac Cloud**: Managed cloud service for Isaac Sim and Isaac ROS, optimized by NVIDIA.

**Absolute Trajectory Error (ATE)**: Error metric measuring difference between estimated and ground-truth robot path.

**Relative Pose Error (RPE)**: Error in relative motion between consecutive poses (less sensitive to drift).

---

**Version**: Module 3 v1.0
**Last Updated**: 2026-01-23
**Contact**: robotics@example.com
