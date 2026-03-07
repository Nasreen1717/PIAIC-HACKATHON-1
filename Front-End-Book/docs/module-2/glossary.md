# Glossary: Module 2 - The Digital Twin

**Purpose**: Quick reference for key terms used throughout Module 2

---

## A

### Animation
The process of changing an object's properties (position, rotation, scale) over time to create motion. In Module 2, used to move robot links based on joint state data from Gazebo.

**Related**: [Chapter 5](chapter-5.md) - Real-Time Joint Animation from ROS 2

### ArticulationBody
A Unity component that represents a physically simulated joint. Used to synchronize joint states from Gazebo simulation with 3D robot animation in Unity.

**Related**: [Chapter 5](chapter-5.md) - Unity Rendering

---

## B

### Base Link
The root link of a robot kinematic chain (usually the main body or torso). All other links connect to it via joints. Defined in URDF.

**Example**: In a humanoid robot, "torso" is typically the base link.

**Related**: [Chapter 1 - URDF & Robot Description](../module-1/chapter-3.md), [Chapter 4](chapter-4.md)

### Bias (Sensor)
A systematic offset in sensor measurements. IMU sensors often have accelerometer/gyroscope bias that causes drift over time.

**Related**: [Chapter 6 - IMU & Motion Sensors](chapter-6.md)

### Bullet Physics Engine
An open-source physics simulation engine used by Gazebo. Simulates collisions, gravity, and rigid body dynamics.

**Alternative**: ODE (Open Dynamics Engine)

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

---

## C

### Camera (Sensor)
A simulated RGB-D (color + depth) camera in Gazebo that produces images and depth maps. Can be attached to robot links.

**Related**: [Chapter 6 - Camera & Depth Imaging](chapter-6.md)

### Collision Geometry
The shape used for physics collision detection in Gazebo. May differ from visual geometry for computational efficiency.

**Related**: [Chapter 4 - Loading & Running Simulations](chapter-4.md), [Chapter 1 - URDF](../module-1/chapter-3.md)

### Collision Detection
The process of identifying when two objects in simulation contact each other. Gazebo computes contact points, normals, and forces.

**Related**: [Chapter 4](chapter-4.md), [Collision Demo Example](../static/examples/module-2/chapter-4-gazebo/4-collision-demo.py)

### Contact Force
The force magnitude at a collision contact point. Published by Gazebo on `/gazebo/contact_states` topic.

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md)

---

## D

### Damping (Joint)
Friction coefficient that resists joint motion. Higher damping = more resistance to movement (energy dissipation).

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md), [Chapter 1 - URDF](../module-1/chapter-3.md)

### Depth Camera
A camera that measures distance to objects, producing a depth map where each pixel value = distance. Used for 3D perception.

**Related**: [Chapter 6 - Camera & Depth Imaging](chapter-6.md)

### Depth Image
Raw output from a depth camera showing distance measurements. Typically encoded as 16-bit or 32-bit values.

**Related**: [Chapter 6 - Camera & Depth Imaging](chapter-6.md)

### Digital Twin
A virtual representation of a physical robot that mirrors its behavior. Consists of physics simulation (Gazebo) + rendering (Unity) + sensor processing (ROS 2).

**Related**: [Module 2 Overview](intro.md)

---

## E

### EKF (Extended Kalman Filter)
A sensor fusion algorithm that combines noisy measurements from multiple sensors to estimate system state. Assumes linear process and measurement models.

**Related**: [Chapter 6 - Sensor Fusion & Data Integration](chapter-6.md)

### Effort (Joint)
The torque (for revolute joints) or force (for prismatic joints) currently applied to a joint. Published in ROS 2 `sensor_msgs/JointState`.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4 - Joint Control & Feedback](chapter-4.md)

---

## F

### FOV (Field of View)
The visible angle range of a camera in radians. Typical value: 1.5708 radians (~90 degrees).

**Related**: [Chapter 6 - Camera & Depth Imaging](chapter-6.md)

### Frame / Coordinate Frame
A named 3D coordinate system (origin, X/Y/Z axes) used to express positions and orientations. Gazebo and ROS 2 use multiple frames (base_link, odom, map, camera_frame, etc.).

**Related**: [Chapter 4 - Loading & Running Simulations](chapter-4.md), [ROS 2 TF Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/Tf2/Tf2.html)

### Friction (Joint)
Static friction coefficient that prevents a joint from moving under small forces. Related to but distinct from damping.

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md)

---

## G

### Gazebo
An open-source physics simulation and rendering platform. Used in Module 2 to simulate robot behavior (gravity, collisions, joint dynamics, sensors).

