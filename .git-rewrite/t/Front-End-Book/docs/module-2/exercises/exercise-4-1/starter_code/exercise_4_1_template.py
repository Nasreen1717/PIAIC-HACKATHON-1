#!/usr/bin/env python3
"""
Exercise 4.1 - Load & Simulate Humanoid Robot in Gazebo

TEMPLATE WITH TODO ITEMS

TODO #1: Complete the main() function
TODO #2: Implement the robot loading function
TODO #3: Implement the joint state verification
TODO #4: Implement the performance measurement

Instructions:
1. Read through the comments
2. Complete each TODO section
3. Test with: python3 exercise_4_1_template.py
4. Expected: Robot loads in Gazebo, confirms /joint_states publishing

Hints are provided for each TODO.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from gazebo_msgs.srv import SpawnEntity
import time
from pathlib import Path


class Exercise41Node(Node):
    """ROS 2 node for Exercise 4.1 - Robot Loading"""

    def __init__(self):
        super().__init__('exercise_4_1_node')
        self.logger = self.get_logger()
        self.logger.info("Exercise 4.1 Node initialized")

        # TODO #1: Create service client for spawning entities
        # Hint: Use self.create_client(SpawnEntity, '/spawn_entity')
        # Store in self.spawn_client
        self.spawn_client = None  # TODO: Implement

        # TODO #2: Create subscription to /joint_states
        # Hint: Use self.create_subscription(JointState, '/joint_states', callback, 10)
        # Store subscription and set self.robot_loaded = False initially
        self.robot_loaded = False
        self.joint_names = []

    def wait_for_service(self, timeout: int = 30) -> bool:
        """
        TODO #3: Implement service availability check

        Hints:
        - Use self.spawn_client.service_is_ready()
        - Loop for 'timeout' seconds checking if service ready
        - Log progress messages
        - Return True if ready, False if timeout

        Example pattern:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if client.service_is_ready():
                    return True
                time.sleep(1)
            return False
        """
        # TODO: Implement
        return True

    def load_robot(self, urdf_path: str, name: str, z: float = 1.0) -> bool:
        """
        TODO #4: Implement robot spawning

        Steps:
        1. Load URDF from file (use Path(urdf_path).read_text())
        2. Wait for /spawn_entity service
        3. Create SpawnEntity.Request() with:
           - request.name = name
           - request.xml = urdf_content
           - request.initial_pose.position.z = z
        4. Call service and check result
        5. Log success/failure

        Hints:
        - Check if file exists: Path(urdf_path).exists()
        - Use self.spawn_client.call_async(request)
        - Wait for future.done() before checking result
        - result.success tells if spawn worked
        """
        # TODO: Implement
        self.logger.info(f"[TODO] Load robot from {urdf_path}")
        return False

    def verify_joint_states(self, timeout: int = 10) -> bool:
        """
        TODO #5: Verify /joint_states topic

        Steps:
        1. Wait for robot_loaded flag to be set to True
        2. Check that joint_names list is not empty
        3. Log joint names received
        4. Return True if joints received within timeout

        Hints:
        - Use time.time() for timeout tracking
        - Check self.robot_loaded and self.joint_names
        - Log received joint names
        """
        # TODO: Implement
        self.logger.info("[TODO] Wait for joint states...")
        return False

    def joint_states_callback(self, msg: JointState):
        """
        TODO #6: Implement joint state callback

        This is called when /joint_states message received.

        Steps:
        1. Extract joint names: msg.name
        2. Store in self.joint_names
        3. Set self.robot_loaded = True
        4. Log the first time we receive joint states

        Hint: Only log first time (check if self.robot_loaded was False before)
        """
        # TODO: Implement
        pass

    def measure_performance(self) -> dict:
        """
        TODO #7: Measure simulation performance

        Steps:
        1. Measure /joint_states publishing rate using ros2 topic hz
        2. Check Gazebo is responding to commands
        3. Return dict with measurements

        Hints:
        - Can use subprocess to run: ros2 topic hz /joint_states
        - Expected: >10 Hz (Chapter 4 requirement)
        - Return: {'hz': float, 'status': 'OK' or 'FAIL'}
        """
        # TODO: Implement
        return {'hz': 0.0, 'status': 'NOT MEASURED'}


def main(args=None):
    """
    TODO #8: Implement main() function

    Steps:
    1. rclpy.init(args=args)
    2. Create Exercise41Node()
    3. Load robot: node.load_robot('humanoid.urdf', 'humanoid', z=1.0)
    4. Verify joint states: node.verify_joint_states()
    5. Measure performance: node.measure_performance()
    6. Print results
    7. rclpy.shutdown()

    Hints:
    - Use try/except for KeyboardInterrupt (Ctrl+C)
    - Check return values from load_robot() and verify_joint_states()
    - Print success message if all steps completed
    """
    print("\n" + "=" * 70)
    print("EXERCISE 4.1 - Load & Simulate Humanoid Robot in Gazebo")
    print("=" * 70)

    # TODO: Implement main function body
    print("[TODO] Implement main() function")

    print("=" * 70)


if __name__ == '__main__':
    exit(main())
