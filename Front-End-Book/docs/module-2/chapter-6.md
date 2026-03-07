# Chapter 6: Simulate Sensors for Perception

**Chapter Status**: 🚀 Perception Systems
**Duration**: 10-12 hours of study
**Prerequisites**: Chapters 4-5 (Gazebo physics, Unity rendering), basic linear algebra

---

## Introduction: Why Sensors Matter

In Chapters 4 and 5, you built a **digital twin** that accurately simulates robot physics and renders beautiful 3D visualizations. But there's a critical missing piece: **perception**.

Think about how real robots work:

> A real autonomous robot doesn't move by magic. It:
> 1. **Senses** the environment (cameras, lidar, IMU)
> 2. **Processes** sensor data to build internal models
> 3. **Plans** actions based on understanding
> 4. **Acts** to achieve goals
> 5. **Observes** results via sensors → loop back to step 1

**Without sensors**, you only have half a digital twin!

### Why Simulate Sensors?

**In real robotics development, you need:**
- 🎥 **Camera data** to test vision algorithms (object detection, lane following, etc.)
- 📡 **LiDAR** for 3D scene understanding and navigation
- 📊 **IMU** for motion estimation and localization
- 🔗 **Sensor fusion** to combine multiple sensors for robust perception

**Simulating sensors allows you to:**

✅ **Test perception algorithms** before field deployment
✅ **Generate realistic training data** for machine learning
✅ **Validate sensor fusion** without expensive hardware
✅ **Iterate quickly** (simulation is 1000x faster than real-world)
✅ **Stress test** with perfect ground truth (impossible in real world)

### Real-World Example

Consider an autonomous delivery robot navigating a warehouse:

```
Real Robot Flow:
┌──────────────────────────────────────────────────────┐
│ 1. Sensors capture: RGB camera, LiDAR, IMU, GPS      │
│ 2. Sensor fusion: Estimate position + obstacles      │
│ 3. Planner: Compute collision-free path              │
│ 4. Controller: Execute motion commands                │
│ 5. Sensors loop back: Verify actual vs. planned      │
└──────────────────────────────────────────────────────┘
     Timeline: Real-time, unpredictable, expensive

Digital Twin (Sim) Flow:
┌──────────────────────────────────────────────────────┐
│ 1. Gazebo simulates sensors with 100% accuracy       │
│ 2. Perfect ground truth available for validation      │
│ 3. Same algorithms as real robot, no modification    │
│ 4. Instant replay, pause, inspect any moment         │
│ 5. Test edge cases (darkness, fog, interference)     │
└──────────────────────────────────────────────────────┘
     Timeline: Can run >1000x faster than real-time!
```

### Learning Objectives (SMART)

By end of Chapter 6, you will be able to:

1. **Understand** sensor simulation in Gazebo:
   - How Gazebo plugins simulate realistic sensor behavior
   - Sensor noise modeling (measurement noise, bias, drift)
   - Frame transformations and coordinate conventions

2. **Implement** multi-sensor ROS 2 pipelines:
   - Subscribe to camera, lidar, and IMU topics
   - Process sensor data (image filtering, point cloud downsampling)
   - Handle different message types (Image, PointCloud2, Imu)

3. **Process** sensor data with open-source tools:
   - OpenCV for image processing
   - PCL (Point Cloud Library) for 3D data
   - NumPy/SciPy for signal processing

4. **Visualize** sensor data professionally:
   - RViz2 configuration for multi-sensor display
   - Custom visualization in Python (matplotlib)
   - Real-time sensor fusion displays

5. **Evaluate** sensor performance:
   - Measure accuracy (compare to ground truth)
   - Assess noise characteristics
   - Validate sensor fusion results

6. **Design** sensor fusion systems:
   - Extended Kalman Filter (EKF) basics
   - Multi-sensor alignment (time sync)
   - Uncertainty quantification

---

## Key Motivation: The Perception Challenge

### Why Sensors Are Hard to Simulate

Gazebo faces a tradeoff:
- **Too realistic**: Simulator becomes slow, hard to reproduce results
- **Too simple**: Results don't transfer to real robots

**This chapter teaches the Goldilocks zone**: Realistic enough to learn, fast enough to iterate.

### Sensor Types We'll Cover

