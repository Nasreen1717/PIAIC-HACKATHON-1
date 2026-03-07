# Quickstart: Module 3 Setup & First Examples

**Created**: 2026-01-23
**Purpose**: Get students from zero to running first examples in each chapter (Isaac Sim, Isaac ROS, Nav2) in <30 minutes

---

## System Requirements

### Minimum Hardware
- **GPU**: RTX 4070 Ti+ (24GB VRAM) preferred, RTX 4060 (8GB) acceptable with memory management
- **CPU**: Intel i7-12700K or AMD Ryzen 7 5700X (8+ cores recommended)
- **RAM**: 32GB system RAM
- **Disk**: 100GB free (Isaac Sim + dependencies + example datasets)

### Software Prerequisites
- **OS**: Ubuntu 22.04 LTS (tested; other Linux distributions may work)
- **Python**: 3.10 or 3.11
- **NVIDIA Driver**: 525+ (validated 550.x, 560.x)
- **NVIDIA CUDA**: 12.x (tested 12.2, 12.4)
- **ROS 2**: Humble distribution (installed via apt)

### Network
- Internet connection for downloading Isaac Sim (≈15 GB), Isaac ROS packages, dependencies
- No specific bandwidth requirements after setup

---

## Part 1: Environment Setup (15 minutes)

### Step 1.1: Install Ubuntu 22.04 LTS Base

If not already installed, use official ISO: https://releases.ubuntu.com/22.04/

```bash
# Verify Ubuntu version
lsb_release -a  # Should show "22.04 LTS"

# Update system
sudo apt update && sudo apt upgrade -y
```

### Step 1.2: Install NVIDIA Drivers & CUDA 12.x

```bash
# Install NVIDIA drivers (550.x or newer)
sudo apt install -y nvidia-driver-550

# Verify driver installation
nvidia-smi  # Should show GPU details and driver version

# Install CUDA 12.x
wget https://developer.nvidia.com/download/compute/cuda/12.4.1/local_installers/cuda_12.4.1_550.54.15_linux.run
sudo sh cuda_12.4.1_550.54.15_linux.run --silent --driver --toolkit

# Add CUDA to PATH
echo "export PATH=/usr/local/cuda/bin:$PATH" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc

# Verify CUDA installation
nvcc --version  # Should show CUDA 12.4
```

### Step 1.3: Install ROS 2 Humble

```bash
# Add ROS 2 repository
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 Humble
sudo apt update
sudo apt install -y ros-humble-desktop ros-humble-dev

# Source ROS 2 setup script
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Verify ROS 2 installation
ros2 --version  # Should show Humble
```

### Step 1.4: Install Python & Development Tools

```bash
# Install Python 3.10 + pip + venv
sudo apt install -y python3.10 python3.10-dev python3.10-venv python3-pip

# Upgrade pip
python3.10 -m pip install --upgrade pip

# Install common robotics tools
pip3 install numpy scipy matplotlib opencv-python scipy scikit-learn PyYAML colcon-common-extensions
```

---

## Part 2: Isaac Sim Installation (10 minutes)

### Step 2.1: Download Isaac Sim 2023.8

NVIDIA provides pre-built binaries. Requires free NVIDIA developer account.

```bash
# Create Isaac Sim directory
mkdir -p ~/isaac-sim
cd ~/isaac-sim

# Download Isaac Sim 2023.8.1 (≈15 GB)
# Visit: https://developer.nvidia.com/isaac/sim
# Download "Isaac Sim 2023.8.1 - Offline Release" for Linux

# Or use NVIDIA Omniverse Launcher (GUI)
# https://www.nvidia.com/en-us/omniverse/

# After download, extract
tar -xzf isaac-sim-2023.8.1-linux.tar.gz
cd isaac-sim-2023.8.1-linux
```

### Step 2.2: Validate Isaac Sim Installation

```bash
# Test Isaac Sim launch (headless or with display)
./isaac-sim.sh --version

# Launch a test scene (may take 2-3 minutes first time)
./isaac-sim.sh --headless

# Expected output: Omniverse environment ready
```

### Step 2.3: Install Isaac Sim Python Extension

```bash
# Isaac Sim ships with Python 3.10; add NVIDIA-specific packages
cd ~/isaac-sim/isaac-sim-2023.8.1-linux

# Install isaac-sim Python extension
python3.10 -m pip install isaac-sim-2023.8.1
```

---

## Part 3: Isaac ROS Installation (10 minutes)

### Step 3.1: Clone Isaac ROS Repositories

```bash
# Create ROS 2 workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone Isaac ROS repositories
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_perception.git

cd ~/ros2_ws
```

### Step 3.2: Install Isaac ROS Dependencies

