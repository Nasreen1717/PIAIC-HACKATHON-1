# Exercise 6.1: Multi-Sensor Data Capture and Processing

**Difficulty**: Guided (step-by-step instructions, fill-in-the-blank code)
**Duration**: 3-4 hours
**Learning Outcomes**: Sensor configuration → Data collection → Processing pipelines → Visualization

---

## Exercise Overview

In this exercise, you will set up a realistic sensor simulation in Gazebo and process data from multiple sensors (camera, LiDAR, IMU) in real-time using ROS 2 nodes.

**Your task**: Build a complete sensor data pipeline that:
1. Captures RGB and depth images from a simulated camera
2. Processes LiDAR point clouds (filtering and visualization)
3. Reads IMU sensor data and estimates motion
4. Visualizes all data in ROS 2 tools (RViz2, rqt)

Unlike Exercise 4 and 5 which focused on simulation or rendering, this exercise focuses on **perception and data processing** — the critical bridge between raw sensor data and robot understanding.

---

## Prerequisites

Before starting, verify you have:

- ✅ Gazebo 11+ with working robot models
- ✅ ROS 2 Humble fully installed
- ✅ Python 3.10+ with cv_bridge, pcl_ros packages
- ✅ RViz2 installed (`sudo apt install ros-humble-rviz2`)
- ✅ Completed Chapter 6 reading (Sensor Simulation & Perception)

Quick verification:

```bash
# Check ROS 2
source /opt/ros/humble/setup.bash
ros2 node list  # Should work (even if empty)

# Check required packages
python3 -c "import cv2; import numpy" || pip install opencv-python numpy

# Check RViz
rviz2 --version
```

---

## Step 1: Set Up Sensor-Equipped Robot (30 min)

### 1.1 Create URDF with Sensors

Create file: `sensor_robot.urdf`

```xml
<?xml version="1.0" ?>
<robot name="sensor_robot">
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.3 0.3 0.3"/>
      </geometry>
      <material name="white"><color rgba="1 1 1 1"/></material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.3 0.3"/>
      </geometry>
    </collision>
  </link>

  <!-- RGB-D Camera -->
  <link name="camera_link">
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="blue"><color rgba="0 0 1 1"/></material>
    </visual>
    <collision>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.15 0 0.1" rpy="0 0 0"/>
  </joint>

  <!-- LiDAR (3D laser scanner) -->
  <link name="lidar_link">
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <material name="black"><color rgba="0 0 0 1"/></material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
    </collision>
  </link>

  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>

  <!-- IMU (Inertial Measurement Unit) -->
  <link name="imu_link">
    <inertial>
      <mass value="0.05"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="imu_joint" type="fixed">
    <parent link="base_link"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <!-- TODO 1: Add visual geometry to IMU link -->
  <!-- Hint: Use a small sphere, radius="0.02", color red -->

</robot>
```

### 1.2 Create Gazebo SDF World with Sensors

Create file: `sensor_world.world`

```xml
<?xml version="1.0" ?>
<sdf version="1.4">
  <world name="sensor_demo">
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <include>
      <uri>model://sun</uri>
    </include>

    <!-- TODO 2: Physics configuration -->
    <!-- Add <physics> with ODE solver, gravity [0 0 -9.81], time_step 0.001 -->

    <!-- Robot with sensors -->
    <model name="robot">
      <pose>0 0 0.5 0 0 0</pose>
      <link name="base_link">
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
              <size>0.3 0.3 0.3</size>
            </box>
          </geometry>
          <material>
            <ambient>1 1 1 1</ambient>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.3 0.3 0.3</size>
            </box>
          </geometry>
        </collision>

        <!-- RGB-D Camera Sensor -->
        <sensor name="camera" type="camera">
          <camera>
            <horizontal_fov>1.047</horizontal_fov>
            <image>
              <width>640</width>
              <height>480</height>
              <format>R8G8B8</format>
            </image>
            <clip>
              <near>0.01</near>
              <far>100</far>
            </clip>
          </camera>
          <plugin name="camera_controller"
            filename="libgazebo_ros_camera.so">
            <ros>
              <remapping>~/image_raw:=/camera/color/image_raw</remapping>
              <remapping>~/camera_info:=/camera/color/camera_info</remapping>
            </ros>
            <camera_name>camera</camera_name>
            <frame_name>camera_link</frame_name>
          </plugin>
          <pose>0.15 0 0.1 0 0 0</pose>
          <update_rate>30</update_rate>
        </sensor>

        <!-- Depth Camera -->
        <sensor name="depth_camera" type="depth">
          <camera>
            <horizontal_fov>1.047</horizontal_fov>
            <image>
              <width>640</width>
              <height>480</height>
            </image>
            <clip>
              <near>0.01</near>
              <far>100</far>
            </clip>
          </camera>
          <plugin name="depth_camera_controller"
            filename="libgazebo_ros_camera.so">
            <ros>
              <remapping>~/image_raw:=/camera/depth/image_raw</remapping>
              <remapping>~/camera_info:=/camera/depth/camera_info</remapping>
            </ros>
            <camera_name>depth_camera</camera_name>
            <frame_name>camera_link</frame_name>
          </plugin>
          <pose>0.15 0 0.1 0 0 0</pose>
          <update_rate>30</update_rate>
        </sensor>

        <!-- 3D LiDAR Sensor (gpu_ray) -->
        <!-- TODO 3: Add LiDAR sensor -->
        <!-- Hint: type="gpu_lidar", horizontal_samples=1024, vertical_samples=64 -->
        <!-- Frame name: lidar_link, publish_rate: 10Hz -->

        <!-- IMU Sensor -->
        <sensor name="imu_sensor" type="imu">
          <plugin name="imu_controller"
            filename="libgazebo_ros_imu_sensor.so">
            <ros>
              <remapping>~/imu:=/imu/data</remapping>
            </ros>
            <frame_name>imu_link</frame_name>
          </plugin>
          <pose>0 0 0 0 0 0</pose>
          <update_rate>100</update_rate>
        </sensor>
      </link>
    </model>

    <!-- Obstacle for sensor testing -->
    <model name="box_obstacle">
      <pose>2 0 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual>
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
          </material>
        </visual>
        <collision>
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>
```