| Sensor | Use Case | Challenge |
|--------|----------|-----------|
| **RGB Camera** | Object detection, SLAM, navigation | High data rate (30 MB/s per camera), real-time processing |
| **Depth Camera** | 3D scene understanding, grasping | Noisy at distance, fails in darkness, reflective surfaces |
| **2D LiDAR** | Planar obstacle detection, navigation | Limited FOV, not for 3D mapping |
| **3D LiDAR** | Dense 3D mapping, autonomous driving | Expensive, high data rate, motion artifact-prone |
| **IMU** | Motion estimation, stability, odometry | Drift, bias, orientation ambiguity (gimbal lock) |
| **Combination (Fusion)** | Robust perception despite single failures | Complexity, time synchronization, association |

---

## Chapter Roadmap

```
Chapter 6: Sensor Simulation & Perception
│
├─ Section 1: Sensor Simulation in Gazebo
│  └─ Plugins, noise modeling, frame transforms
│
├─ Section 2: Camera & Depth Imaging
│  └─ RGB-D cameras, depth encoding, point clouds from depth
│
├─ Section 3: LiDAR & Point Clouds
│  └─ 2D/3D scanners, PointCloud2 messages, visualization
│
├─ Section 4: IMU & Motion Sensors
│  └─ Accelerometer, gyroscope, integration, odometry
│
├─ Section 5: Sensor Fusion & Data Integration
│  └─ EKF principles, time synchronization, data association
│
├─ Section 6: Processing & Visualization
│  └─ Filters, downsampling, RViz2, custom plots
│
└─ Exercises 6.1 & 6.2
   ├─ Exercise 6.1 (Guided): Multi-sensor data capture
   └─ Exercise 6.2 (Semi-open): Sensor fusion pipeline
```

---

## Key Concepts Preview

### Sensor Noise & Reality

**Ideal sensor** (math textbook):
```
measurement = true_value
```

**Real sensor** (physics):
```
measurement = true_value + measurement_noise + bias + drift
```

**Example**: An IMU accelerometer reading Earth's gravity:

Ideal: `[0, 0, 9.81]` m/s²

Real: `[0.003, -0.002, 9.812]` m/s² + white noise ± 0.005 + slow bias drift

### Message Types You'll Use

**ROS 2 Messages** for different sensors:

```python
# Camera image
sensor_msgs.Image:
  header (timestamp, frame_id)
  height, width, encoding
  data (pixel bytes)

# Point cloud
sensor_msgs.PointCloud2:
  header (timestamp, frame_id)
  points (x, y, z coordinates)
  channels (intensity, rgb, etc.)

# IMU reading
sensor_msgs.Imu:
  header
  orientation (quaternion)
  angular_velocity
  linear_acceleration
  covariance matrices (uncertainty)

# Laser scan (2D lidar)
sensor_msgs.LaserScan:
  header
  angle_min, angle_max, angle_increment
  ranges (distance array)
  intensities
```

### Coordinate Frames

Robots use multiple coordinate frames:

```
World Frame (Global):
  origin at fixed location
  Z-up, X-forward (ROS convention)

Robot Base Frame:
  origin at robot center
  moves with robot

Sensor Frames:
  camera_optical_frame
  lidar_frame
  imu_frame

Transformation (TF):
  Converts between frames via:
  - Translation (3D position)
  - Rotation (quaternion or matrix)
```

**Why it matters**: A point at `[1, 0, 0]` in camera frame might be `[0.5, 2.1, 0.3]` in world frame!

---

## Technologies & Tools

### Gazebo Sensor Plugins

Gazebo includes plugins that simulate:
- **Camera plugin**: Ray-cast raytracing → RGB image
- **GPU Ray plugin**: GPU-accelerated lidar simulation (fast!)
- **IMU plugin**: Integrates physics accelerations/angular velocities

### Processing Libraries

**Python libraries** you'll use:
- **OpenCV** (cv2): Image processing, feature detection
- **PCL (Point Cloud Library)**: 3D point cloud filtering/segmentation
- **NumPy/SciPy**: Linear algebra, signal processing, statistics
- **ROS 2 geometry2**: Frame transformations (TF2)

### Visualization Tools

- **RViz2**: Official ROS 2 3D visualization (point clouds, images, transforms)
- **Matplotlib**: Python plotting (sensor data graphs)
- **Custom Python**: Your own visualization UIs

---

## Real-World Analogies

### Sensor Fusion = Human Perception

How do YOU navigate in darkness?
1. **Eyes (vision)**: Best in bright light, fails in darkness
2. **Ears (audio)**: Detects obstacles via echos
3. **Proprioception (body sense)**: Knows arm position without looking
4. **Vestibular (inner ear)**: Senses motion and balance

**Together**: More robust than any single sense!

**Robots do the same**: Fuse camera + lidar + IMU for robust navigation.

### Kalman Filter = Prediction Game

