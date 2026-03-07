#!/usr/bin/env python3
"""
Example 8.6: Isaac Sim + Isaac ROS Integration Launch File

Complete launch configuration that:
- Starts Isaac Sim with a robot and environment
- Connects Isaac ROS perception pipeline
- Integrates with Nav2 navigation stack
- Sets up sensor fusion and visualization
- Enables debugging and performance monitoring

Prerequisites:
  - Isaac Sim 2023.1+
  - Isaac ROS packages installed
  - Nav2 stack
  - RViz2 for visualization

Usage:
  ros2 launch example_8_6_ros_isaac_integration.launch.py \
    sim_headless:=False \
    nav2_enabled:=True \
    rviz:=True

Launches:
  - Isaac Sim simulator (physics + rendering)
  - Isaac ROS VSLAM node
  - Depth perception pipeline
  - Sensor fusion EKF
  - Nav2 navigation stack
  - RViz visualization
  - Performance monitoring dashboard

Output:
  [INFO] Isaac Sim initialized...
  [INFO] VSLAM node started on /odometry/visual_odometry
  [INFO] Depth perception running at 30 fps
  [INFO] Sensor fusion EKF initialized
  [INFO] Nav2 stack ready
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    """Generate launch description for Isaac Sim + Isaac ROS integration."""

    # Arguments
    sim_headless = DeclareLaunchArgument(
        'sim_headless',
        default_value='false',
        description='Run Isaac Sim in headless mode'
    )

    sim_scenario = DeclareLaunchArgument(
        'sim_scenario',
        default_value='warehouse.usd',
        description='Isaac Sim scenario file'
    )

    nav2_enabled = DeclareLaunchArgument(
        'nav2_enabled',
        default_value='true',
        description='Enable Nav2 navigation stack'
    )

    rviz_enabled = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2 visualization'
    )

    gpu_device = DeclareLaunchArgument(
        'gpu_device',
        default_value='0',
        description='GPU device index'
    )

    # Isaac Sim Node
    isaac_sim_node = Node(
        package='isaac_sim',
        executable='isaac_sim_python',
        name='isaac_sim',
        output='screen',
        parameters=[
            {'scenario_file': LaunchConfiguration('sim_scenario')},
            {'headless': LaunchConfiguration('sim_headless')},
            {'physics_dt': 0.01},
            {'rendering_dt': 0.01},
            {'gpu_device': LaunchConfiguration('gpu_device')},
        ],
        remappings=[
            ('/camera/image', '/Isaac_Sim/camera/image'),
            ('/camera/depth', '/Isaac_Sim/camera/depth'),
            ('/imu/data', '/Isaac_Sim/imu'),
        ],
        respawn=False
    )

    # Isaac ROS VSLAM Node
    vslam_node = Node(
        package='isaac_ros_vslam',
        executable='isaac_ros_vslam_node',
        name='isaac_ros_vslam',
        output='screen',
        parameters=[
            {'enable_debug_mode': False},
            {'enable_imu_fusion': True},
            {'feature_detector': 'SuperPoint'},
            {'max_features': 300},
            {'gpu_device': LaunchConfiguration('gpu_device')},
        ],
        remappings=[
            ('/camera/image_rect', '/Isaac_Sim/camera/image'),
            ('/imu/data', '/Isaac_Sim/imu'),
        ]
    )

    # Depth Perception Node
    depth_node = Node(
        package='isaac_ros_stereo_image_proc',
        executable='isaac_ros_stereo_image_proc',
        name='stereo_processor',
        output='screen',
        parameters=[
            {'queue_size': 10},
            {'input_queue_size': 5},
            {'output_queue_size': 5},
            {'gpu_device': LaunchConfiguration('gpu_device')},
        ],
        remappings=[
            ('/image_left', '/Isaac_Sim/camera/left/image'),
            ('/image_right', '/Isaac_Sim/camera/right/image'),
        ]
    )

    # Sensor Fusion EKF Node
    fusion_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='sensor_fusion',
        output='screen',
        parameters=[
            {
                'frequency': 100.0,
                'sensor_timeout': 0.1,
                'two_d_mode': False,
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_link_frame': 'base_link',
                'world_frame': 'odom',
                'publish_acceleration': True,
                'use_control': True,
                'odom0': '/odometry/visual_odometry',
                'odom0_config': [
                    True, True, True,      # position x, y, z
                    True, True, True,      # orientation r, p, y
                    False, False, False,   # velocity x, y, z
                    False, False, False,   # angular velocity r, p, y
                    False, False, False    # acceleration x, y, z
                ],
                'imu0': '/Isaac_Sim/imu',
                'imu0_config': [
                    False, False, False,   # position
                    True, True, True,      # orientation
                    False, False, False,   # velocity
                    True, True, True,      # angular velocity
                    True, True, True       # acceleration
                ],
                'odom0_relative': False,
                'imu0_relative': False,
                'imu0_remove_gravitational_acceleration': True,
                'process_noise_covariance': [
                    0.01, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.01, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.01, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.01, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.01, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.01
                ],
            }
        ]
    )

    # Nav2 Stack
    nav2_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            FindPackageShare('nav2_bringup'),
            'launch',
            'bringup_launch.py'
        ]),
        launch_arguments={
            'slam': 'False',
            'map': os.path.expanduser('~/maps/warehouse.yaml'),
            'use_sim_time': 'True',
        }.items(),
        condition=lambda context: LaunchConfiguration('nav2_enabled').perform(context) == 'true'
    )

    # RViz Visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d', PathJoinSubstitution([
                FindPackageShare('isaac_ros_vslam'),
                'rviz',
                'default.rviz'
            ])
        ],
        condition=lambda context: LaunchConfiguration('rviz').perform(context) == 'true'
    )

    # Performance Monitoring Node
    perf_monitor_node = Node(
        package='ros2_profiling',
        executable='performance_monitor_node',
        name='perf_monitor',
        output='screen',
        parameters=[
            {'publish_frequency': 1.0},  # 1 Hz
            {'log_to_file': True},
            {'output_file': '/tmp/isaac_ros_perf.log'},
        ]
    )

    # Static TF broadcasters
    base_to_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_camera_tf',
        arguments=[
            '0.0', '0.0', '0.5',  # xyz translation
            '0.0', '0.0', '0.0',  # rpy rotation
            'base_link', 'camera_frame'
        ]
    )

    map_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom_tf',
        arguments=[
            '0.0', '0.0', '0.0',  # xyz
            '0.0', '0.0', '0.0',  # rpy
            'map', 'odom'
        ]
    )

    # Bag recording (optional, for debugging)
    # rosbag_record = ExecuteProcess(
    #     cmd=['ros2', 'bag', 'record',
    #          '/odometry/visual_odometry',
    #          '/camera/depth_image',
    #          '/tf',
    #          '-o', '/tmp/isaac_ros_recording'],
    #     output='screen'
    # )

    return LaunchDescription([
        # Arguments
        sim_headless,
        sim_scenario,
        nav2_enabled,
        rviz_enabled,
        gpu_device,

        # Core nodes
        isaac_sim_node,
        vslam_node,
        depth_node,
        fusion_node,
        perf_monitor_node,

        # TF
        base_to_camera,
        map_to_odom,

        # Navigation (conditional)
        nav2_launch,

        # Visualization (conditional)
        rviz_node,
    ])