---

## Step 2: Start Simulation and Verify Sensors (20 min)

### 2.1 Launch Gazebo with Sensors

Terminal 1:

```bash
source /opt/ros/humble/setup.bash

# Change to your working directory
cd /path/to/exercise-6-1

# Start Gazebo server with sensor world
gzserver sensor_world.world
```

### 2.2 Verify ROS 2 Topics

Terminal 2:

```bash
source /opt/ros/humble/setup.bash

# List all published topics
ros2 topic list
# Expected output should include:
#   /camera/color/image_raw
#   /camera/depth/image_raw
#   /camera/color/camera_info
#   /lidar/scan
#   /imu/data

# Check camera image rate
ros2 topic hz /camera/color/image_raw
# Expected: ~30 Hz

# Check IMU rate
ros2 topic hz /imu/data
# Expected: ~100 Hz
```

---

## Step 3: Process Camera Data (45 min)

### 3.1 Create Camera Processing Node

Create file: `src/camera_processor.py`

```python
#!/usr/bin/env python3
"""
Exercise 6.1: Camera Processor Node

Processes RGB and depth camera data from Gazebo.
Publishes edge-detected images and point clouds.
"""

import numpy as np
import cv2

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image, PointCloud2, CameraInfo
from cv_bridge import CvBridge
from image_geometry import PinholeCameraModel
import sensor_msgs.point_cloud2 as pc2


class CameraProcessor(Node):
    """Process camera data from Gazebo."""

    def __init__(self):
        super().__init__('camera_processor')

        self.bridge = CvBridge()
        self.camera_model = PinholeCameraModel()
        self.camera_info_received = False

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # TODO 4: Create subscription to /camera/color/camera_info
        # Hint: Subscribe with CameraInfo type, call camera_info_callback

        # TODO 5: Create subscription to /camera/color/image_raw
        # Hint: Subscribe with Image type, call rgb_callback

        # TODO 6: Create subscription to /camera/depth/image_raw
        # Hint: Subscribe with Image type, call depth_callback

        # TODO 7: Create publishers
        # - Publish processed RGB to /camera/processed
        # - Publish depth point cloud to /camera/pointcloud
        # Hint: self.create_publisher(Image/PointCloud2, topic, qos)

        self.get_logger().info("✅ Camera Processor initialized")

    def camera_info_callback(self, msg: CameraInfo) -> None:
        """Store camera calibration."""
        if not self.camera_info_received:
            self.camera_model.fromCameraInfo(msg)
            self.camera_info_received = True
            self.get_logger().info(f"📷 Camera: {msg.width}×{msg.height}")

    def rgb_callback(self, msg: Image) -> None:
        """Process RGB image: edge detection."""
        try:
            # TODO 8: Convert ROS Image to OpenCV format
            # Hint: cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # TODO 9: Convert to grayscale
            # Hint: gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # TODO 10: Apply Canny edge detection
            # Hint: edges = cv2.Canny(gray, 50, 150)

            # TODO 11: Convert back to ROS Image and publish
            # Hint: processed_msg = self.bridge.cv2_to_imgmsg(edges, 'mono8')

            pass

        except Exception as e:
            self.get_logger().error(f"❌ RGB processing error: {e}")

    def depth_callback(self, msg: Image) -> None:
        """Convert depth image to point cloud."""
        if not self.camera_info_received:
            return

        try:
            # TODO 12: Convert depth image to numpy array
            # Hint: depth_np = self.bridge.imgmsg_to_cv2(msg, 'passthrough')

            # TODO 13: Create mesh grid of pixel coordinates
            # Hint: u, v = np.meshgrid(np.arange(width), np.arange(height))

            # TODO 14: Get camera intrinsics
            # Hint: fx = self.camera_model.fx()

            # TODO 15: Back-project to 3D points
            # Hint: x = (u - cx) * z / fx

            # TODO 16: Create PointCloud2 and publish
            # Hint: pc2.create_cloud_xyz32(frame_id, timestamp, xyz)

            pass

        except Exception as e:
            self.get_logger().error(f"❌ Depth processing error: {e}")


def main():
    rclpy.init()
    processor = CameraProcessor()
    rclpy.spin(processor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3.2 Test Camera Processing

```bash
# Terminal 3:
source /opt/ros/humble/setup.bash
cd /path/to/exercise-6-1
python3 src/camera_processor.py