Imagine tracking a moving ball:
1. **Sensor says**: Ball at `[0.5, 1.2, 0.0]` (noisy measurement)
2. **Physics knows**: Ball moving at `[1.0, 0.5, 0.0]` m/s
3. **Fusion predicts**: Ball will be at `[1.5, 1.7, 0.0]` next frame

**Kalman Filter** optimally balances:
- Trust sensor measurements (might be correct)
- Trust physics model (might be more accurate)

Result: Smooth, accurate state estimate despite noisy sensors!

---

## Next Steps

Ready to dive deep? Let's start with **Section 1: Sensor Simulation in Gazebo**. We'll learn how to add sensors to your robot and understand the noise characteristics that make simulations realistic.

Then we'll process that data in ROS 2 to build perception pipelines!

---

**Let's begin!** Continue to [Section 1: Sensor Simulation in Gazebo](#section-1-sensor-simulation-in-gazebo).

---

## Section 1: Sensor Simulation in Gazebo

**Estimated Duration**: 2 hours
**Learning Outcomes**:
- Understand Gazebo sensor plugins and how they work
- Add sensors to robot URDF descriptions
- Configure noise, update rates, and parameters
- Verify sensors are publishing correctly in ROS 2

### 1.1 Gazebo Sensor Plugins Overview

Gazebo simulates sensors through **plugins** that:
1. **Ray-cast** rays from sensor location
2. **Detect** what they hit (distances, colors, etc.)
3. **Add noise** to make realistic
4. **Publish** ROS 2 messages

**Common Gazebo sensor plugins**:

| Plugin | What It Simulates | Output | Speed |
|--------|------------------|--------|-------|
| **camera** | RGB color camera | sensor_msgs/Image | Moderate (CPU) |
| **gpu_ray** | LiDAR scanner | sensor_msgs/LaserScan or PointCloud2 | Fast (GPU) |
| **imu** | Accelerometer + gyroscope | sensor_msgs/Imu | Very fast (direct integration) |
| **contact** | Touch/collision sensor | gazebo_msgs/ContactsState | Very fast (physics-based) |

### 1.2 Adding Sensors to URDF

**Example: Adding camera to humanoid head**

```xml
<?xml version="1.0"?>
<robot name="humanoid_with_sensors">
  <link name="head">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" iyy="0.01" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry><sphere radius="0.1"/></geometry>
    </visual>
  </link>

  <!-- Camera sensor -->
  <joint name="head_camera_joint" type="fixed">
    <parent link="head"/>
    <child link="camera_link"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
  </joint>

  <link name="camera_link">
    <inertial>
      <mass value="0.05"/>
      <inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <!-- Gazebo camera plugin configuration -->
  <gazebo reference="camera_link">
    <sensor type="camera" name="camera_sensor">
      <update_rate>30.0</update_rate>  <!-- 30 Hz publish rate -->
      <camera name="camera">
        <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>  <!-- RGB color -->
        </image>
        <clip>
          <near>0.02</near>  <!-- 2 cm minimum distance -->
          <far>100</far>     <!-- 100 m maximum distance -->
        </clip>
        <noise>
          <type>gaussian</type>
          <mean>0.0</mean>
          <stddev>0.007</stddev>  <!-- Gaussian noise, ±1% -->
        </noise>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>robot</namespace>
          <remapping>~/image_raw:=camera/image_raw</remapping>
          <remapping>~/camera_info:=camera/camera_info</remapping>
        </ros>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

### 1.3 Sensor Noise Modeling

**Why add noise?**

Simulated sensors without noise are *unrealistically perfect*. Real sensors have:

```
True Value: 1.5 m (distance to obstacle)
Real Sensor Reading:
  - Measurement noise: ±0.02 m
  - Bias: +0.01 m (systematic error)
  - Drift: Slowly changes ±0.001 m/hour (bias instability)

Result: Reading varies: 1.48 m, 1.52 m, 1.53 m, 1.49 m, ...
        Average: 1.51 m (true value + bias)
```

**Noise types in Gazebo**:

1. **Gaussian (white noise)**
   ```xml
   <noise>
     <type>gaussian</type>
     <mean>0.0</mean>
     <stddev>0.01</stddev>  <!-- 1-sigma uncertainty -->
   </noise>
   ```

2. **Gaussian quantized** (discrete readings)
3. **Custom distributions**

**Realistic sensor specs**:

| Sensor | Typical Noise |
|--------|--------------|
| RGB camera | 0.5-1% pixel variation |
| LiDAR | 0.02-0.05 m range error + angular error |
| IMU accelerometer | ±0.005 m/s² |
| IMU gyroscope | ±0.01 rad/s |

### 1.4 Coordinate Frames & Transforms

**Key concept**: Sensors don't always point forward!

```
Robot Base Frame:
  ├─ Camera mounted facing forward
  │  └─ camera_optical_frame (Z points out, X right, Y down)
  ├─ Front LiDAR mounted on front bumper
  │  └─ front_lidar_frame
  └─ IMU mounted at center
     └─ imu_frame
