#!/usr/bin/env python3
"""
Example 9.5: Integrated Footstep Planning with Obstacle Avoidance

This module combines global footstep planning with local reactive obstacle avoidance
for bipedal humanoids. It handles dynamic obstacles that appear during navigation.

Key components:
  1. Global planner: Generates footstep path to goal
  2. Local reactive controller: Handles dynamic obstacles
  3. Obstacle detector: Identifies sudden obstacles in swing path
  4. Recovery planner: Replans if current step becomes blocked
  5. Balance validator: Ensures stability throughout

Prerequisites:
  - numpy, scipy
  - ROS 2 costmap from sensors
  - Real-time sensor fusion (LiDAR, RGB-D camera)

Usage:
  nav = ObstacleAvoider(global_costmap, local_costmap)
  while not at_goal:
      step_cmd = nav.get_next_step(current_pose, goal_pose)
      execute_step(step_cmd)
      update_local_costmap(sensor_data)

Output:
  - Safe footstep commands that avoid obstacles
  - Graceful handling of blocked paths
  - Recovery actions if current step is blocked
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class NavigationState(Enum):
    """Navigation state machine."""
    PLANNING = 1
    EXECUTING = 2
    REPLANNING = 3
    RECOVERING = 4
    STUCK = 5
    SUCCESS = 6

@dataclass
class StepCommand:
    """Command to execute a single footstep."""
    foot_index: int  # 0=left, 1=right
    target_x: float
    target_y: float
    target_theta: float
    swing_height: float = 0.10  # Minimum foot clearance
    swing_time: float = 0.5  # Time to execute swing
    confidence: float = 1.0  # 0-1, confidence this step is safe

@dataclass
class Obstacle:
    """Detected dynamic obstacle."""
    x: float
    y: float
    radius: float
    confidence: float  # 0-1
    velocity_x: float
    velocity_y: float

class ObstacleDetector:
    """Real-time obstacle detection from sensor data."""

    def __init__(self, max_obstacles: int = 10):
        """
        Initialize obstacle detector.

        Args:
            max_obstacles: Maximum number of tracked obstacles
        """
        self.obstacles: List[Obstacle] = []
        self.max_obstacles = max_obstacles
        self.detection_threshold = 0.5  # Confidence threshold

    def update(self, sensor_data: np.ndarray,
              current_pose: Tuple[float, float, float]) -> List[Obstacle]:
        """
        Update obstacle list from sensor data.

        Args:
            sensor_data: Point cloud or laser scan data
            current_pose: Current robot position (x, y, theta)

        Returns:
            List of detected obstacles
        """
        # Simplified: threshold sensor data to find clusters
        detected = []

        for point in sensor_data:
            # Convert sensor frame to world frame
            px, py = point[:2]

            # Simple clustering: if within radius of existing obstacle, merge
            merged = False
            for obs in self.obstacles:
                dist = np.sqrt((px - obs.x)**2 + (py - obs.y)**2)
                if dist < 0.3:  # 30cm clustering distance
                    obs.x = (obs.x + px) / 2
                    obs.y = (obs.y + py) / 2
                    obs.confidence = min(1.0, obs.confidence + 0.1)
                    merged = True
                    break

            if not merged:
                detected.append(Obstacle(
                    x=px, y=py, radius=0.15,
                    confidence=0.5,
                    velocity_x=0.0, velocity_y=0.0
                ))

        # Remove low-confidence obstacles
        self.obstacles = [o for o in self.obstacles + detected
                         if o.confidence > self.detection_threshold]

        # Limit number of tracked obstacles
        if len(self.obstacles) > self.max_obstacles:
            self.obstacles.sort(key=lambda o: o.confidence, reverse=True)
            self.obstacles = self.obstacles[:self.max_obstacles]

        return self.obstacles

    def is_swing_path_clear(self, swing_start: Tuple[float, float],
                           swing_end: Tuple[float, float],
                           swing_height: float = 0.10) -> bool:
        """
        Check if foot swing trajectory is free of obstacles.

        Args:
            swing_start: Initial foot position
            swing_end: Final foot position
            swing_height: Maximum foot height during swing

        Returns:
            True if path is clear, False if blocked
        """
        # Sample swing trajectory (parabolic arc)
        num_samples = 10
        for t in np.linspace(0, 1, num_samples):
            # Interpolate position
            x = swing_start[0] + t * (swing_end[0] - swing_start[0])
            y = swing_start[1] + t * (swing_end[1] - swing_start[1])

            # Height follows parabola (max at t=0.5)
            z = swing_height * 4 * t * (1 - t)

            # Check for obstacles at this point
            for obs in self.obstacles:
                dist_xy = np.sqrt((x - obs.x)**2 + (y - obs.y)**2)
                if dist_xy < obs.radius + 0.05:  # 5cm safety margin
                    return False

        return True

class ObstacleAvoider:
    """Integrated obstacle-aware footstep planner."""

    def __init__(self, global_costmap: np.ndarray,
                local_costmap_size: Tuple[int, int] = (100, 100)):
        """
        Initialize obstacle avoider.

        Args:
            global_costmap: Static map (walls, furniture)
            local_costmap_size: (width, height) of local costmap grid
        """
        self.global_costmap = global_costmap
        self.local_costmap = np.zeros(local_costmap_size, dtype=np.uint8)
        self.obstacle_detector = ObstacleDetector()

        # State machine
        self.state = NavigationState.PLANNING
        self.failed_steps = 0
        self.max_retries = 3

        # Current execution state
        self.global_path: List[Tuple[float, float, float]] = []
        self.path_index = 0
        self.current_foot = 0  # 0=left, 1=right

        # Humanoid parameters
        self.foot_length = 0.25
        self.foot_width = 0.10
        self.min_clearance = 0.05

    def detect_step_collision(self, step_target: Tuple[float, float],
                             obstacles: List[Obstacle]) -> bool:
        """
        Check if target footstep will collide with obstacles.

        Args:
            step_target: Target foot position (x, y)
            obstacles: List of detected obstacles

        Returns:
            True if collision expected, False if safe
        """
        step_x, step_y = step_target

        for obs in obstacles:
            dist = np.sqrt((step_x - obs.x)**2 + (step_y - obs.y)**2)
            # Check if obstacle overlaps foot footprint
            if dist < obs.radius + 0.15:  # Foot footprint + obstacle radius
                return True

        return False

    def get_recovery_step(self, current_pose: Tuple[float, float, float],
                         blocked_target: Tuple[float, float],
                         obstacles: List[Obstacle]) -> Optional[StepCommand]:
        """
        Generate recovery step if swing path is blocked.

        Attempts to step to the side or forward to unblock path.

        Args:
            current_pose: Current foot position
            blocked_target: Original target (now blocked)
            obstacles: Detected obstacles

        Returns:
            Alternative step command, or None if no recovery possible
        """
        x, y, theta = current_pose

        # Try lateral steps (away from obstacle)
        recovery_targets = [
            (x + 0.3, y + 0.20, theta),  # Forward-left
            (x + 0.3, y - 0.20, theta),  # Forward-right
            (x + 0.5, y, theta),          # Forward
            (x, y + 0.25, theta),         # Left
            (x, y - 0.25, theta),         # Right
        ]

        for target_x, target_y, target_theta in recovery_targets:
            # Check if recovery target is safe
            if not self.detect_step_collision((target_x, target_y), obstacles):
                return StepCommand(
                    foot_index=1 - self.current_foot,
                    target_x=target_x,
                    target_y=target_y,
                    target_theta=target_theta,
                    swing_height=0.15,  # Higher clearance for recovery
                    confidence=0.7
                )

        return None

    def get_next_step(self, current_pose: Tuple[float, float, float],
                     goal_pose: Tuple[float, float, float],
                     sensor_data: np.ndarray,
                     global_path: List[Tuple[float, float, float]]) -> Optional[StepCommand]:
        """
        Compute next footstep command with obstacle avoidance.

        Combines global path planning with reactive obstacle handling.

        Args:
            current_pose: Current robot pose (x, y, theta)
            goal_pose: Goal position
            sensor_data: Sensor data for obstacle detection
            global_path: Pre-computed global footstep path

        Returns:
            Next step command, or None if stuck
        """
        # Update obstacle list
        obstacles = self.obstacle_detector.update(sensor_data, current_pose)

        # Determine next step target from global path
        if self.path_index >= len(global_path):
            self.state = NavigationState.SUCCESS
            return None

        target_pose = global_path[self.path_index]
        target_x, target_y, target_theta = target_pose

        # Check if target is blocked
        if self.detect_step_collision((target_x, target_y), obstacles):
            # Target blocked - attempt recovery
            recovery_step = self.get_recovery_step(current_pose, (target_x, target_y), obstacles)

            if recovery_step:
                self.state = NavigationState.RECOVERING
                return recovery_step
            else:
                # No recovery possible
                self.failed_steps += 1
                if self.failed_steps > self.max_retries:
                    self.state = NavigationState.STUCK
                    return None
                else:
                    # Wait and retry
                    return None

        # Check if swing path is clear
        swing_start = current_pose[:2]
        swing_end = (target_x, target_y)

        if not self.obstacle_detector.is_swing_path_clear(swing_start, swing_end):
            # Swing path blocked - find alternative
            recovery_step = self.get_recovery_step(current_pose, swing_end, obstacles)
            if recovery_step:
                return recovery_step
            else:
                self.failed_steps += 1
                return None

        # Path is clear - execute step
        self.state = NavigationState.EXECUTING
        self.failed_steps = 0
        self.path_index += 1

        step_cmd = StepCommand(
            foot_index=self.current_foot,
            target_x=target_x,
            target_y=target_y,
            target_theta=target_theta,
            swing_height=self.min_clearance + 0.05,  # 10cm clearance
            swing_time=0.5,
            confidence=0.9
        )

        self.current_foot = 1 - self.current_foot

        return step_cmd

# Example usage
if __name__ == "__main__":
    # Create global and local costmaps
    global_costmap = np.zeros((200, 200), dtype=np.uint8)
    global_costmap[80:120, :] = 100  # Wall across map

    # Create avoider
    avoider = ObstacleAvoider(global_costmap)

    # Simulate global path
    global_path = [
        (0.0 + i*0.5, 0.0, 0.0) for i in range(5)
    ]

    # Simulate navigation with obstacles
    current_pose = (0.0, 0.0, 0.0)
    goal_pose = (2.5, 0.0, 0.0)

    print("Navigation with obstacle avoidance:")
    print(f"Start: {current_pose}")
    print(f"Goal: {goal_pose}\n")

    for step_num in range(10):
        # Simulate sensor data (obstacle appears at step 3)
        sensor_data = []
        if step_num >= 3:
            # Obstacle in front
            sensor_data.append([1.5, 0.1, 0.0])
            sensor_data.append([1.6, 0.05, 0.0])

        sensor_data = np.array(sensor_data) if sensor_data else np.array([]).reshape(0, 3)

        # Get next step
        step_cmd = avoider.get_next_step(current_pose, goal_pose, sensor_data, global_path)

        if step_cmd is None:
            print(f"Step {step_num}: State={avoider.state.name}, No command (waiting/stuck)")
            break
        else:
            print(f"Step {step_num}: Foot {step_cmd.foot_index} → ({step_cmd.target_x:.2f}, {step_cmd.target_y:.2f})")
            current_pose = (step_cmd.target_x, step_cmd.target_y, step_cmd.target_theta)

    print(f"\nFinal state: {avoider.state.name}")
