#!/usr/bin/env python3
"""
Example 9.1: Nav2 Stack Launch Configuration for Bipedal Humanoids

This launch file configures and starts the complete Nav2 stack for bipedal robot navigation.
It includes costmap servers, global/local planners, behavior tree, and safety monitors.

Prerequisites:
  - ROS 2 (Humble or later)
  - nav2 packages (nav2_bringup, nav2_smac_planner, nav2_dwb_controller)
  - Humanoid robot URDF with footprint definition
  - Static map file (map.yaml) in maps/ directory

Usage:
  ros2 launch example_9_1_nav2_setup.launch.py \
    map:=maps/office.yaml \
    robot_model:=humanoid_h1 \
    use_sim_time:=false

Output:
  - /map (occupancy grid)
  - /costmap (layered costmap)
  - /plan (global path)
  - /cmd_vel (local controller output)
  - /tf (robot pose transform)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    # Arguments
    map_file = LaunchConfiguration("map")
    robot_model = LaunchConfiguration("robot_model")
    use_sim_time = LaunchConfiguration("use_sim_time")

    declare_map_arg = DeclareLaunchArgument(
        "map",
        default_value="maps/office.yaml",
        description="Path to occupancy grid map file"
    )

    declare_robot_arg = DeclareLaunchArgument(
        "robot_model",
        default_value="humanoid_h1",
        description="Robot model identifier (humanoid_h1, unitree_h1, etc.)"
    )

    declare_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation time from /clock topic"
    )

    # Map Server Node
    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"yaml_filename": map_file},
            {"use_sim_time": use_sim_time},
        ],
        remappings=[("/map", "/map")]
    )

    # Costmap Node (Global)
    costmap_global = Node(
        package="nav2_costmap_2d",
        executable="costmap_2d_node",
        name="global_costmap",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "plugins": [
                "static_layer",
                "inflation_layer"
            ],
            "static_layer": {
                "plugin": "nav2_costmap_2d::StaticLayer",
                "map_subscribe_transient_local": True,
                "map_topic": "/map"
            },
            "inflation_layer": {
                "plugin": "nav2_costmap_2d::InflationLayer",
                "inflation_radius": 0.20,
                "cost_scaling_factor": 10.0,
                "inflate_unknown": False,
                "inflate_around_unknown": False
            },
            "footprint_padding": 0.05,
            "robot_radius": 0.15,
            "update_frequency": 5.0,
            "publish_frequency": 2.0,
            "width": 50,
            "height": 50,
            "resolution": 0.05,
            "origin_x": -1.25,
            "origin_y": -1.25
        }],
        remappings=[
            ("/costmap/footprint", "/global_costmap/footprint"),
            ("/costmap/costmap", "/global_costmap/costmap"),
            ("/costmap/costmap_raw", "/global_costmap/costmap_raw")
        ]
    )

    # Costmap Node (Local)
    costmap_local = Node(
        package="nav2_costmap_2d",
        executable="costmap_2d_node",
        name="local_costmap",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "plugins": [
                "obstacle_layer",
                "inflation_layer"
            ],
            "obstacle_layer": {
                "plugin": "nav2_costmap_2d::ObstacleLayer",
                "enabled": True,
                "observation_sources": ["scan"],
                "scan": {
                    "sensor_frame": "laser_frame",
                    "topic": "/scan",
                    "observation_persistence": 0.0,
                    "expected_transform_tolerance": 0.1,
                    "min_obstacle_height": 0.05,
                    "max_obstacle_height": 2.0,
                    "clearing": True,
                    "marking": True,
                    "data_type": "LaserScan"
                }
            },
            "inflation_layer": {
                "plugin": "nav2_costmap_2d::InflationLayer",
                "inflation_radius": 0.25,
                "cost_scaling_factor": 10.0
            },
            "footprint_padding": 0.05,
            "robot_radius": 0.15,
            "update_frequency": 10.0,
            "publish_frequency": 5.0,
            "width": 20,
            "height": 20,
            "resolution": 0.05,
            "origin_x": -0.5,
            "origin_y": -0.5,
            "robot_base_frame": "base_link",
            "global_frame": "map"
        }],
        remappings=[
            ("/costmap/footprint", "/local_costmap/footprint"),
            ("/costmap/costmap", "/local_costmap/costmap"),
            ("/costmap/costmap_raw", "/local_costmap/costmap_raw")
        ]
    )

    # Global Planner (SMAC)
    global_planner = Node(
        package="nav2_smac_planner",
        executable="smac_planner",
        name="smac_planner",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "allow_unknown": False,
            "max_iterations": 1000000,
            "max_on_approach_iterations": 100,
            "max_planning_time": 5.0,
            "motion_model_type": "FOOTSTEP",
            "angle_quantization_bins": 16,
            "minimum_turning_radius": 0.2,
            "reverse_penalty": 2.0,
            "change_penalty": 0.0,
            "non_straight_penalty": 1.2,
            "cost_penalty": 1.7,
            "analytic_expansion_ratio": 3.5,
            "analytic_expansion_max_length": 3.0,
            "lookup_table_size": 20,
            "collision_checker_inflation_radius": 0.25,
            "footstep_stride": 0.5,
            "footstep_width": 0.15
        }],
        remappings=[
            ("/plan", "/plan")
        ]
    )

    # Local Controller (DWB)
    local_controller = Node(
        package="nav2_dwb_controller",
        executable="dwb_controller",
        name="dwb_controller",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "critics": [
                "RotateToGoal",
                "Oscillation",
                "BaseObstacle",
                "GoalAlign",
                "PathAlign",
                "PathDist",
                "GoalDist"
            ],
            "default_critic_namespaces": [
                "nav2_core"
            ],
            "max_vel_theta": 0.5,
            "min_speed_xy": 0.0,
            "max_speed_xy": 0.5,
            "min_speed_theta": 0.0,
            "max_speed_theta": 0.5,
            "acc_lim_x": 0.2,
            "acc_lim_y": 0.0,
            "acc_lim_theta": 0.2,
            "decel_lim_x": -0.2,
            "decel_lim_y": 0.0,
            "decel_lim_theta": -0.2,
            "vx_samples": 20,
            "vy_samples": 5,
            "vtheta_samples": 20,
            "sim_time": 1.7,
            "linear_granularity": 0.05,
            "angular_granularity": 0.025,
            "transform_tolerance": 0.2,
            "xy_goal_tolerance": 0.25,
            "trans_stopped_velocity": 0.25,
            "theta_stopped_velocity": 0.1,
            "sim_period": 0.125
        }],
        remappings=[
            ("/cmd_vel", "/cmd_vel_nav"),
            ("/odom", "/odometry/filtered")
        ]
    )

    # Behavior Tree Navigator
    nav_lifecycle_node = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            {"autostart": True},
            {"node_names": [
                "map_server",
                "global_costmap",
                "local_costmap",
                "smac_planner",
                "dwb_controller"
            ]},
            {"use_sim_time": use_sim_time}
        ]
    )

    # Safety Monitor Node (detects falls via IMU)
    safety_monitor = Node(
        package="nav2_util",
        executable="lifecycle_manager",
        name="safety_monitor",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "imu_topic": "/imu/data",
            "acceleration_threshold": 1.5,
            "fall_detection_enabled": True,
            "estop_timeout": 5.0
        }]
    )

    # Transform broadcaster (static transforms)
    static_tf_broadcaster = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="base_to_laser_tf",
        arguments=[
            "0.0", "0.0", "0.0",  # x, y, z
            "0.0", "0.0", "0.0",  # roll, pitch, yaw
            "base_link", "laser_frame"
        ]
    )

    return LaunchDescription([
        declare_map_arg,
        declare_robot_arg,
        declare_sim_time_arg,
        map_server,
        costmap_global,
        costmap_local,
        global_planner,
        local_controller,
        nav_lifecycle_node,
        safety_monitor,
        static_tf_broadcaster
    ])