```

**Why frames matter**: To fuse data, all measurements must be in same frame.

Gazebo handles transforms via **TF2** (Transform Library):
- Publishes frame relationships automatically
- Available in `/tf` and `/tf_static` topics

### 1.5 Verify Sensor Publication

**Check what Gazebo is publishing**:

```bash
# List all topics
ros2 topic list | grep -E "(camera|lidar|imu)"

# Expected output:
# /robot/camera/image_raw          (Image data)
# /robot/camera/camera_info        (Calibration)
# /robot/front_lidar/scan          (LaserScan)
# /robot/imu/data                  (Imu message)
# /tf, /tf_static                  (Transforms)

# Monitor one topic
ros2 topic hz /robot/camera/image_raw
# Should show ~30 Hz for camera (or whatever you set)

# Inspect message structure
ros2 topic echo /robot/camera/camera_info --once
# Shows camera intrinsics (focal length, principal point, etc.)
```

---

## Section 2: Camera & Depth Imaging

**Estimated Duration**: 2 hours
**Learning Outcomes**:
- Understand RGB vs. depth vs. RGB-D cameras
- Process depth images to point clouds
- Handle camera intrinsics for accurate 3D reconstruction

### 2.1 RGB Camera Basics

**RGB Camera in Gazebo**:
- Simulates ray-casting through virtual scene
- Returns color values (R, G, B) for each pixel
- Can process with OpenCV for object detection, etc.

**Important camera properties**:

```xml
<camera>
  <horizontal_fov>1.047</horizontal_fov>  <!-- Field of view (radians) -->
  <image>
    <width>640</width>   <!-- Horizontal resolution -->
    <height>480</height> <!-- Vertical resolution -->
    <format>R8G8B8</format>  <!-- Color format (RGB) -->
  </image>
  <clip>
    <near>0.02</near>   <!-- Minimum depth -->
    <far>100</far>      <!-- Maximum depth -->
  </clip>
</camera>
```

### 2.2 Depth Cameras (RGB-D)

**Depth camera** = RGB camera + depth map:
- **RGB channel**: Color image (same as above)
- **Depth channel**: Per-pixel distance in meters

**Gazebo depth camera configuration**:

```xml
<gazebo reference="camera_link">
  <sensor type="depth_camera" name="depth_camera">
    <update_rate>30.0</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R32F</format>  <!-- Depth as 32-bit float (meters) -->
      </image>
      <clip>
        <near>0.3</near>   <!-- ~30 cm minimum depth -->
        <far>10</far>      <!-- 10 m maximum depth -->
      </clip>
      <noise>
        <type>gaussian</type>
        <stddev>0.05</stddev>  <!-- 5 cm depth noise (typical for depth cameras) -->
      </noise>
    </camera>
  </sensor>
</gazebo>
```

### 2.3 Converting Depth to Point Clouds

**Point Cloud**: 3D array of (x, y, z) coordinates.

**Process**:
1. Get depth image (640×480 matrix of depths)
2. Get camera intrinsics (focal length, principal point)
3. For each pixel, compute 3D position:

```python
import numpy as np

def depth_to_pointcloud(depth_image, camera_intrinsics):
    """
    Convert depth image to 3D point cloud.

    Args:
        depth_image: (height, width) array of depth values (meters)
        camera_intrinsics: dict with 'fx', 'fy', 'cx', 'cy'

    Returns:
        points: (height*width, 3) array of 3D points
    """
    height, width = depth_image.shape

    # Create coordinate grids for pixel positions
    x = np.arange(0, width)
    y = np.arange(0, height)
    xx, yy = np.meshgrid(x, y)

    # Get depth values
    z = depth_image

    # Compute 3D coordinates using camera intrinsics
    fx = camera_intrinsics['fx']
    fy = camera_intrinsics['fy']
    cx = camera_intrinsics['cx']
    cy = camera_intrinsics['cy']

    # Deproject pixel coordinates to 3D
    x_3d = (xx - cx) * z / fx
    y_3d = (yy - cy) * z / fy
    z_3d = z

    # Stack into point cloud
    points = np.stack([x_3d.ravel(), y_3d.ravel(), z_3d.ravel()], axis=1)

    return points