```bash
# Use provided dependency installation script
cd ~/ros2_ws/src/isaac_ros_common
bash ./scripts/install_isaac_ros_dev.sh

# Install custom perception packages
cd ~/ros2_ws
colcon build --packages-select isaac_ros_visual_slam isaac_ros_perception

# Source the built packages
source ~/ros2_ws/install/setup.bash
```

### Step 3.3: Validate Isaac ROS Installation

```bash
# Check Isaac ROS packages are installed
ros2 pkg list | grep isaac_ros_visual_slam

# Expected: lists available Isaac ROS packages
```

---

## Part 4: Nav2 Installation (5 minutes)

### Step 4.1: Install Nav2 Humble

```bash
# Install Nav2 stack for Humble
sudo apt install -y ros-humble-nav2 ros-humble-nav2-bringup

# Install navigation dependencies
sudo apt install -y ros-humble-tf2 ros-humble-costmap-converter
```

### Step 4.2: Validate Nav2 Installation

```bash
# Check Nav2 is available
ros2 pkg list | grep nav2

# Expected: lists nav2 packages
```

---

## Part 5: Cloud Setup (Optional, 5 minutes)

### Option A: AWS EC2 g5.2xlarge

```bash
# 1. Launch EC2 instance
# - AMI: Ubuntu 22.04 LTS (ami-0c55b159cbfafe1f0 in us-east-1)
# - Instance type: g5.2xlarge ($1.50/hour on-demand, ~$0.45/hour spot)
# - Storage: 150GB gp3 (default 30GB insufficient)
# - Security group: Allow SSH (22), HTTP (80), HTTPS (443)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Run setup scripts above (1-4) on EC2 instance
# Ubuntu, drivers, ROS 2, Isaac Sim, Isaac ROS setup

# 4. Estimate costs
# - On-demand: $1.50/hr × 4 hours/student × 20 students = $120/session
# - Spot instances: $0.45/hr × 4 hours/student × 20 students = $36/session (recommended)
```

### Option B: NVIDIA Isaac Cloud

```bash
# 1. Visit https://www.nvidia.com/en-us/isaac/cloud/
# 2. Sign in with NVIDIA account or create new account
# 3. Launch pre-configured Isaac Sim environment
# 4. Web interface provides terminal + graphical desktop
# 5. All tools (Python, ROS 2, Isaac Sim, Isaac ROS) pre-installed
# 6. ~$0.30/hour estimated (pricing TBD at public release)

# Advantages: No setup required, instant access, managed service
```

---

## Part 6: First Examples (15 minutes total)

### Example 6.1: Hello Isaac Sim (Chapter 7)

```bash
# Create a simple Python script to verify Isaac Sim works
cat > ~/test_isaac_sim.py << 'EOF'
#!/usr/bin/env python3
"""Minimal Isaac Sim test: load scene, run 5 seconds, export data"""

from isaacsim import SimulationApp
from isaacsim.core import World
from isaacsim.core.utils.stage import add_reference_to_stage
import numpy as np

# Initialize Isaac Sim
simulation_app = SimulationApp({"headless": False})
world = World(stage_units_in_meters=1.0)

# Add a simple robot model (cube for now; URDF in Chapter 7 example)
add_reference_to_stage(
    usd_path="/Isaac/Robots/Jetbot/jetbot.usd",
    prim_path="/World/jetbot"
)

# Run simulation for 5 seconds (150 frames at 30 FPS)
for frame in range(150):
    world.step(render=True)

print("✅ Isaac Sim test PASSED: simulation ran successfully")
simulation_app.close()
EOF

python3 ~/test_isaac_sim.py

# Expected output:
# ✅ Isaac Sim test PASSED: simulation ran successfully
```

### Example 6.2: Hello VSLAM (Chapter 8)

```bash
# Create a minimal VSLAM pipeline test
cat > ~/test_vslam.py << 'EOF'
#!/usr/bin/env python3
"""Minimal Isaac ROS VSLAM test: verify perception pipeline loads"""

import rclpy
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry

rclpy.init()
node = rclpy.create_node('vslam_test')

# Check if Isaac ROS VSLAM is available
try:
    from isaac_ros_visual_slam import VisualSLAM
    print("✅ Isaac ROS VSLAM module loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Isaac ROS VSLAM: {e}")

rclpy.shutdown()
EOF

python3 ~/test_vslam.py

# Expected output:
# ✅ Isaac ROS VSLAM module loaded successfully
```

### Example 6.3: Hello Nav2 (Chapter 9)

