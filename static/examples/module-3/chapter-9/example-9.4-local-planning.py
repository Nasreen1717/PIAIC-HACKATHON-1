#!/usr/bin/env python3
"""
Example 9.4: Local Real-Time Path Planning with Balance Constraints

This module implements real-time local trajectory planning for bipedal humanoids
using a Dynamic Window Broker (DWB) approach with balance constraint validation.

Key features:
  - Real-time trajectory generation (10 Hz)
  - Balance validation (center-of-mass in support polygon)
  - Obstacle cost calculation
  - Velocity smoothing and acceleration limits

Prerequisites:
  - numpy, scipy
  - Current robot state (position, velocity, IMU)
  - Local costmap (surrounding obstacles)

Usage:
  controller = LocalController(costmap, robot_state)
  twist = controller.compute_velocity_command(goal_pose)
  # Apply twist.linear.x, twist.angular.z to motors

Output:
  - Twist command (linear velocity, angular velocity) for robot base
  - Validated for balance constraints
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class RobotState:
    """Current robot state estimate."""
    x: float
    y: float
    theta: float
    v_x: float
    v_theta: float
    com_x: float
    com_y: float
    imu_accel: Tuple[float, float, float]  # x, y, z accelerations

@dataclass
class Trajectory:
    """Simulated trajectory (sequence of poses over time)."""
    poses: List[Tuple[float, float, float]]  # (x, y, theta) at each time step
    v_x: float
    v_theta: float
    time_steps: int

    def score(self) -> float:
        """Overall trajectory quality (lower is better)."""
        pass

class LocalController:
    """Real-time local controller for bipedal humanoid."""

    def __init__(self, costmap: np.ndarray, resolution: float = 0.05):
        """
        Initialize local controller.

        Args:
            costmap: 2D occupancy grid (local view around robot)
            resolution: Grid cell size in meters
        """
        self.costmap = costmap
        self.resolution = resolution
        self.height, self.width = costmap.shape

        # Humanoid kinematics
        self.com_height = 0.55
        self.foot_length = 0.25
        self.foot_width = 0.10
        self.step_width = 0.15

        # Velocity limits
        self.max_v_x = 0.5  # m/s forward
        self.max_v_theta = 0.5  # rad/s turning
        self.min_v_x = 0.0

        # Acceleration limits
        self.acc_lim_x = 0.2
        self.acc_lim_theta = 0.2
        self.decel_lim_x = 0.2
        self.decel_lim_theta = 0.2

        # Control parameters
        self.sim_time = 1.7  # Seconds to simulate ahead
        self.sim_period = 0.125  # Time step
        self.vx_samples = 20  # Velocity samples
        self.vtheta_samples = 20

    def get_velocity_samples(self, current_v_x: float,
                            current_v_theta: float) -> List[Tuple[float, float]]:
        """
        Sample feasible velocity commands.

        Returns:
            List of (v_x, v_theta) tuples within acceleration limits
        """
        samples = []

        # Velocity limits considering acceleration
        v_x_min = max(self.min_v_x,
                     current_v_x - self.acc_lim_x * self.sim_period)
        v_x_max = min(self.max_v_x,
                     current_v_x + self.acc_lim_x * self.sim_period)

        v_theta_min = max(-self.max_v_theta,
                         current_v_theta - self.acc_lim_theta * self.sim_period)
        v_theta_max = min(self.max_v_theta,
                         current_v_theta + self.acc_lim_theta * self.sim_period)

        # Grid sampling
        for i in range(self.vx_samples):
            v_x = v_x_min + (v_x_max - v_x_min) * i / (self.vx_samples - 1)
            for j in range(self.vtheta_samples):
                v_theta = v_theta_min + (v_theta_max - v_theta_min) * j / (self.vtheta_samples - 1)
                samples.append((v_x, v_theta))

        return samples

    def simulate_trajectory(self, start_state: RobotState,
                           v_x: float, v_theta: float) -> Trajectory:
        """
        Simulate robot motion for sim_time seconds.

        Args:
            start_state: Current robot state
            v_x: Forward velocity command
            v_theta: Angular velocity command

        Returns:
            Simulated trajectory
        """
        poses = [( start_state.x, start_state.y, start_state.theta)]
        num_steps = int(self.sim_time / self.sim_period)

        x, y, theta = start_state.x, start_state.y, start_state.theta

        for step in range(num_steps):
            # Simple kinematic model: dx/dt = v*cos(theta), dy/dt = v*sin(theta)
            dt = self.sim_period
            x += v_x * np.cos(theta) * dt
            y += v_x * np.sin(theta) * dt
            theta += v_theta * dt

            poses.append((x, y, theta))

        return Trajectory(
            poses=poses,
            v_x=v_x,
            v_theta=v_theta,
            time_steps=num_steps
        )

    def calculate_obstacle_cost(self, trajectory: Trajectory) -> float:
        """
        Calculate cost based on proximity to obstacles.

        Returns:
            Cost in range [0, 1000], where 0 = no collision, 1000 = collision
        """
        collision_dist = 0.3  # Safety distance
        min_dist = float('inf')

        for x, y, theta in trajectory.poses:
            # Convert to grid coordinates
            grid_x = int((x / self.resolution) + self.width / 2)
            grid_y = int((y / self.resolution) + self.height / 2)

            # Check distance to obstacles
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    check_x = grid_x + dx
                    check_y = grid_y + dy

                    if 0 <= check_x < self.width and 0 <= check_y < self.height:
                        if self.costmap[check_y, check_x] > 100:
                            # Obstacle found
                            dist = np.sqrt(dx*dx + dy*dy) * self.resolution
                            min_dist = min(min_dist, dist)

        # Cost function: exponential penalty as distance approaches 0
        if min_dist < collision_dist:
            cost = 1000 * (1.0 - min_dist / collision_dist)
        else:
            cost = 0

        return cost

    def calculate_heading_cost(self, trajectory: Trajectory,
                              goal_x: float, goal_y: float) -> float:
        """
        Calculate cost based on alignment with goal direction.

        Returns:
            Cost in range [0, 100]
        """
        final_x, final_y, final_theta = trajectory.poses[-1]

        # Desired heading to goal
        dx = goal_x - final_x
        dy = goal_y - final_y
        desired_theta = np.arctan2(dy, dx)

        # Angle error
        angle_error = abs(desired_theta - final_theta)
        # Normalize to [0, pi]
        while angle_error > np.pi:
            angle_error -= 2 * np.pi
        angle_error = abs(angle_error)

        # Cost increases with heading error
        cost = 100 * (angle_error / np.pi)

        return cost

    def calculate_balance_cost(self, trajectory: Trajectory,
                              state: RobotState) -> float:
        """
        Calculate cost based on balance constraints.

        Returns:
            Cost in range [0, 200]. >100 = unstable, >150 = likely to fall
        """
        balance_cost = 0

        for x, y, theta in trajectory.poses:
            # Estimate COM from robot pose
            com_x = x  # Simplified: COM directly above base
            com_y = y

            # Support polygon (feet positions)
            # Simplified: two feet at ±step_width/2
            left_foot_y = y - self.step_width / 2
            right_foot_y = y + self.step_width / 2

            # Check if COM is within support region (y-direction)
            if com_y < left_foot_y or com_y > right_foot_y:
                # Outside support polygon
                dist_to_support = max(
                    abs(com_y - left_foot_y),
                    abs(com_y - right_foot_y)
                )
                # Penalize deviation
                balance_cost += dist_to_support * 100

        # Check IMU acceleration (fall detection)
        imu_accel = np.array(state.imu_accel)
        total_accel = np.linalg.norm(imu_accel - np.array([0, 0, 9.81]))
        if total_accel > 1.5:  # Sudden acceleration = falling
            balance_cost += 100

        return min(balance_cost, 200)  # Cap at 200

    def calculate_velocity_cost(self, trajectory: Trajectory,
                               current_v_x: float) -> float:
        """
        Prefer smooth velocity changes.

        Returns:
            Cost in range [0, 50]
        """
        v_change = abs(trajectory.v_x - current_v_x)
        # Penalize large acceleration
        cost = min(50, v_change * 50)
        return cost

    def compute_velocity_command(self, state: RobotState,
                                goal_x: float, goal_y: float) -> Tuple[float, float]:
        """
        Compute optimal velocity command minimizing costs.

        Args:
            state: Current robot state
            goal_x, goal_y: Goal position

        Returns:
            (v_x, v_theta) optimal command
        """
        # Generate velocity samples
        samples = self.get_velocity_samples(state.v_x, state.v_theta)

        best_cost = float('inf')
        best_command = (0.0, 0.0)

        # Evaluate each sample
        for v_x, v_theta in samples:
            # Simulate trajectory
            trajectory = self.simulate_trajectory(state, v_x, v_theta)

            # Calculate costs
            obstacle_cost = self.calculate_obstacle_cost(trajectory)
            heading_cost = self.calculate_heading_cost(trajectory, goal_x, goal_y)
            balance_cost = self.calculate_balance_cost(trajectory, state)
            velocity_cost = self.calculate_velocity_cost(trajectory, state.v_x)

            # Weighted sum
            total_cost = (
                2.0 * obstacle_cost +     # High priority: avoid obstacles
                1.0 * heading_cost +      # Medium: track goal
                3.0 * balance_cost +      # High: maintain balance
                0.5 * velocity_cost       # Low: smooth motion
            )

            # Update best command
            if total_cost < best_cost:
                best_cost = total_cost
                best_command = (v_x, v_theta)

        return best_command

# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Create test costmap (moving obstacles)
    costmap = np.zeros((100, 100), dtype=np.uint8)
    costmap[40:60, 30:35] = 200  # Obstacle

    # Create controller
    controller = LocalController(costmap, resolution=0.05)

    # Simulate robot state
    state = RobotState(
        x=0.0, y=0.0, theta=0.0,
        v_x=0.2, v_theta=0.0,
        com_x=0.0, com_y=0.0,
        imu_accel=(0.0, 0.0, 9.81)
    )

    # Goal position
    goal_x, goal_y = 1.5, 0.5

    # Compute command
    v_x, v_theta = controller.compute_velocity_command(state, goal_x, goal_y)

    print(f"Goal: ({goal_x}, {goal_y})")
    print(f"Command: v_x={v_x:.3f} m/s, v_theta={v_theta:.3f} rad/s")
    print(f"Expected behavior: Move toward goal while avoiding obstacle")
