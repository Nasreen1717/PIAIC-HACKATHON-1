# Exercise 6.2: Sensor Fusion Pipeline Implementation

**Difficulty**: Semi-open (architecture-focused, design decisions required)
**Duration**: 4-5 hours
**Learning Outcomes**: Multi-sensor fusion → Kalman filtering → Autonomous perception → System integration

---

## Exercise Overview

In this exercise, you will design and implement a **sensor fusion pipeline** that combines data from multiple sensors (camera, LiDAR, IMU) to create a robust perception system.

Unlike Exercise 6.1 (step-by-step guided), this is a **design challenge**: you decide the architecture, trade-offs, and implementation details.

**Your task**: Build a fusion node that:
1. Subscribes to multiple sensor topics (camera, LiDAR, IMU)
2. Implements time synchronization of asynchronous sensors
3. Applies Extended Kalman Filter (or alternative fusion method)
4. Produces a unified "best estimate" of robot state
5. Quantifies confidence (covariance) in the estimate

**Real-world context**: This mirrors how self-driving cars, drones, and robots perceive their environment—no single sensor is perfect, so fusion is essential.

---

## Background: Why Sensor Fusion?

Each sensor has strengths and weaknesses:

| Sensor | Strengths | Weaknesses |
|--------|-----------|-----------|
| **Camera** | High-resolution, colored information | Slow (30 Hz), affected by lighting, no depth |
| **LiDAR** | Fast (10-20 Hz), 3D data, works in dark | Sparse clouds, expensive, moving parts |
| **IMU** | Very fast (100+ Hz), motion estimation | Drifts quickly, no absolute position |

**Fusion solution**: Combine their strengths, mitigate weaknesses.

---

## Step 1: Design Your Fusion Architecture (45 min)

### 1.1 Create Architecture Document

Create file: `ARCHITECTURE.md`

Document your design decisions:

```markdown
# Sensor Fusion Architecture

## Sensor Inputs

### Camera
- Topic: `/camera/color/image_raw` (30 Hz)
- Type: RGB image
- Processing: Extract features? Estimate position from visual odometry?
- Trust level: [High/Medium/Low] because...

### LiDAR
- Topic: `/lidar/scan` (10 Hz)
- Type: Point cloud (sparse)
- Processing: Feature detection? Distance estimation?
- Trust level: [High/Medium/Low] because...

### IMU
- Topic: `/imu/data` (100 Hz)
- Type: Acceleration, angular velocity
- Processing: Dead reckoning? Motion preintegration?
- Trust level: [High/Medium/Low] because...

## Fusion Method

Choose your approach:

- [ ] **Extended Kalman Filter (EKF)** - Standard in robotics
  - Pros: Well-understood, handles uncertainty well
  - Cons: Nonlinear filters more complex

- [ ] **Unscented Kalman Filter (UKF)** - Better for highly nonlinear systems
  - Pros: More accurate than EKF
  - Cons: More computationally expensive

- [ ] **Particle Filter** - Most flexible
  - Pros: Handles multimodal distributions
  - Cons: Requires many particles, slower

- [ ] **Custom weighted average** - Simple approach
  - Pros: Easy to understand and debug
  - Cons: Doesn't optimally handle uncertainty

**Justification**: [Why did you choose this method?]

## Time Synchronization Strategy

How will you handle different update rates?

- [ ] ApproximateTimeSynchronizer (ROS 2 standard)
  - Tolerance: [X] milliseconds

- [ ] Custom buffer with time window

- [ ] Asynchronous fusion (different rates okay)

## State Representation

What state vector are you estimating?

```
[x, y, z,           # Position (meters)
 vx, vy, vz,        # Velocity (m/s)
 yaw, pitch, roll,  # Orientation (radians)
 ax, ay, az]        # Acceleration estimates
```

Or something else? Document here.

## Covariance/Uncertainty Model

How do you represent confidence?

- State covariance matrix (P)
- Measurement noise (R)
- Process noise (Q)

Example:
```
Q (process noise) = [0.01,  0,  0, ...]  # Expect small drift in state
R (measurement noise) = [0.1, 0, 0, ...]  # Camera position estimate uncertain
```

## Output Interface

What does your fused estimate publish?

- Topic: `/robot/fused_estimate` (proposed)
- Message type: Odometry / PoseStamped / Custom
- Frequency: [X] Hz
- Includes covariance: [Yes/No]

## Performance Target

What's acceptable performance?

- Latency: [X] milliseconds
- Accuracy: [X] meters (compared to ground truth)
- Update rate: [X] Hz
- CPU usage: < [X]%

```

