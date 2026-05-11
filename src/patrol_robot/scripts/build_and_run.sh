#!/bin/bash
# Hizli derleme ve calistirma scripti
# Kullanim: ./build_and_run.sh

set -e

echo "=========================================="
echo "  Smart Patrol Robot - Build & Run"
echo "=========================================="

# ROS 2 ortamini yukle
source /opt/ros/jazzy/setup.bash

# Workspace dizinine git
cd ~/patrol_robot_ws

# Derle
echo ""
echo "[1/3] Derleniyor..."
colcon build --symlink-install

# Install setup
echo ""
echo "[2/3] Ortam yukleniyor..."
source install/setup.bash

# Gazebo resource path
export GZ_SIM_RESOURCE_PATH=~/patrol_robot_ws/src/patrol_robot/worlds:$GZ_SIM_RESOURCE_PATH

# Calistir
echo ""
echo "[3/3] Simulasyon baslatiliyor..."
echo ""
ros2 launch patrol_robot patrol_simulation.launch.py
