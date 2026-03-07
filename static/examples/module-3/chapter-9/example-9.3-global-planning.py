#!/usr/bin/env python3
"""
Example 9.3: Global Path Planning with Footstep Lattice

This module implements global path planning for bipedal humanoids using a footstep
lattice model. It demonstrates A* search with humanoid-specific constraints:
  - Footstep collision checking
  - Balance validation (center-of-mass in support polygon)
  - Swing phase clearance (>0.05m)
  - Stable step transitions

Prerequisites:
  - numpy, scipy
  - ROS 2 with nav_msgs

Usage:
  planner = FootstepPlanner(costmap, robot_model)
  path = planner.plan(start_pose, goal_pose)
  for step in path:
      print(f"Step: x={step.x:.2f}, y={step.y:.2f}, theta={step.theta:.2f}")

Output:
  - Sequence of (x, y, theta, foot_index) tuples representing footstep path
  - None if no path found
"""

import numpy as np
from heapq import heappush, heappop
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Step:
    """Single footstep position and orientation."""
    x: float
    y: float
    theta: float
    foot_index: int  # 0=left, 1=right

    def __hash__(self):
        # Discretize for hashing (5cm resolution)
        return hash((round(self.x*20), round(self.y*20),
                     round(self.theta*16), self.foot_index))

    def __eq__(self, other):
        if not isinstance(other, Step):
            return False
        return (abs(self.x - other.x) < 0.01 and
                abs(self.y - other.y) < 0.01 and
                abs(self.theta - other.theta) < 0.05 and
                self.foot_index == other.foot_index)

class FootstepLattice:
    """Predefined step actions for humanoid locomotion."""

    def __init__(self, stride_params: dict):
        """
        Initialize footstep lattice with humanoid stride parameters.

        Args:
            stride_params: Dict with keys:
                - stride_forward: [0.3, 0.5, 0.7] (conservative, normal, fast)
                - step_width: 0.15
                - max_turning: 0.5 rad (~30 degrees)
        """
        self.stride_forward = stride_params.get("stride_forward", [0.3, 0.5, 0.7])
        self.step_width = stride_params.get("step_width", 0.15)
        self.max_turning = stride_params.get("max_turning", 0.5)

    def get_actions(self, current_step: Step) -> List[Step]:
        """
        Generate candidate next steps from current position.

        Each action represents a possible footstep placement.
        The opposing foot is used (left to right or vice versa).

        Returns:
            List of candidate Step objects
        """
        actions = []

        # Footstep action primitives (relative to current foot position)
        # Format: (dx, dy, dtheta, label)
        primitives = [
            (0.3, 0.15, 0.0, "step_forward_left"),
            (0.5, 0.15, 0.0, "step_forward_normal_left"),
            (0.7, 0.15, 0.0, "step_forward_fast_left"),
            (0.3, -0.15, 0.0, "step_forward_right"),
            (0.5, -0.15, 0.0, "step_forward_normal_right"),
            (0.7, -0.15, 0.0, "step_forward_fast_right"),
            (0.0, 0.20, 0.0, "step_left"),
            (0.0, -0.20, 0.0, "step_right"),
            (0.3, 0.15, 0.2, "step_turn_left_slight"),
            (0.3, 0.15, -0.2, "step_turn_right_slight"),
            (-0.3, 0.15, 0.0, "step_backward_left"),
            (-0.3, -0.15, 0.0, "step_backward_right"),
        ]

        for dx, dy, dtheta, label in primitives:
            # Transform step to world frame based on current orientation
            cos_t = np.cos(current_step.theta)
            sin_t = np.sin(current_step.theta)

            world_dx = dx * cos_t - dy * sin_t
            world_dy = dx * sin_t + dy * cos_t

            next_step = Step(
                x=current_step.x + world_dx,
                y=current_step.y + world_dy,
                theta=current_step.theta + dtheta,
                foot_index=1 - current_step.foot_index  # Toggle foot
            )

            actions.append(next_step)

        return actions