### 1.2 Data Flow Diagram

Create file: `DATAFLOW.txt`

Sketch (in ASCII or describe) your data pipeline:

```
Inputs:
  /camera/color/image_raw --┐
  /lidar/scan               ├---> Time Sync ---> Feature Extraction --┐
  /imu/data                 ┘                                          │
                                                                        ├---> EKF/Filter ---> /robot/fused_estimate
                                                                        │
  /gazebo/ground_truth ----┐ (optional, for validation)               │
  (for benchmarking) -------┘────────────────────────────────────────→ Validation

Publish:
  /robot/fused_estimate (Odometry)
  /robot/fused_covariance (optional, for uncertainty visualization)
```

---

## Step 2: Implement Time Synchronization (45 min)

### 2.1 Create Fusion Node with Synchronization

Create file: `src/sensor_fusion.py`

```python
#!/usr/bin/env python3
"""
Exercise 6.2: Sensor Fusion Pipeline

Fuses camera, LiDAR, and IMU data using [YOUR METHOD].
Handles time synchronization and outputs unified perception.
"""

import numpy as np
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image, PointCloud2, Imu, CameraInfo
from nav_msgs.msg import Odometry
from message_filters import Subscriber, ApproximateTimeSynchronizer
from std_msgs.msg import Header


class SensorFusionNode(Node):
    """
    Fuse multiple sensors for robust state estimation.

    DESIGN DECISIONS:
    - Fusion method: [EKF/UKF/Particle Filter/Other]
    - Time sync tolerance: [X] ms
    - State vector: [List what you're estimating]
    - Update frequency: [X] Hz target
    """

    def __init__(self):
        super().__init__('sensor_fusion')

        # TODO 1: Initialize filter/fusion method
        # Hint: Create EKF instance, or initialize particle filter
        # Example: self.ekf = ExtendedKalmanFilter(...)

        # TODO 2: Set up time synchronization
        # Hint: Use ApproximateTimeSynchronizer with appropriate slop
        # Example:
        #   imu_sub = Subscriber(self, Imu, '/imu/data', qos_profile)
        #   cam_sub = Subscriber(self, Image, '/camera/...', qos_profile)
        #   ts = ApproximateTimeSynchronizer([imu_sub, cam_sub], queue_size=10, slop=0.05)
        #   ts.registerCallback(self.fusion_callback)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # TODO 3: Subscribe to individual sensors (for asynchronous processing)
        # OR use time synchronizer above (for synchronized processing)
        # Choose one approach based on ARCHITECTURE.md

        # TODO 4: Create publisher for fused estimate
        # Hint: self.fused_pub = self.create_publisher(Odometry, ...)

        # TODO 5: Create publisher for covariance visualization (optional)
        # Hint: Could publish as Marker, TwistWithCovariance, etc.

        self.fusion_update_count = 0
        self.last_log_time = None

        self.get_logger().info("✅ Sensor Fusion Node initialized")

    # Choose ONE of the following:

    def fusion_callback(self, imu_msg: Imu, cam_msg: Image, lidar_msg: PointCloud2) -> None:
        """
        Synchronized callback for all three sensors.

        Called when all three sensors have recent data (within slop tolerance).
        """
        try:
            # TODO 6: Extract sensor measurements
            # IMU: accel = [msg.linear_acceleration.x, y, z]
            # Camera: [Extract features or position estimate]
            # LiDAR: [Extract range measurements or obstacle map]

            # TODO 7: Predict step (using motion model)
            # Hint: Use IMU accel to predict next state
            # Example: self.ekf.predict(imu_accel, dt)

            # TODO 8: Update step (using measurements)
            # Hint: Call update with camera position estimate
            # Example: self.ekf.update(z_camera, R_camera)
            # Hint: Call update with LiDAR measurements
            # Example: self.ekf.update(z_lidar, R_lidar)

            # TODO 9: Publish fused estimate
            # Hint: Extract state from filter, create Odometry message
            # Example: self.fused_pub.publish(odom_msg)

            self.fusion_update_count += 1

        except Exception as e:
            self.get_logger().error(f"❌ Fusion error: {e}")

    def async_imu_callback(self, msg: Imu) -> None:
        """
        Alternative: Process IMU asynchronously (high frequency).

        Call predict step at 100 Hz, update less frequently with cameras.
        """
        try:
            # TODO 10 (Alternative): High-frequency predict step
            # Use this if you choose asynchronous fusion

            pass

        except Exception as e:
            self.get_logger().error(f"❌ IMU callback error: {e}")


class SimpleExtendedKalmanFilter:
    """
    Minimal EKF implementation for sensor fusion.

    You can replace this with your custom implementation.
    """

    def __init__(self):
        # TODO 11: Initialize state vector
        # Example: self.state = np.zeros(6)  # [x, y, z, vx, vy, vz]

        # TODO 12: Initialize covariance matrices
        # P: State covariance (uncertainty)
        # Q: Process noise (trust in motion model)
        # R: Measurement noise (trust in sensors)

        pass

    def predict(self, u: np.ndarray, dt: float) -> None:
        """
        Predict step: advance state using motion model.

        Args:
            u: Control input (acceleration from IMU)
            dt: Time step
        """
        # TODO 13: Update state using motion model
        # Example: x += v*dt, v += a*dt

        # TODO 14: Update covariance (uncertainty grows)
        # Example: P = F @ P @ F.T + Q

        pass

    def update(self, z: np.ndarray, R: np.ndarray) -> None:
        """
        Update step: correct state using measurement.

        Args:
            z: Measurement (position from camera, range from LiDAR)
            R: Measurement noise covariance
        """
        # TODO 15: Compute innovation (difference from prediction)
        # Example: innovation = z - H @ state

        # TODO 16: Compute Kalman gain
        # Example: K = P @ H.T @ inv(S)

        # TODO 17: Update state and covariance
        # Example: state += K @ innovation
        # Example: P = (I - K @ H) @ P

        pass

    def get_estimate(self) -> dict:
        """Return current state estimate and covariance."""
        return {
            'state': self.state.copy(),
            'covariance': self.covariance.copy()
        }


def main():
    rclpy.init()

    try:
        node = SensorFusionNode()
        rclpy.spin(node)
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## Step 3: Implement Measurement Extraction (45 min)

### 3.1 Add Feature Extractors

Create file: `src/feature_extractors.py`

```python
"""
Feature extractors for camera and LiDAR measurements.

These convert raw sensor data to measurement vectors for fusion.
"""