**Official Docs**: [Gazebo 11 Documentation](https://classic.gazebosim.org/tutorials)

**Related**: [Chapter 4](chapter-4.md)

### Gravity
Acceleration due to gravity. Default: 9.81 m/s² downward (0, 0, -9.81 in [x, y, z] format).

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

### GameObject
A fundamental entity in Unity representing any object in a scene (robot link, light, camera, UI element).

**Related**: [Chapter 5 - Importing URDF into Unity](chapter-5.md)

---

## H

### Headless Mode
Running Gazebo/simulation without a graphical UI. Requires X11 forwarding or VNC for remote systems.

**Related**: [Chapter 4 - Loading & Running Simulations](chapter-4.md#cloud-deployment)

---

## I

### IMU (Inertial Measurement Unit)
A sensor that measures acceleration (accelerometer), angular velocity (gyroscope), and sometimes magnetic heading (magnetometer).

**Related**: [Chapter 6 - IMU & Motion Sensors](chapter-6.md)

### Inertia (Link)
The resistance to rotational acceleration. Represented as a 3×3 inertia tensor (Ixx, Iyy, Izz) in URDF.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4](chapter-4.md)

### Inertial Frame
A reference frame where Newton's laws hold without apparent forces due to acceleration. Often synonymous with world/map frame.

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

---

## J

### Joint
A connection between two links that allows motion (revolute, prismatic) or is fixed. Defined in URDF with limits, dynamics, sensors.

**Types**: Revolute (rotational), Prismatic (linear), Fixed (no motion), Floating (free), Planar (2D)

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4 - Joint Control & Feedback](chapter-4.md)

### Joint Limit
Physical or software constraint on joint motion. Each joint has lower/upper position limits and maximum velocity/effort.

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md), [Chapter 1 - URDF](../module-1/chapter-3.md)

### Joint State
Current position, velocity, and effort of all robot joints. Published by Gazebo on `/joint_states` topic as `sensor_msgs/JointState` ROS 2 message.

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md), [Chapter 1 - URDF](../module-1/chapter-3.md)

---

## K

### Kinematic Chain
A sequence of links connected by joints. Describes the structure of a robot's "skeleton."

**Example**: Humanoid robot arm: base_link → shoulder → upper_arm → lower_arm → hand

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4](chapter-4.md)

---

## L

### Laser Scanner (2D/3D)
A sensor that measures distance to objects by scanning a line (2D) or plane (3D). Output is a LaserScan (2D) or PointCloud2 (3D) ROS 2 message.

**Related**: [Chapter 6 - LiDAR & Point Clouds](chapter-6.md)

### Lighting
3D rendering technique using light sources (directional, point, spot) to illuminate scenes. Affects visual realism but increases computation.

**Related**: [Chapter 5 - Materials, Lighting & Rendering Quality](chapter-5.md)

### Link (URDF)
A rigid body segment of a robot defined in URDF. Contains geometry (visual + collision), inertia, and mass properties.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4](chapter-4.md)

### LiDAR (Light Detection and Ranging)
A sensor that uses laser light to measure distances. Produces 3D point cloud data.

**Related**: [Chapter 6 - LiDAR & Point Clouds](chapter-6.md)

---

## M

### Material (Rendering)
Properties defining how a 3D surface appears: color, metallic value, roughness, normal maps. Used by rendering engine to compute shading.

**Related**: [Chapter 5 - Materials, Lighting & Rendering Quality](chapter-5.md)

### Message (ROS 2)
A data structure for communication between ROS 2 nodes. Examples: `sensor_msgs/JointState`, `sensor_msgs/Image`, `geometry_msgs/Twist`.

**Related**: [Chapter 1 - Communication Patterns](../module-1/chapter-2.md), [ROS 2 Messages Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Msg-and-Srv-Files.html)

### Mesh (3D)
A 3D geometric shape represented as triangles. Used for visual geometry in URDF and collision detection in Gazebo.

**Formats**: DAE (Collada), STL, OBJ

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 5 - Importing URDF into Unity](chapter-5.md)

---

## N

### Noise (Sensor)
Random variation in sensor measurements. Gazebo simulates realistic sensor noise to train robust perception algorithms.

**Types**: White noise, bias noise, quantization noise

**Related**: [Chapter 6 - Sensor Simulation in Gazebo](chapter-6.md), [Chapter 6 - IMU & Motion Sensors](chapter-6.md)

### Node (ROS 2)
A process running in ROS 2 that publishes/subscribes to topics or provides/calls services.