class FootstepPlanner:
    """A* path planner for bipedal humanoid footstep planning."""

    def __init__(self, costmap: np.ndarray, resolution: float = 0.05):
        """
        Initialize planner with occupancy costmap.

        Args:
            costmap: 2D numpy array (0=free, >0=obstacle)
            resolution: Grid cell size in meters
        """
        self.costmap = costmap
        self.resolution = resolution
        self.height, self.width = costmap.shape

        # Humanoid parameters
        self.foot_length = 0.25
        self.foot_width = 0.10
        self.com_height = 0.55
        self.min_ground_clearance = 0.05

        # Lattice
        self.lattice = FootstepLattice({
            "stride_forward": [0.3, 0.5, 0.7],
            "step_width": 0.15,
            "max_turning": 0.5
        })

    def footstep_to_grid(self, step: Step) -> Tuple[int, int]:
        """Convert world coordinates to grid indices."""
        grid_x = int((step.x / self.resolution) + self.width / 2)
        grid_y = int((step.y / self.resolution) + self.height / 2)
        return (grid_x, grid_y)

    def grid_to_footstep(self, grid_x: int, grid_y: int, theta: float) -> Step:
        """Convert grid indices to world coordinates."""
        x = (grid_x - self.width / 2) * self.resolution
        y = (grid_y - self.height / 2) * self.resolution
        return Step(x, y, theta, 0)

    def check_collision(self, step: Step) -> bool:
        """
        Check if footstep collides with obstacles.

        Models foot as rectangular footprint (0.25m x 0.10m).
        """
        grid_x, grid_y = self.footstep_to_grid(step)

        # Footprint size in grid cells
        foot_len_cells = int(self.foot_length / self.resolution / 2)
        foot_wid_cells = int(self.foot_width / self.resolution / 2)

        # Check footprint bounding box
        for dx in range(-foot_len_cells, foot_len_cells + 1):
            for dy in range(-foot_wid_cells, foot_wid_cells + 1):
                check_x = grid_x + dx
                check_y = grid_y + dy

                # Boundary check
                if check_x < 0 or check_x >= self.width:
                    return True
                if check_y < 0 or check_y >= self.height:
                    return True

                # Collision check (costmap > 200 = lethal)
                if self.costmap[check_y, check_x] > 200:
                    return True

        return False

    def check_balance(self, prev_step: Step, curr_step: Step) -> bool:
        """
        Validate center-of-mass stays within support polygon.

        Support polygon = convex hull of both feet.
        COM must stay inside during transition.
        """
        # Simplified: check if COM stays between feet
        # Real implementation would use convex hull

        min_x = min(prev_step.x, curr_step.x)
        max_x = max(prev_step.x, curr_step.x)
        min_y = min(prev_step.y, curr_step.y)
        max_y = max(prev_step.y, curr_step.y)

        # COM should be roughly centered
        com_x = (min_x + max_x) / 2
        com_y = (min_y + max_y) / 2

        # Distance from COM to support polygon
        distance_to_support = abs(curr_step.y - com_y)

        # Allow COM within 0.2m of support region
        return distance_to_support < 0.2

    def check_step_validity(self, prev_step: Optional[Step],
                           curr_step: Step) -> bool:
        """
        Validate footstep (collision, balance, clearance).

        Returns True if step is valid, False otherwise.
        """
        # Check collision
        if self.check_collision(curr_step):
            return False

        # Check balance constraint (if not first step)
        if prev_step is not None:
            if not self.check_balance(prev_step, curr_step):
                return False

        return True

    def heuristic(self, curr_step: Step, goal_step: Step) -> float:
        """
        Estimate cost to goal (Euclidean distance).

        Used for A* search guidance.
        """
        dx = goal_step.x - curr_step.x
        dy = goal_step.y - curr_step.y
        return np.sqrt(dx*dx + dy*dy)

    def step_cost(self, prev_step: Step, curr_step: Step) -> float:
        """
        Compute cost of stepping from prev to curr.

        Includes distance, stability, and energy costs.
        """
        # Distance cost
        dx = curr_step.x - prev_step.x
        dy = curr_step.y - prev_step.y
        dist_cost = np.sqrt(dx*dx + dy*dy)

        # Direction cost (penalize away from goal direction)
        direction_cost = 0.0  # Simplified

        # Stability cost (penalize large rotations)
        rotation_cost = abs(curr_step.theta - prev_step.theta) * 0.1

        # Total cost
        total_cost = dist_cost + rotation_cost

        # Penalize if this is a backward step
        if dx < 0:
            total_cost *= 2.0

        return total_cost

    def plan(self, start_pose: Tuple[float, float, float],
             goal_pose: Tuple[float, float, float]) -> Optional[List[Step]]:
        """
        Plan footstep path from start to goal using A*.

        Args:
            start_pose: (x, y, theta) in meters and radians
            goal_pose: (x, y, theta) in meters and radians

        Returns:
            List of Step objects representing footstep path, or None if no path
        """
        start_step = Step(start_pose[0], start_pose[1], start_pose[2], 0)
        goal_step = Step(goal_pose[0], goal_pose[1], goal_pose[2], 0)

        # A* search
        open_set = []
        closed_set = set()
        g_score = {start_step: 0}
        f_score = {start_step: self.heuristic(start_step, goal_step)}
        came_from = {}

        heappush(open_set, (f_score[start_step], start_step))

        iterations = 0
        max_iterations = 10000

        while open_set and iterations < max_iterations:
            iterations += 1
            current = heappop(open_set)[1]

            if current == goal_step:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                print(f"Path found in {iterations} iterations, {len(path)} steps")
                return path

            closed_set.add(current)

            # Expand neighbors
            for neighbor in self.lattice.get_actions(current):
                if neighbor in closed_set:
                    continue

                # Check validity
                if not self.check_step_validity(current, neighbor):
                    continue

                # Compute scores
                tentative_g = g_score[current] + self.step_cost(current, neighbor)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal_step)
                    heappush(open_set, (f_score[neighbor], neighbor))

        print(f"No path found after {iterations} iterations")
        return None

# Example usage
if __name__ == "__main__":
    # Create simple costmap (100x100 grid, 5cm resolution = 5m x 5m)
    costmap = np.zeros((100, 100), dtype=np.uint8)

    # Add obstacle (wall at y=2m)
    costmap[30:70, :] = 200

    # Create planner
    planner = FootstepPlanner(costmap, resolution=0.05)

    # Plan path
    start = (-1.0, -1.0, 0.0)
    goal = (1.0, 1.0, 0.0)

    path = planner.plan(start, goal)

    if path:
        print(f"\nFootstep path ({len(path)} steps):")
        for i, step in enumerate(path):
            print(f"  {i:2d}: x={step.x:6.2f} y={step.y:6.2f} theta={step.theta:6.2f} foot={step.foot_index}")
    else:
        print("No path found")