import numpy as np
from typing import Tuple, Optional


class CameraFeatureExtractor:
    """Extract position/orientation estimates from images."""

    def __init__(self, camera_matrix: np.ndarray):
        # TODO 18: Store camera intrinsics
        self.K = camera_matrix

    def extract_position(self, image) -> Optional[np.ndarray]:
        """
        Extract 2D position estimate from image.

        Simple implementation: Find centroid of image features.
        Advanced: Use SIFT/ORB features, PnP solver for 6D pose.

        TODO 19: Implement feature detection and position estimation
        """
        # Hint: Use cv2.SIFT_create(), cv2.ORB_create()
        # Hint: Find features, match with previous frame
        # Hint: Estimate motion from feature matching
        # Return: [x, y, z] position estimate
        pass


class LiDARFeatureExtractor:
    """Extract range/bearing measurements from point clouds."""

    def __init__(self):
        self.min_range = 0.1
        self.max_range = 30.0

    def extract_obstacles(self, pointcloud) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract obstacle ranges from point cloud.

        TODO 20: Process point cloud to extract obstacle distances
        - Filter by range
        - Cluster points into obstacles
        - Extract centroid of each obstacle

        Returns:
            positions: (N, 3) array of obstacle positions
            ranges: (N,) array of distances to obstacles
        """
        # Hint: Use spatial clustering (e.g., DBSCAN)
        # Hint: Filter points by range
        # Hint: Compute obstacle centroids
        pass

    def extract_ground_plane(self, pointcloud) -> Optional[Tuple[np.ndarray, float]]:
        """
        Extract ground plane equation from point cloud.

        Useful for: Floor detection, robot height estimation

        TODO 21: Fit plane to lower points
        Returns:
            normal: Plane normal vector (a, b, c)
            d: Plane distance constant (ax + by + cz = d)
        """
        # Hint: Use RANSAC for robust fitting
        # Hint: Filter points at z < z_robot + 0.5m
        # Hint: Fit plane using SVD or least squares
        pass


class IMUMeasurementProcessor:
    """Process IMU for velocity/acceleration estimates."""

    def __init__(self):
        self.accel_bias = np.array([0.0, 0.0, 0.0])

    def get_acceleration(self, imu_msg) -> np.ndarray:
        """Extract acceleration measurement."""
        # TODO 22: Get acceleration from IMU message
        accel = np.array([
            imu_msg.linear_acceleration.x,
            imu_msg.linear_acceleration.y,
            imu_msg.linear_acceleration.z
        ])
        return accel - self.accel_bias

    def calibrate_accel_bias(self, imu_msgs_at_rest) -> None:
        """
        Calibrate accelerometer bias (gyro/accel offset at rest).

        TODO 23: Compute mean of stationary IMU readings
        """
        # Hint: Average multiple readings while robot is still
        pass
```

---

## Step 4: Validation and Performance (45 min)

### 4.1 Create Validation Script

Create file: `validate_fusion.py`

```python
#!/usr/bin/env python3
"""
Validate sensor fusion output against ground truth.