**Related**: [Chapter 1 - ROS 2 Fundamentals](../module-1/chapter-1.md)

---

## O

### ODE (Open Dynamics Engine)
An open-source physics simulation engine used by Gazebo. Simulates rigid body dynamics and collisions.

**Alternative**: Bullet physics engine

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

### Odometry
Estimation of robot position/orientation by integrating sensor measurements (wheel encoders, IMU). May drift over time.

**Related**: [Chapter 4 - Joint Control & Feedback](chapter-4.md), [Chapter 6 - Sensor Fusion & Data Integration](chapter-6.md)

---

## P

### PBR (Physically-Based Rendering)
Rendering technique that uses physically accurate material properties (metallic, roughness, albedo) for realistic appearance.

**Related**: [Chapter 5 - Materials, Lighting & Rendering Quality](chapter-5.md)

### Physics Engine
Software that simulates realistic physical behavior (gravity, collisions, forces, friction). Gazebo uses ODE or Bullet.

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

### Physics Timestep
The discrete time interval at which the physics simulation updates. Default: 0.001 seconds (1000 Hz). Smaller = more accurate but slower.

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

### Plugin (Gazebo)
A shared library that extends Gazebo functionality. Examples: sensor plugins (camera, laser), controller plugins, world plugins.

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

### Point Cloud
3D data representation as a collection of points in space, each with (x, y, z) coordinates. Often includes intensity/color. ROS 2 message type: `sensor_msgs/PointCloud2`.

**Related**: [Chapter 6 - LiDAR & Point Clouds](chapter-6.md)

### Position (Joint)
Current angle of a revolute joint (radians) or displacement of a prismatic joint (meters). Constrained by joint limits.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4 - Joint Control & Feedback](chapter-4.md)

---

## Q

### Quaternion
A 4-component representation of 3D rotation (w, x, y, z). Used in ROS 2 to avoid gimbal lock. Can be converted to Euler angles (roll, pitch, yaw).

**Related**: [Chapter 6 - IMU & Motion Sensors](chapter-6.md), [ROS 2 TF Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/Tf2/Tf2.html)

---

## R

### Rendering
The process of computing pixel colors from 3D scene data (geometry, materials, lighting, camera view). Produces 2D images for display.

**Related**: [Chapter 5 - High-Fidelity Rendering with Unity](chapter-5.md)

### Revolute Joint
A joint that rotates around an axis. Motion is angular (radians). Examples: shoulder, elbow, hip joints.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4 - Joint Control & Feedback](chapter-4.md)

### ROS 2 (Robot Operating System 2)
A middleware framework for building modular robotic software. Provides pub/sub messaging, services, parameter server, launch files.

**Related**: [Chapter 1 - ROS 2 Fundamentals](../module-1/chapter-1.md)

### RViz2 (ROS Visualization 2)
A 3D visualization tool for ROS 2 that displays robot state, sensor data, transforms, and trajectories.

**Related**: [Chapter 4 - Common Issues & Debugging](chapter-4.md)

---

## S

### Sensor (Gazebo)
A simulated hardware sensor that produces ROS 2 messages. Examples: camera, laser (LiDAR), IMU, force/torque sensors.

**Related**: [Chapter 4 - Sensor Simulation Basics](chapter-4.md), [Chapter 6](chapter-6.md)

### SDF (Simulation Description Format)
XML-based format for describing simulated robots, objects, and worlds. Extended version of URDF with physics properties.

**Related**: [Chapter 4 - URDF & SDF: From Robot Description to Simulation](chapter-4.md)

### Sensor Fusion
Process of combining measurements from multiple sensors to estimate system state more accurately than any single sensor.

**Related**: [Chapter 6 - Sensor Fusion & Data Integration](chapter-6.md)

---

## T

### Topic (ROS 2)
A named communication channel for pub/sub messaging between ROS 2 nodes. Example: `/joint_states`, `/camera/image_raw`.

**Related**: [Chapter 1 - Communication Patterns](../module-1/chapter-2.md)

### Transform (TF / Frame Transform)
The relative position and orientation between two coordinate frames. Expressed as translation (x, y, z) and rotation (quaternion or rotation matrix).