```

### 2.4 Camera Intrinsics

**Camera intrinsics** = Optical properties of camera:

```
Intrinsic Matrix K:
┌        ┐
│ fx  0  cx │
│  0  fy cy │
│  0  0   1 │
└        ┘

Where:
- fx, fy = focal lengths (pixels)
- cx, cy = principal point (image center)
```

**Typical values for 640×480 camera**:
- fx, fy ≈ 400-500 pixels (depends on lens)
- cx = 320 pixels (half width)
- cy = 240 pixels (half height)

Gazebo provides intrinsics via `camera_info` topic.

---

## Section 3: LiDAR & Point Clouds

**Estimated Duration**: 2.5 hours
**Learning Outcomes**:
- Understand 2D vs. 3D LiDAR
- Process PointCloud2 messages
- Filter and downsample point clouds for real-time processing
- Visualize in RViz2

### 3.1 2D LiDAR (Planar Laser Scanner)

**2D LiDAR** = Ray scanner in a single plane:
- Emits laser in arc (e.g., 180° scan)
- Measures distance to first obstacle
- Result: 1D array of distances (range array)

**Gazebo SDF for 2D LiDAR**:

```xml
<gazebo reference="base_link">
  <sensor type="ray" name="laser_scan">
    <pose>0 0 0.3 0 0 0</pose>  <!-- Mounted 30 cm above base -->
    <update_rate>10.0</update_rate>  <!-- 10 Hz -->
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>    <!-- 360 rays -->
          <resolution>1.0</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -180°-->
          <max_angle>3.14159</max_angle>   <!-- +180°-->
        </horizontal>
      </scan>
      <range>
        <min>0.05</min>      <!-- 5 cm min range -->
        <max>10.0</max>      <!-- 10 m max range -->
        <resolution>0.01</resolution>
      </range>
      <noise>
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.03</stddev>  <!-- 3 cm noise -->
      </noise>
    </ray>
    <plugin name="laserscan_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
    </plugin>
  </sensor>
</gazebo>
```

**LaserScan message** structure:
```python
from sensor_msgs.msg import LaserScan

msg.header.stamp          # Timestamp
msg.header.frame_id       # "base_scan" (sensor frame)
msg.angle_min             # -3.14159 rad (-180°)
msg.angle_max             # 3.14159 rad (+180°)
msg.angle_increment       # Step between rays (~0.017 rad for 360 rays)
msg.time_increment        # Time between rays (for moving sensor)
msg.scan_time             # Total time for one scan
msg.range_min             # 0.05 m
msg.range_max             # 10.0 m
msg.ranges[i]             # Distance (meters) for ray i
msg.intensities[i]        # Optional: reflectivity (0-1)
```

### 3.2 3D LiDAR (Point Cloud)

**3D LiDAR** = Multiple 2D scans stacked vertically:
- Velodyne, Ouster, etc.
- Outputs **point cloud** (3D array of x, y, z)
- Higher data rate and density than 2D

**3D LiDAR in Gazebo**:

```xml
<gazebo reference="base_link">
  <sensor type="gpu_ray" name="gpu_lidar">
    <!-- gpu_ray is GPU-accelerated, much faster than ray -->
    <pose>0 0 0.5 0 0 0</pose>
    <update_rate>20.0</update_rate>  <!-- 20 Hz -->
    <ray>
      <scan>
        <horizontal>
          <samples>1024</samples>  <!-- More rays for 3D -->
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
        <vertical>
          <samples>64</samples>    <!-- 64 vertical channels (like Velodyne) -->
          <min_angle>-0.436</min_angle>  <!-- -25° -->
          <max_angle>0.349</max_angle>   <!-- +20° -->
        </vertical>
      </scan>
      <range>
        <min>0.1</min>
        <max>120.0</max>
      </range>
      <noise>
        <type>gaussian</type>
        <stddev>0.05</stddev>
      </noise>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=points</remapping>
      </ros>
      <output_type>sensor_msgs/PointCloud2</output_type>
    </plugin>
  </sensor>
</gazebo>
```

### 3.3 PointCloud2 Message Format

**PointCloud2** = Efficient binary format for 3D points:

```python
from sensor_msgs.msg import PointCloud2
import numpy as np

# Extract points from PointCloud2
def pointcloud2_to_numpy(cloud_msg):
    """
    Convert ROS 2 PointCloud2 message to NumPy array.
    """
    # Create structured array from raw data
    points = np.frombuffer(cloud_msg.data, dtype=np.float32)
    points = points.reshape(-1, 3)  # Reshape to (N, 3) = N points with (x, y, z)
    return points