Measures:
- Accuracy: How close to ground truth?
- Latency: How fast is fusion?
- Consistency: How often do estimates change dramatically?
"""

import numpy as np
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry


class FusionValidator(Node):
    """Validate fusion accuracy."""

    def __init__(self):
        super().__init__('fusion_validator')

        # Metrics tracking
        self.position_errors = []
        self.velocity_errors = []
        self.process_times = []

        # TODO 24: Subscribe to fused estimate
        # Hint: self.create_subscription(Odometry, '/robot/fused_estimate', ...)

        # TODO 25: Subscribe to ground truth (if available in simulation)
        # Hint: gazebo publishes /gazebo/ground_truth_model_states

        self.get_logger().info("✅ Fusion Validator initialized")

    def fused_callback(self, msg: Odometry) -> None:
        """Record fused estimate."""
        # TODO 26: Extract position from message
        fused_pos = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])

        # TODO 27: Extract covariance (uncertainty)
        position_cov = np.array([
            msg.pose.covariance[0],   # x variance
            msg.pose.covariance[7],   # y variance
            msg.pose.covariance[14]   # z variance
        ])

        # Store for analysis
        self.position_errors.append({
            'position': fused_pos,
            'covariance': position_cov,
            'timestamp': msg.header.stamp
        })

    def ground_truth_callback(self, msg) -> None:
        """
        Compare with ground truth (optional).

        TODO 28: Extract ground truth position
        TODO 29: Compute error relative to fused estimate
        """
        pass

    def compute_validation_metrics(self) -> dict:
        """
        TODO 30: Compute statistics from collected data

        Metrics:
        - Mean absolute error (MAE)
        - Root mean squared error (RMSE)
        - Max error
        - Consistency (variance of errors)
        """
        if not self.position_errors:
            return {}

        # Extract positions
        positions = np.array([
            err['position'] for err in self.position_errors
        ])

        metrics = {
            'position_mean': np.mean(positions, axis=0),
            'position_std': np.std(positions, axis=0),
            'covariance_mean': np.mean([
                err['covariance'] for err in self.position_errors
            ], axis=0)
        }

        return metrics
```

### 4.2 Create Benchmarking Script

Create file: `benchmark_fusion.py`

```python
#!/usr/bin/env python3
"""
Benchmark sensor fusion performance.

