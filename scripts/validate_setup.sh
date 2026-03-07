#!/bin/bash
# Module 3 Quickstart Validation Script

echo "=================================================="
echo "Module 3 Setup Validation"
echo "=================================================="
echo ""

# Check NVIDIA driver
echo "1. Checking NVIDIA driver..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi | grep -E "Driver|CUDA" | head -2
    echo "✅ NVIDIA driver found"
else
    echo "❌ NVIDIA driver not found"
    exit 1
fi

# Check CUDA
echo ""
echo "2. Checking CUDA..."
if command -v nvcc &> /dev/null; then
    nvcc --version | tail -1
    echo "✅ CUDA found"
else
    echo "❌ CUDA not found"
fi

# Check Python
echo ""
echo "3. Checking Python..."
python3 --version
echo "✅ Python found"

# Check ROS 2
echo ""
echo "4. Checking ROS 2..."
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
    ros2 --version
    echo "✅ ROS 2 Humble found"
else
    echo "❌ ROS 2 not found"
fi

# Check Isaac Sim
echo ""
echo "5. Checking Isaac Sim..."
if [ -d ~/isaac-sim/isaac-sim-2023.8.1-linux ]; then
    echo "✅ Isaac Sim 2023.8 found"
else
    echo "⚠️  Isaac Sim not found in default location"
    echo "   Set ISAAC_SIM_PATH environment variable"
fi

# Check dependencies
echo ""
echo "6. Checking Python dependencies..."
python3 -c "import numpy; print('✅ NumPy')" 2>/dev/null || echo "❌ NumPy"
python3 -c "import torch; print('✅ PyTorch')" 2>/dev/null || echo "❌ PyTorch"
python3 -c "import cv2; print('✅ OpenCV')" 2>/dev/null || echo "❌ OpenCV"

echo ""
echo "=================================================="
echo "Validation Complete!"
echo "=================================================="
