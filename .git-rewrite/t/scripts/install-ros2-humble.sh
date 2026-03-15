#!/bin/bash
# ROS 2 Humble Installation Script for Ubuntu 22.04
# This script automates the installation of ROS 2 Humble on Ubuntu 22.04 LTS

set -e  # Exit on error

echo "===================================="
echo "ROS 2 Humble Installation for Ubuntu 22.04"
echo "===================================="

# Check if running on Ubuntu 22.04
if [ ! -f /etc/os-release ]; then
    echo "❌ Error: Cannot determine OS"
    exit 1
fi

source /etc/os-release
if [ "$VERSION_ID" != "22.04" ]; then
    echo "⚠️  Warning: This script is tested on Ubuntu 22.04"
    echo "   Current version: $VERSION_ID"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Setup locale
echo "📝 Setting up locale..."
sudo apt update
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Step 2: Enable Ubuntu Universe repository
echo "📦 Enabling Ubuntu Universe repository..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe

# Step 3: Add ROS 2 GPG key
echo "🔑 Adding ROS 2 GPG key..."
sudo apt install -y curl
sudo curl -sSL https://raw.githubusercontent.com/ros/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Step 4: Add ROS 2 repository
echo "📚 Adding ROS 2 repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.sources.list > /dev/null

# Step 5: Install ROS 2 Humble
echo "⬇️  Installing ROS 2 Humble..."
sudo apt update
sudo apt install -y ros-humble-desktop-full

# Step 6: Install additional utilities
echo "🛠️  Installing additional tools..."
sudo apt install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip

# Step 7: Initialize rosdep
echo "🔧 Initializing rosdep..."
if [ ! -d /etc/ros/rosdep ]; then
    sudo rosdep init
fi
rosdep update

# Step 8: Verify installation
echo "✅ Verifying installation..."
source /opt/ros/humble/setup.bash
ROS_VERSION=$(ros2 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ ROS 2 installed successfully!"
    echo "   Version: $ROS_VERSION"
else
    echo "❌ ROS 2 installation failed"
    exit 1
fi

echo ""
echo "===================================="
echo "Installation Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Source the ROS 2 setup script:"
echo "   source /opt/ros/humble/setup.bash"
echo ""
echo "2. Test the installation:"
echo "   ros2 --version"
echo ""
echo "3. To automatically source ROS 2, add to ~/.bashrc:"
echo "   source /opt/ros/humble/setup.bash"