```bash
# Launch minimal Nav2 stack
# Note: requires Isaac Sim scene running in parallel

cat > ~/test_nav2.sh << 'EOF'
#!/bin/bash
# Minimal Nav2 launch (no actual planning, just verify stack loads)

source /opt/ros/humble/setup.bash

# Check Nav2 packages
ros2 pkg list | grep -c nav2

if [ $? -eq 0 ]; then
    echo "✅ Nav2 packages available"
else
    echo "❌ Nav2 packages not found"
    exit 1
fi
EOF

bash ~/test_nav2.sh

# Expected output:
# ✅ Nav2 packages available
```

---

## Part 7: Verify Complete Installation

```bash
# Run comprehensive verification script
cat > ~/verify_installation.sh << 'EOF'
#!/bin/bash
echo "=== Module 3 Installation Verification ==="
echo

echo "1. NVIDIA GPU:"
nvidia-smi | grep -E "(GPU|CUDA)" | head -3

echo
echo "2. Ubuntu:"
lsb_release -d

echo
echo "3. Python:"
python3 --version

echo
echo "4. ROS 2:"
ros2 --version

echo
echo "5. CUDA:"
nvcc --version | tail -1

echo
echo "6. Isaac Sim:"
if [ -d ~/isaac-sim/isaac-sim-2023.8.1-linux ]; then
    echo "✅ Isaac Sim 2023.8 found"
else
    echo "❌ Isaac Sim not found"
fi

echo
echo "7. Isaac ROS:"
if grep -q "isaac_ros_visual_slam" ~/.bashrc; then
    echo "✅ Isaac ROS configured"
else
    echo "❌ Isaac ROS not in PATH"
fi

echo
echo "8. Nav2:"
if ros2 pkg list | grep -q nav2; then
    echo "✅ Nav2 installed"
else
    echo "❌ Nav2 not installed"
fi

echo
echo "=== Verification Complete ==="
EOF

bash ~/verify_installation.sh
```

---

## Part 8: Quick Diagnostics

### If Isaac Sim won't launch:
```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA
nvcc --version

# Check disk space (Isaac Sim needs >50GB free)
df -h ~/isaac-sim/

# Reinstall Isaac Sim if corrupt
rm -rf ~/isaac-sim && download fresh from NVIDIA website
```

### If Isaac ROS fails to build:
```bash
# Rebuild workspace cleanly
cd ~/ros2_ws
rm -rf build install log
colcon build --packages-select isaac_ros_visual_slam isaac_ros_perception

# Check for missing dependencies
rosdep install --from-paths src --ignore-src -r -y
```

### If Nav2 doesn't launch:
```bash
# Verify ROS 2 environment
echo $ROS_DISTRO  # Should print "humble"

# Check Nav2 packages
ros2 launch nav2_bringup bringup_launch.py map:=/path/to/map.yaml use_sim_time:=true
```

---

## Next Steps

Now that setup is complete, you're ready to:

1. **Chapter 7**: Follow examples 7.1–7.5 (URDF import, physics tuning, synthetic data)
2. **Chapter 8**: Run examples 8.1–8.6 (VSLAM pipeline, sensor fusion, GPU benchmarking)
3. **Chapter 9**: Execute examples 9.1–9.6 (Nav2 setup, bipedal planning, sim-to-real)

Each chapter includes 2 hands-on exercises with starter/solution code.

---

## Support & Troubleshooting

- **NVIDIA Isaac Sim docs**: https://docs.omniverse.nvidia.com/isaacsim/
- **Isaac ROS GitHub**: https://github.com/NVIDIA-ISAAC-ROS/
- **Nav2 documentation**: https://docs.nav2.org/
- **ROS 2 Humble docs**: https://docs.ros.org/en/humble/
- **Ubuntu 22.04 support**: https://ubuntu.com/support/

---

## Estimated Setup Time

| Task | Time | Notes |
|------|------|-------|
| System prerequisites | 5 min | Updates, basic tools |
| NVIDIA drivers + CUDA | 5 min | Download + installation |
| ROS 2 Humble | 3 min | Standard apt installation |
| Isaac Sim | 15 min | Download (~15 GB) + extraction |
| Isaac ROS | 10 min | Git clone + colcon build |
| Nav2 | 2 min | Standard apt installation |
| Verification | 3 min | Quick tests |
| **TOTAL** | **~45 min** | With typical internet speed (~50 Mbps) |

**Total time can vary based on:**
- Internet connection speed (Isaac Sim download)
- GPU capabilities (colcon build time)
- Existing NVIDIA software (driver installation)

---

## Post-Setup Next Steps

1. ✅ Run `bash ~/verify_installation.sh` to confirm all components
2. 📖 Proceed to Chapter 7, Example 7.1: "Isaac Sim Installation Validation"
3. 💻 Complete Chapter 7 exercises before moving to Chapter 8
4. 🚀 Progress to Chapter 8 (Isaac ROS VSLAM)
5. 🗺️ Finish Chapter 9 (Nav2 path planning)

Welcome to Module 3! 🤖