# Process: Filter by distance
def filter_by_range(points, max_range=10.0):
    """Keep only points within max_range."""
    distances = np.linalg.norm(points, axis=1)
    mask = distances <= max_range
    return points[mask]

# Usage
subscriber = node.create_subscription(PointCloud2, "/lidar/points", callback)

def callback(msg):
    points = pointcloud2_to_numpy(msg)       # Get NumPy array
    filtered = filter_by_range(points, 10.0) # Filter
    print(f"Cloud has {len(points)} points, {len(filtered)} within 10m")
```

### 3.4 Point Cloud Processing & Visualization

**Common point cloud operations**:

1. **Downsampling** (reduce points for speed):
   ```python
   # Voxel grid filter: keep 1 point per 0.05m×0.05m×0.05m cube
   from pcl import PointCloud
   cloud = PointCloud(points)
   cloud_filtered = cloud.make_voxel_grid_filter()
   cloud_filtered.set_leaf_size(0.05, 0.05, 0.05)
   filtered_cloud = cloud_filtered.filter()
   ```

2. **Statistical outlier removal**:
   ```python
   # Remove isolated noisy points
   statistical_outlier = cloud.make_statistical_outlier_removal()
   statistical_outlier.set_mean_k(50)  # Check 50 nearest neighbors
   statistical_outlier.set_std_dev_mul_thresh(1.0)  # Remove if 1σ away
   ```

3. **Visualization in RViz2**:
   - Add new display → PointCloud2
   - Topic: `/lidar/points`
   - Color transformer: Z-axis (shows height)
   - Point size: 2-5 pixels

---

## Section 4: IMU & Motion Sensors

**Estimated Duration**: 1.5 hours
**Learning Outcomes**:
- Understand IMU components and noise
- Integrate IMU data for motion estimation
- Handle gimbal lock and quaternions

### 4.1 IMU Sensor Overview

**IMU** (Inertial Measurement Unit) contains:
- **Accelerometer**: Measures acceleration (linear motion)
- **Gyroscope**: Measures angular velocity (rotation)
- **Magnetometer** (optional): Compass (magnetic field)

**Why IMU?**
- Fast (typically 100-200 Hz)
- Works in darkness (no camera dependency)
- Detects motion, orientation, vibration
- Base for **odometry** (motion estimation)

### 4.2 Gazebo IMU Plugin

**URDF configuration**:

```xml
<gazebo reference="base_link">
  <sensor name="imu_sensor" type="imu">
    <pose>0 0 0 0 0 0</pose>
    <update_rate>200.0</update_rate>  <!-- 200 Hz -->
    <imu>
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.009</stddev>  <!-- ~0.5° per second -->
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.009</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.009</stddev>
          </noise>
        </z>
      </angular_velocity>
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.021</stddev>  <!-- ~0.002g -->
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.021</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0.0</mean>
            <stddev>0.021</stddev>
          </noise>
        </z>
      </linear_acceleration>
    </imu>
    <plugin name="imu_controller" filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <remapping>~/out:=imu/data</remapping>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

### 4.3 IMU Message Structure

```python
from sensor_msgs.msg import Imu
import numpy as np

def process_imu(msg):
    # Header
    timestamp = msg.header.stamp
    frame_id = msg.header.frame_id

    # Orientation (quaternion: qx, qy, qz, qw)
    q = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]

    # Angular velocity (rad/s)
    omega = np.array([msg.angular_velocity.x,
                      msg.angular_velocity.y,
                      msg.angular_velocity.z])

    # Linear acceleration (m/s²) - includes gravity!
    a = np.array([msg.linear_acceleration.x,
                  msg.linear_acceleration.y,
                  msg.linear_acceleration.z])

    # Note: linear_acceleration includes gravity component!
    # To get "net" acceleration: a_net = a - gravity_vector

    return timestamp, q, omega, a
```

### 4.4 IMU Dead Reckoning (Motion Integration)

**Dead reckoning** = estimate position/orientation from IMU:

```python
import numpy as np
from scipy.spatial.transform import Rotation

class IMUOdometer:
    """Estimate robot position/orientation from IMU."""

    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.orientation = Rotation.identity()  # Start aligned with world
        self.gravity = np.array([0.0, 0.0, -9.81])

    def update(self, imu_msg, dt):
        """Update position/velocity given new IMU measurement."""
        # Get acceleration in sensor frame
        a_sensor = np.array([imu_msg.linear_acceleration.x,
                            imu_msg.linear_acceleration.y,
                            imu_msg.linear_acceleration.z])

        # Rotate to world frame
        a_world = self.orientation.apply(a_sensor)

        # Remove gravity component
        a_net = a_world - self.gravity

        # Integrate: velocity += acceleration * dt
        self.velocity += a_net * dt

        # Integrate: position += velocity * dt
        self.position += self.velocity * dt

        # Update orientation from angular velocity
        omega = np.array([imu_msg.angular_velocity.x,
                         imu_msg.angular_velocity.y,
                         imu_msg.angular_velocity.z])

        # Small angle approximation for rotation update
        delta_rot = Rotation.from_rotvec(omega * dt)
        self.orientation = delta_rot * self.orientation

    def get_pose(self):
        """Return estimated position and orientation."""
        return self.position, self.orientation.as_quat()
```

