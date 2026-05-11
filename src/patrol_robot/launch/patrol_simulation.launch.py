#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('patrol_robot')
    world_file = os.path.join(pkg_dir, 'worlds', 'patrol_world.sdf')
    
    return LaunchDescription([
        # Gazebo
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen',
        ),
        
        # Bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            ],
            output='screen',
        ),
        
        # Nodes with delay
        TimerAction(period=4.0, actions=[
            Node(package='patrol_robot', executable='patrol_node', output='screen'),
        ]),
        TimerAction(period=4.0, actions=[
            Node(package='patrol_robot', executable='zone_monitor', output='screen'),
        ]),
        TimerAction(period=4.0, actions=[
            Node(package='patrol_robot', executable='alert_manager', output='screen'),
        ]),
        TimerAction(period=5.0, actions=[
            Node(package='patrol_robot', executable='object_spawner', output='screen'),
        ]),
    ])
