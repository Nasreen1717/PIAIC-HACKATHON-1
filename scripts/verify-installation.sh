#!/bin/bash
# ROS 2 Installation Verification Script
# Verifies that ROS 2 Humble is correctly installed and configured

set -e

echo "======================================"
echo "ROS 2 Installation Verification"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: ROS 2 executable
echo "🔍 Check 1: ROS 2 executable..."
if command -v ros2 &> /dev/null; then
    ROS_VERSION=$(ros2 --version)
    echo "✅ ros2 command found: $ROS_VERSION"
else
    echo "❌ ros2 command not found"
    echo "   Please ensure /opt/ros/humble/setup.bash is sourced"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: ROS 2 environment variables
echo ""
echo "🔍 Check 2: ROS 2 environment variables..."
if [ -z "$ROS_DISTRO" ]; then
    echo "❌ ROS_DISTRO not set"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ ROS_DISTRO=$ROS_DISTRO"
fi

if [ -z "$AMENT_PREFIX_PATH" ]; then
    echo "❌ AMENT_PREFIX_PATH not set"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ AMENT_PREFIX_PATH set"
fi

# Check 3: Colcon
echo ""
echo "🔍 Check 3: Colcon build system..."
if command -v colcon &> /dev/null; then
    COLCON_VERSION=$(colcon --version)
    echo "✅ colcon found: $COLCON_VERSION"
else
    echo "⚠️  colcon not found (can be installed with: sudo apt install python3-colcon-common-extensions)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 4: Python ROS 2 client
echo ""
echo "🔍 Check 4: Python ROS 2 client (rclpy)..."
if python3 -c "import rclpy" 2>/dev/null; then
    echo "✅ rclpy (Python ROS 2 client) installed"
else
    echo "⚠️  rclpy not found (can be installed with: pip install rclpy)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 5: ROS 2 CLI tools
echo ""
echo "🔍 Check 5: ROS 2 CLI tools..."
MISSING_TOOLS=0
for tool in ros2 ros2 ros2; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS=$((MISSING_TOOLS + 1))
    fi
done

if [ $MISSING_TOOLS -eq 0 ]; then
    echo "✅ ROS 2 CLI tools available"
else
    echo "⚠️  Some CLI tools missing"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✅ All checks passed! ROS 2 is properly installed."
        exit 0
    else
        echo "⚠️  Installation is functional but some optional tools are missing."
        exit 0
    fi
else
    echo "❌ Installation has issues that need to be fixed."
    exit 1
fi