Measures:
- CPU usage
- Memory usage
- Processing latency
- Update frequency
"""

import psutil
import time

def benchmark_fusion_node():
    """
    TODO 31: Monitor fusion node performance

    - Track CPU usage over time
    - Check memory consumption
    - Measure callback latency
    - Verify update rate
    """

    # TODO 32: Print performance report
    print("=" * 60)
    print("Sensor Fusion Performance Report")
    print("=" * 60)
    print(f"CPU Usage: [X]%")
    print(f"Memory: [X] MB")
    print(f"Average latency: [X] ms")
    print(f"Update rate: [X] Hz")
    print("=" * 60)

if __name__ == '__main__':
    benchmark_fusion_node()
```

---

## Step 5: Documentation and Analysis (30 min)

### 5.1 Create Implementation Report

Create file: `IMPLEMENTATION_REPORT.md`

Document your implementation:

```markdown
# Sensor Fusion Implementation Report

## Architecture Summary

- **Fusion method**: [EKF/UKF/Other]
- **Time sync**: ApproximateTimeSynchronizer with [X]ms tolerance
- **Update frequency**: [X] Hz
- **State vector**: [Your state representation]

## Key Design Decisions

### 1. Measurement Uncertainty (R matrix)

How much do you trust each sensor?

- Camera: variance = [X] m²
  - Reasoning: [Why this value?]
- LiDAR: variance = [X] m²
  - Reasoning: [Why this value?]
- IMU: variance = [X] (m/s²)²
  - Reasoning: [Why this value?]

### 2. Process Noise (Q matrix)

How much do you expect the state to change unpredictably?

- Position process noise: [X]
  - Reasoning: [Why?]
- Velocity process noise: [X]
  - Reasoning: [Why?]

### 3. Time Synchronization Strategy

- Using ApproximateTimeSynchronizer: [Yes/No]
  - Slop: [X] milliseconds
  - Trade-off: What breaks if slop is too small/large?

- Alternative approach: [Describe if not using TimeSynchronizer]

## Performance Results

### Accuracy
- Position error vs ground truth: [X] ± [Y] meters
- Velocity error: [X] ± [Y] m/s
- Method for validation: [How did you measure?]

### Latency
- Average fusion update latency: [X] ms
- 95th percentile latency: [X] ms
- Bottleneck: [Which sensor/operation is slowest?]

### Update Frequency
- Actual fusion update rate: [X] Hz
- Sensor update rates:
  - Camera: [X] Hz
  - LiDAR: [X] Hz
  - IMU: [X] Hz

### Resource Usage
- CPU: [X]%
- Memory: [X] MB
- Can run real-time on embedded system? [Yes/No/Maybe with optimization]

## Lessons Learned

What worked well:
- [Success 1]
- [Success 2]

Challenges encountered:
- [Challenge 1: Solution]
- [Challenge 2: Solution]

If implementing again:
- [What would you do differently?]
- [What would you optimize?]

## Future Improvements

Short term (easy):
1. [Improvement idea]
2. [Improvement idea]

Long term (challenging):
1. [Advanced idea]
2. [Advanced idea]
```

---

## Grading Rubric (100 points)

### Architecture & Design (25 points)

- [ ] (5 pts) ARCHITECTURE.md clearly documents all decisions
- [ ] (5 pts) Fusion method justified with pros/cons analysis
- [ ] (5 pts) Time synchronization strategy well-explained
- [ ] (5 pts) State vector and measurement model clearly defined
- [ ] (5 pts) DATAFLOW.txt shows clear system architecture

### Implementation (35 points)

- [ ] (10 pts) Fusion node compiles and runs without errors
- [ ] (10 pts) Time synchronization working (all 3 sensors received together)
- [ ] (8 pts) Measurement extraction for each sensor implemented
- [ ] (7 pts) Filter predict/update steps correctly implemented

### Validation & Performance (25 points)

- [ ] (8 pts) Validation script measures accuracy vs ground truth
- [ ] (8 pts) Performance benchmarking shows metrics
- [ ] (9 pts) IMPLEMENTATION_REPORT.md documents results with actual numbers

### Code Quality (15 points)

- [ ] (5 pts) All TODO comments resolved with implementation
- [ ] (5 pts) Code well-commented, follows PEP 8
- [ ] (5 pts) Error handling for edge cases (missing sensors, timeouts)

---

## Acceptance Criteria

Your submission must:

- [ ] ARCHITECTURE.md explains all design decisions
- [ ] Code compiles and runs without errors
- [ ] Sensor data being fused (verify with ros2 topic list)
- [ ] Fused estimate publishing at target frequency
- [ ] IMPLEMENTATION_REPORT.md includes actual performance measurements
- [ ] Validation shows fusion is working (covariance decreasing, error reasonable)
- [ ] All [X] placeholders filled with actual values
- [ ] Extra credit if: Covariance visualization in RViz, comparison of different fusion methods, real robot testing

---

## Testing Checklist

```bash
# Terminal 1: Start Gazebo with sensors
source /opt/ros/humble/setup.bash
cd exercise-6-2
gzserver sensor_world.world

# Terminal 2: Run fusion node
source /opt/ros/humble/setup.bash
python3 src/sensor_fusion.py

# Terminal 3: Validate output
source /opt/ros/humble/setup.bash
python3 validate_fusion.py

# Terminal 4: Visualize in RViz2
source /opt/ros/humble/setup.bash
rviz2 -d rviz_config.rviz
# Add /robot/fused_estimate (Odometry)
# Watch how covariance shrinks as fusion runs

# Terminal 5: Benchmark performance
source /opt/ros/humble/setup.bash
python3 benchmark_fusion.py
```

---

## Bonus Challenges

**Challenge 1**: Implement multiple fusion algorithms and compare (EKF vs UKF vs Particle Filter)

**Challenge 2**: Add dynamic covariance (adapt sensor trust based on recent accuracy)

**Challenge 3**: Implement loop closure detection (recognize returning to previous location)

**Challenge 4**: Test with real robot (if available)

**Challenge 5**: Optimize for real-time on embedded system (Jetson Nano, RPi 4)

---

**Congratulations!** You've implemented a professional-grade sensor fusion system! 🤖🎯
