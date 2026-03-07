"""
Pytest configuration and fixtures for Module 3 tests.
"""

import pytest
import sys
from pathlib import Path

# Add source directories to path
sys.path.insert(0, str(Path(__file__).parent / "static" / "examples" / "module-3"))
sys.path.insert(0, str(Path(__file__).parent / "static" / "exercises" / "module-3"))


@pytest.fixture
def isaac_sim_path():
    """Fixture for Isaac Sim installation path."""
    return "/home/user/isaac-sim/isaac-sim-2023.8.1-linux"


@pytest.fixture
def test_urdf():
    """Fixture for test URDF file."""
    return "static/models/module-3/humanoid_robot.urdf"


@pytest.fixture
def test_scene():
    """Fixture for test Isaac Sim scene."""
    return "static/config/module-3/scenes/test_environment.yaml"


@pytest.fixture
def gpu_available():
    """Check if GPU is available for testing."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.fixture
def ros2_environment():
    """Setup ROS 2 environment for tests."""
    import os
    ros2_setup = "/opt/ros/humble/setup.bash"
    return {
        "ROS_DISTRO": "humble",
        "ROS_PYTHON_VERSION": "3",
        "ROS2_SETUP": ros2_setup if Path(ros2_setup).exists() else None
    }