# In another terminal:
# View processed RGB
ros2 run rqt_image_view rqt_image_view /camera/processed

# View depth point cloud
rviz2
# Add PointCloud2 display: /camera/pointcloud
```

---

## Step 4: Process LiDAR Data (45 min)

### 4.1 Create LiDAR Processing Node

Create file: `src/lidar_processor.py`

```python
#!/usr/bin/env python3
"""
Exercise 6.1: LiDAR Processor Node

Processes point cloud data from Gazebo LiDAR.
Applies filtering and publishes processed cloud.
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import PointCloud2
import sensor_msgs.point_cloud2 as pc2


class LiDARProcessor(Node):
    """Process LiDAR point cloud data."""

    def __init__(self):
        super().__init__('lidar_processor')

        # TODO 17: Set processing parameters
        # Hint: self.voxel_size = 0.01  # 1cm voxels
        # Hint: self.max_distance = 10.0  # 10m max range

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # TODO 18: Subscribe to /lidar/scan
        # Hint: self.create_subscription(PointCloud2, ...)

        # TODO 19: Create publisher for /lidar/filtered
        # Hint: self.filtered_pub = self.create_publisher(...)

        self.get_logger().info("✅ LiDAR Processor initialized")

    def lidar_callback(self, msg: PointCloud2) -> None:
        """Process LiDAR point cloud."""
        try:
            # TODO 20: Convert PointCloud2 to numpy array
            # Hint: points = np.array([(pt[0], pt[1], pt[2]) for pt in pc2.read_points(...)])

            # TODO 21: Filter by distance
            # Hint: distances = np.linalg.norm(points, axis=1)

            # TODO 22: Apply voxel downsampling
            # Hint: Divide space into voxels, keep one point per voxel

            # TODO 23: Create filtered PointCloud2 and publish
            # Hint: pc2.create_cloud_xyz32(...)

            pass

        except Exception as e:
            self.get_logger().error(f"❌ LiDAR processing error: {e}")


def main():
    rclpy.init()
    processor = LiDARProcessor()
    rclpy.spin(processor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## Step 5: Process IMU Data (45 min)

### 5.1 Create IMU Processing Node

Create file: `src/imu_processor.py`

```python
#!/usr/bin/env python3
"""
Exercise 6.1: IMU Processor Node

Reads IMU data and estimates motion using dead reckoning.
Publishes velocity and position estimates.
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist


class IMUProcessor(Node):
    """Process IMU sensor data."""

    def __init__(self):
        super().__init__('imu_processor')

        # TODO 24: Initialize state variables
        # Hint: self.position = np.array([0.0, 0.0, 0.0])
        # Hint: self.velocity = np.array([0.0, 0.0, 0.0])
        # Hint: self.last_time = None

        # TODO 25: Subscribe to /imu/data
        # Hint: self.create_subscription(Imu, ...)

        # TODO 26: Create publisher for /imu/odometry
        # Hint: self.odom_pub = self.create_publisher(...)

        self.get_logger().info("✅ IMU Processor initialized")

    def imu_callback(self, msg: Imu) -> None:
        """Process IMU data and estimate motion."""
        try:
            # TODO 27: Extract acceleration
            # Hint: accel = np.array([msg.linear_acceleration.x, ...])

            # TODO 28: Compute time delta
            # Hint: current_time = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9

            # TODO 29: Integrate: velocity += accel * dt
            # (Dead reckoning step 1)

            # TODO 30: Integrate: position += velocity * dt
            # (Dead reckoning step 2)

            # TODO 31: Create Odometry message and publish
            # Hint: odom = Odometry()

            pass

        except Exception as e:
            self.get_logger().error(f"❌ IMU processing error: {e}")


