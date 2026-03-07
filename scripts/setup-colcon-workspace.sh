#!/bin/bash
# Colcon Workspace Setup Script
# Creates and initializes a ROS 2 colcon workspace

set -e

WORKSPACE="${1:-.}"

echo "======================================"
echo "Colcon Workspace Setup"
echo "======================================"
echo "Workspace location: $WORKSPACE"
echo ""

# Create workspace structure
echo "📁 Creating workspace directories..."
mkdir -p "$WORKSPACE/src"
mkdir -p "$WORKSPACE/build"
mkdir -p "$WORKSPACE/install"
mkdir -p "$WORKSPACE/log"

# Create a .gitignore for the workspace
echo "📝 Creating .gitignore..."
cat > "$WORKSPACE/.gitignore" <<EOF
# Colcon build directories
build/
install/
log/
colcon_build/
colcon_install/
colcon_debug/

# Python
__pycache__/
*.pyc
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

# Initialize colcon workspace
echo "🔧 Initializing colcon workspace..."
cd "$WORKSPACE"

# Create an empty src directory marker
touch src/.ros_package_path

echo "✅ Workspace created at: $WORKSPACE"
echo ""
echo "Next steps:"
echo "1. Source the ROS 2 setup:"
echo "   source /opt/ros/humble/setup.bash"
echo ""
echo "2. To build the workspace:"
echo "   colcon build"
echo ""
echo "3. To source the workspace setup:"
echo "   source install/setup.bash"
