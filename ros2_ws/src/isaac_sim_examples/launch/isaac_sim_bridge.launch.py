"""
ROS 2 launch file for Isaac Sim bridge integration.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """Generate launch description for Isaac Sim bridge."""
    
    isaac_sim_path_arg = DeclareLaunchArgument(
        'isaac_sim_path',
        default_value='/root/isaac-sim/isaac-sim-2023.8.1-linux',
        description='Path to Isaac Sim installation'
    )
    
    return LaunchDescription([
        isaac_sim_path_arg,
        
        # Isaac Sim bridge node (would be implemented)
        Node(
            package='isaac_sim_examples',
            executable='isaac_sim_bridge_node',
            name='isaac_sim_bridge',
            output='screen',
            parameters=[
                {'isaac_sim_path': LaunchConfiguration('isaac_sim_path')},
            ]
        ),
    ])