def main():
    rclpy.init()
    processor = IMUProcessor()
    rclpy.spin(processor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## Step 6: Visualize All Data in RViz2 (30 min)

### 6.1 Create RViz Configuration

Create file: `rviz_config.rviz`

```yaml
Panels:
  - Class: rviz_common/Displays
    Name: Displays

Visualization Manager:
  Class: rviz_common/VisualizationManager
  Displays:
    - Class: rviz_default_plugins/Image
      Name: RGB Image
      Topic: /camera/processed

    - Class: rviz_default_plugins/PointCloud2
      Name: Depth Pointcloud
      Topic: /camera/pointcloud

    - Class: rviz_default_plugins/PointCloud2
      Name: LiDAR Points
      Topic: /lidar/filtered

    - Class: rviz_default_plugins/TF
      Name: TF

  Global Options:
    Fixed Frame: base_link
    Frame Rate: 30
```

### 6.2 Launch Full Visualization

Terminal (Visualization):

```bash
source /opt/ros/humble/setup.bash
cd /path/to/exercise-6-1

# Start RViz2 with configuration
rviz2 -d rviz_config.rviz
```

---

## Step 7: Document and Verify (30 min)

### 7.1 Create Summary Document

Create file: `RESULTS.md`

Document your findings:

```markdown
# Exercise 6.1 Results

## Sensor Configuration

- Camera resolution: [Your value]
- Camera frame rate: [Your measured Hz]
- LiDAR horizontal samples: [Your value]
- LiDAR vertical samples: [Your value]
- LiDAR update rate: [Your measured Hz]
- IMU update rate: [Your measured Hz]

## Processing Performance

- RGB processing: [X fps]
- Depth conversion: [X fps]
- LiDAR filtering: [X fps, X% reduction]
- Dead reckoning drift: [Measured over 30 seconds]

## Visualization Quality

- [✓/✗] RGB image displays edge detection clearly
- [✓/✗] Depth point cloud aligns with camera view
- [✓/✗] LiDAR cloud shows obstacles at correct distances
- [✓/✗] RViz displays all data simultaneously at >10 Hz

## Observations

- [What works well?]
- [What's challenging?]
- [How do sensors complement each other?]
```

---

## Grading Rubric (100 points)

### Sensor Setup (20 points)

- [ ] (5 pts) URDF includes all three sensors with correct frames
- [ ] (5 pts) Gazebo world launches without errors
- [ ] (5 pts) All ROS 2 topics publishing at expected rates
- [ ] (5 pts) Camera calibration information accessible

### Code Implementation (40 points)

- [ ] (10 pts) Camera processor: RGB edge detection working
- [ ] (10 pts) Camera processor: Depth-to-pointcloud conversion working
- [ ] (10 pts) LiDAR processor: Filtering working, reduction >30%
- [ ] (10 pts) IMU processor: Dead reckoning calculating position

### Visualization & Analysis (25 points)

- [ ] (8 pts) RViz displays all point clouds simultaneously
- [ ] (8 pts) Performance metrics show >15 FPS average
- [ ] (9 pts) RESULTS.md documents findings with actual measurements

### Code Quality (15 points)

- [ ] (5 pts) All TODOs completed with docstrings
- [ ] (5 pts) No console errors or warnings
- [ ] (5 pts) Code follows PEP 8 style guidelines

---

## Acceptance Criteria

Your submission should:

- [ ] All 31 TODOs completed
- [ ] No Python syntax errors
- [ ] All ROS 2 nodes run without crashing
- [ ] Gazebo world loads and runs >10 FPS
- [ ] All sensors publish data (verify with ros2 topic list)
- [ ] Processing nodes consume data successfully
- [ ] RViz displays colored point clouds
- [ ] RESULTS.md includes measurements
- [ ] All code is well-commented

---

## Troubleshooting

### "Topic not found"
```bash
# Verify Gazebo is running
ros2 topic list

# Wait 5-10 seconds for sensors to initialize
ros2 topic hz /lidar/scan
```

### "Camera calibration not received"
```bash
# Check camera_info is publishing
ros2 topic echo /camera/color/camera_info | head -5

# Verify camera_info has non-zero intrinsics (fx, fy should be ~500-600)
```

### "ImportError: No module named cv_bridge"
```bash
sudo apt install ros-humble-cv-bridge
sudo apt install ros-humble-image-geometry
```

---

## Next Steps

After completing this exercise:

1. **Extend processing**: Add your own filters (e.g., Gaussian blur)
2. **Combine sensors**: Use data from multiple sensors in one node
3. **Save data**: Record sensor streams to ROS bags for offline analysis
4. **Add visualization**: Create custom RViz plugins
5. **Begin Exercise 6.2**: Implement sensor fusion (EKF)

---

**Excellent work!** You've built a complete sensor perception pipeline! 🎛️