**Related**: [Chapter 4 - Loading & Running Simulations](chapter-4.md), [ROS 2 TF2 Documentation](https://docs.ros.org/en/humble/Concepts/Intermediate/Tf2/Tf2.html)

---

## U

### URDF (Unified Robot Description Format)
XML-based format describing a robot's structure (links, joints, geometry, sensors). Human-readable and machine-parseable.

**Related**: [Chapter 1 - URDF & Robot Description](../module-1/chapter-3.md), [Chapter 4 - URDF & SDF](chapter-4.md), [Chapter 5 - Importing URDF into Unity](chapter-5.md)

### Unity
A professional 3D game engine and development platform used for rendering and interactive visualization in this module.

**Version Used**: Unity 2022.3 LTS

**Related**: [Chapter 5 - High-Fidelity Rendering with Unity](chapter-5.md)

---

## V

### Velocity (Joint)
Rate of change of joint position. Angular velocity (rad/s) for revolute joints, linear velocity (m/s) for prismatic joints.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 4 - Joint Control & Feedback](chapter-4.md)

### Visualization Geometry
The 3D shape rendered for visual display. May differ from collision geometry for performance or aesthetic reasons.

**Related**: [Chapter 1 - URDF](../module-1/chapter-3.md), [Chapter 5](chapter-5.md)

---

## W

### World File (SDF)
An SDF XML file that defines a complete simulation environment: ground plane, objects, robots, lights, physics parameters, plugins.

**Related**: [Chapter 4 - Loading & Running Simulations](chapter-4.md)

### World Frame
The global coordinate system in Gazebo simulation. Origin typically at (0, 0, 0) with gravity pointing down (-Z direction).

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md)

---

## X, Y, Z

### X, Y, Z Axes
Standard 3D Cartesian coordinate system:
- **X**: Forward direction (red in RViz2)
- **Y**: Left direction (green in RViz2)
- **Z**: Up direction (blue in RViz2)

**Convention**: Right-handed coordinate system

**Related**: [Chapter 4 - Gazebo Architecture](chapter-4.md), [ROS 2 Coordinate Conventions](https://docs.ros.org/en/humble/Concepts/Intermediate/Transforms.html)

---

## Cross-References by Chapter

### Chapter 4 - Physics Simulation
[Animation](#animation), [Base Link](#base-link), [Bullet](#bullet-physics-engine), [Collision Geometry](#collision-geometry), [Collision Detection](#collision-detection), [Contact Force](#contact-force), [Damping](#damping-joint), [Digital Twin](#digital-twin), [Effort](#effort-joint), [Frame](#frame--coordinate-frame), [Friction](#friction-joint), [Gazebo](#gazebo), [Gravity](#gravity), [Headless Mode](#headless-mode), [IMU](#imu-inertial-measurement-unit), [Inertia](#inertia-link), [Joint](#joint), [Joint Limit](#joint-limit), [Joint State](#joint-state), [Kinematic Chain](#kinematic-chain), [Link](#link-urdf), [ODE](#ode-open-dynamics-engine), [Physics Engine](#physics-engine), [Physics Timestep](#physics-timestep), [Plugin](#plugin-gazebo), [Position](#position-joint), [ROS 2](#ros-2-robot-operating-system-2), [RViz2](#rviz2-ros-visualization-2), [SDF](#sdf-simulation-description-format), [Topic](#topic-ros-2), [Transform](#transform-tf--frame-transform), [URDF](#urdf-unified-robot-description-format), [Velocity](#velocity-joint), [Visualization Geometry](#visualization-geometry), [World File](#world-file-sdf), [World Frame](#world-frame)

### Chapter 5 - Rendering
[Animation](#animation), [ArticulationBody](#articulation-body), [GameObject](#gameobject), [Lighting](#lighting), [Material](#material-rendering), [Mesh](#mesh-3d), [PBR](#pbr-physically-based-rendering), [Rendering](#rendering), [Transform](#transform-tf--frame-transform), [URDF](#urdf-unified-robot-description-format), [Unity](#unity), [Visualization Geometry](#visualization-geometry)

### Chapter 6 - Sensors
[Bias](#bias-sensor), [Camera](#camera-sensor), [Depth Camera](#depth-camera), [Depth Image](#depth-image), [EKF](#ekf-extended-kalman-filter), [FOV](#fov-field-of-view), [Frame](#frame--coordinate-frame), [IMU](#imu-inertial-measurement-unit), [Joint State](#joint-state), [Laser Scanner](#laser-scanner-2d3d), [LiDAR](#lidar-light-detection-and-ranging), [Message](#message-ros-2), [Noise](#noise-sensor), [Odometry](#odometry), [Point Cloud](#point-cloud), [Quaternion](#quaternion), [Sensor](#sensor-gazebo), [Sensor Fusion](#sensor-fusion), [Topic](#topic-ros-2), [Transform](#transform-tf--frame-transform)

---

**Last Updated**: 2026-01-22

**Citation**: Glossary terms aligned with official ROS 2, Gazebo, and Unity documentation standards.