**⚠️ Problem with dead reckoning**: Errors accumulate!

```
Time    Error
0s:     0 m (perfect)
5s:     0.1 m drift (from integration errors)
10s:    0.5 m drift
30s:    5 m drift (unusable!)
```

**Solution**: Fuse IMU with other sensors (next section)!

---

## Section 5: Sensor Fusion & Data Integration

**Estimated Duration**: 2.5 hours
**Learning Outcomes**:
- Understand Extended Kalman Filter (EKF) concepts
- Synchronize multiple sensors
- Fuse camera + lidar + IMU for robust state estimation

### 5.1 The Sensor Fusion Problem

**Single sensor** problems:

| Sensor | Advantage | Disadvantage |
|--------|-----------|--------------|
| **Camera** | Rich information, absolute location detection | Fails in darkness, high processing cost |
| **LiDAR** | Works in darkness, fast, dense | Limited range, expensive, no color |
| **IMU** | Very fast, small/cheap, works anywhere | Drifts over time, no absolute reference |

**Fusion solution**: Combine all three!

```
Fusion Formula (simplified):
est_position = (camera_position * confidence_camera +
               lidar_position * confidence_lidar +
               imu_position * confidence_imu) / sum(confidences)
```

### 5.2 Extended Kalman Filter (EKF) Overview

**Kalman Filter** = Optimal linear estimator.

**Extended Kalman Filter (EKF)** = Works with nonlinear robots.

**Two steps**:

1. **Predict** (using physics):
   ```
   x_predicted = motion_model(x_previous, control_input, dt)
   P_predicted = state_covariance + process_noise
   ```
   "Based on how we moved, where should we be?"

2. **Update** (using sensor):
   ```
   innovation = sensor_measurement - predicted_measurement
   gain = P_predicted / (P_predicted + measurement_noise)
   x_corrected = x_predicted + gain * innovation
   P_corrected = (1 - gain) * P_predicted
   ```
   "Sensor says we're here; adjust prediction."

### 5.3 Time Synchronization

**Critical issue**: Sensors publish at different rates and with different latencies!

```
Example timeline:
Time(ms)  Camera    LiDAR     IMU       Issue
0         frame 0
10
20        frame 1   scan 0    (100 Hz)
30                            reading 1  Out of sync!
40        frame 2
50        frame 3   scan 1    reading 2
```

**Solution: Approximate synchronization**:

```python
from message_filters import ApproximateTimeSynchronizer

# Subscribe to multiple topics
camera_sub = message_filters.Subscriber(node, Image, '/camera/image_raw')
lidar_sub = message_filters.Subscriber(node, PointCloud2, '/lidar/points')
imu_sub = message_filters.Subscriber(node, Imu, '/imu/data')

# Synchronize with ~100ms tolerance
sync = ApproximateTimeSynchronizer([camera_sub, lidar_sub, imu_sub],
                                   queue_size=10,
                                   slop=0.1)  # 100ms sync window

sync.registerCallback(fused_callback)

def fused_callback(image_msg, cloud_msg, imu_msg):
    """All three sensors now have synchronized timestamps."""
    # Process fused data
    timestamp = image_msg.header.stamp
    # ...
```

### 5.4 Simple Fusion Example

**Fusing camera position + IMU velocity**:

```python
import numpy as np

class SimplePositionFusion:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.velocity = np.array([0.0, 0.0, 0.0])

    def fuse(self, camera_pos, imu_accel, dt):
        # IMU gives velocity estimate
        v_imu = imu_accel * dt

        # Camera gives absolute position (occasionally)
        # Weight camera heavily (trust camera more than drifting IMU)
        camera_confidence = 0.7
        imu_confidence = 0.3

        # Fused velocity
        self.velocity = (v_imu * imu_confidence +
                        self.velocity * imu_confidence)

        # Fused position: blend camera (absolute) with IMU (relative)
        pos_from_imu = self.position + self.velocity * dt
        self.position = (camera_pos * camera_confidence +
                        pos_from_imu * imu_confidence)

        return self.position, self.velocity
```

