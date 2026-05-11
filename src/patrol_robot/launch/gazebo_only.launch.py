#!/usr/bin/env python3
"""
Sadece Gazebo simülasyonunu başlatır (test için)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('patrol_robot')
    world_file = os.path.join(pkg_dir, 'worlds', 'patrol_world.sdf')
    
    return LaunchDescription([
        # Gazebo simülasyonu
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen',
            name='gazebo'
        ),
        
        # ROS-Gazebo köprüsü
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='gz_bridge',
            output='screen',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            ],
        ),
    ])