---

## Section 6: Processing & Visualization

**Estimated Duration**: 1.5 hours
**Learning Outcomes**:
- Process sensor data efficiently
- Visualize in RViz2
- Create custom Python visualizations
- Build real-time sensor displays

### 6.1 Image Processing (OpenCV)

**Common operations on camera data**:

```python
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()

def process_camera(image_msg):
    # Convert ROS Image to OpenCV
    cv_image = bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")

    # Detect edges (useful for obstacle detection)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Find contours (obstacles)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw on original image
    cv2.drawContours(cv_image, contours, -1, (0, 255, 0), 2)

    # Convert back to ROS message
    result_msg = bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
    return result_msg
```

### 6.2 Point Cloud Filtering (PCL)

**Common point cloud operations**:

```python
# Note: Requires python-pcl package
import pcl
import numpy as np

def filter_point_cloud(cloud_msg):
    points = pointcloud2_to_numpy(cloud_msg)  # Convert to array

    # 1. Remove NaN/inf values
    valid = ~(np.isnan(points).any(axis=1) | np.isinf(points).any(axis=1))
    points = points[valid]

    # 2. Crop by range (remove distant points for speed)
    distances = np.linalg.norm(points, axis=1)
    points = points[distances < 50.0]  # Keep only <50m

    # 3. Voxel grid downsampling
    cloud = pcl.PointCloud(points.astype(np.float32))
    voxel_filter = cloud.make_voxel_grid_filter()
    voxel_filter.set_leaf_size(0.05, 0.05, 0.05)  # 5cm voxels
    cloud_filtered = voxel_filter.filter()

    return numpy_to_pointcloud2(cloud_filtered.to_array())
```

### 6.3 RViz2 Configuration

**Setup for multi-sensor visualization**:

1. **Displays to add**:
   - Image (camera feed)
   - PointCloud2 (LiDAR)
   - IMU (orientation arrow)
   - Axes (coordinate frames)
   - TF tree

2. **Config file** (YAML):
```yaml
Visualization Manager:
  Class: ""
  Displays:
    - Class: rviz_common/Image
      Name: Camera
      Topic: /camera/image_raw

    - Class: rviz_common/PointCloud2
      Name: LiDAR
      Topic: /lidar/points
      Color: [0, 255, 0]  # Green
      Point Size: 3

    - Class: rviz_common/TF
      Name: TF

  Global Options:
    Background Color: [48, 48, 48]
```

### 6.4 Custom Python Visualization

**Real-time plots using Matplotlib**:

```python
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

class SensorPlotter:
    def __init__(self, window_size=100):
        self.history_imu_accel = deque(maxlen=window_size)
        self.history_imu_gyro = deque(maxlen=window_size)
        self.history_distance = deque(maxlen=window_size)

    def update(self, imu_msg, lidar_msg):
        # Store IMU
        self.history_imu_accel.append(imu_msg.linear_acceleration.z)
        self.history_imu_gyro.append(imu_msg.angular_velocity.z)

        # Store LiDAR min distance
        min_range = min(lidar_msg.ranges) if lidar_msg.ranges else 999
        self.history_distance.append(min_range)

    def plot(self):
        fig, axes = plt.subplots(3, 1, figsize=(10, 8))

        # Plot IMU acceleration
        axes[0].plot(self.history_imu_accel, label='Z accel (m/s²)')
        axes[0].set_ylabel('Acceleration')
        axes[0].legend()
        axes[0].set_ylim([-2, 12])  # Include gravity ~9.81

        # Plot IMU gyroscope
        axes[1].plot(self.history_imu_gyro, label='Z rotation (rad/s)', color='orange')
        axes[1].set_ylabel('Angular Velocity')
        axes[1].legend()

        # Plot LiDAR min distance
        axes[2].plot(self.history_distance, label='Min LiDAR range (m)', color='green')
        axes[2].set_ylabel('Distance (m)')
        axes[2].set_xlabel('Sample')
        axes[2].legend()

        plt.tight_layout()
        plt.show()
```

---

## Summary of Chapter 6

✅ **Section 1**: Gazebo sensor plugins and noise modeling
✅ **Section 2**: RGB and depth cameras, point cloud conversion
✅ **Section 3**: 2D/3D LiDAR and point cloud processing
✅ **Section 4**: IMU sensors and dead reckoning
✅ **Section 5**: Sensor fusion and Extended Kalman Filters
✅ **Section 6**: Processing and visualization tools

**Next**: Exercises 6.1 & 6.2 bring it all together!

---
