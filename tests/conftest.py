"""
pytest configuration and fixtures for ROS 2 testing.
Provides mocks, fixtures, and utilities for testing ROS 2 code examples and exercises.
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "examples"))
sys.path.insert(0, str(PROJECT_ROOT / "exercises"))


@pytest.fixture
def mock_rclpy():
    """Mock rclpy module for testing without full ROS 2 installation."""
    with patch.dict(sys.modules):
        mock_rclpy_module = MagicMock()
        mock_rclpy_module.init = MagicMock()
        mock_rclpy_module.shutdown = MagicMock()
        mock_rclpy_module.create_node = MagicMock(return_value=MagicMock())
        mock_rclpy_module.spin = MagicMock()
        mock_rclpy_module.spin_once = MagicMock()
        sys.modules['rclpy'] = mock_rclpy_module
        yield mock_rclpy_module


@pytest.fixture
def ros_environment():
    """Set up ROS 2 environment variables for testing."""
    ros_env = {
        'ROS_DISTRO': 'humble',
        'ROS_DOMAIN_ID': '42',
        'AMENT_PREFIX_PATH': '/opt/ros/humble',
    }
    original_env = {}

    # Save original values
    for key in ros_env:
        original_env[key] = os.environ.get(key)

    # Set test environment
    for key, value in ros_env.items():
        os.environ[key] = value

    yield ros_env

    # Restore original environment
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_node():
    """Create a mock ROS 2 node for testing."""
    node = MagicMock()
    node.create_publisher = MagicMock()
    node.create_subscription = MagicMock()
    node.create_service = MagicMock()
    node.create_client = MagicMock()
    node.create_action_server = MagicMock()
    node.create_action_client = MagicMock()
    node.get_logger = MagicMock(return_value=MagicMock())
    node.destroy_node = MagicMock()
    return node


@pytest.fixture
def mock_publisher():
    """Create a mock ROS 2 publisher for testing."""
    publisher = MagicMock()
    publisher.publish = MagicMock()
    return publisher


@pytest.fixture
def mock_subscriber():
    """Create a mock ROS 2 subscriber for testing."""
    subscriber = MagicMock()
    return subscriber


@pytest.fixture
def mock_service():
    """Create a mock ROS 2 service server for testing."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_service_client():
    """Create a mock ROS 2 service client for testing."""
    client = MagicMock()
    client.call_async = MagicMock()
    return client


@pytest.fixture
def mock_action_server():
    """Create a mock ROS 2 action server for testing."""
    server = MagicMock()
    return server


@pytest.fixture
def mock_action_client():
    """Create a mock ROS 2 action client for testing."""
    client = MagicMock()
    client.send_goal_async = MagicMock()
    return client


@pytest.fixture
def ros_message_string():
    """Mock std_msgs.String message."""
    string_msg = MagicMock()
    string_msg.data = "test_message"
    return string_msg


@pytest.fixture
def ros_message_int32():
    """Mock std_msgs.Int32 message."""
    int_msg = MagicMock()
    int_msg.data = 42
    return int_msg


@pytest.fixture
def example_dir():
    """Get path to examples directory."""
    return PROJECT_ROOT / "examples"


@pytest.fixture
def exercises_dir():
    """Get path to exercises directory."""
    return PROJECT_ROOT / "exercises"


@pytest.fixture
def test_data_dir():
    """Get path to test data directory."""
    test_data = PROJECT_ROOT / "tests" / "data"
    test_data.mkdir(exist_ok=True)
    return test_data


# pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "ros2: mark test as requiring ROS 2 environment"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add ros2 marker to all tests in tests/ directory
        if "tests/" in str(item.fspath):
            item.add_marker(pytest.mark.ros2)


# Helper functions for testing

def create_mock_message(message_type, **kwargs):
    """Create a mock ROS 2 message with specified fields."""
    message = MagicMock()
    for key, value in kwargs.items():
        setattr(message, key, value)
    return message


def assert_publisher_called(publisher_mock, expected_call_count=None):
    """Assert that a publisher's publish method was called."""
    assert publisher_mock.publish.called, "Publisher.publish was not called"
    if expected_call_count:
        assert publisher_mock.publish.call_count == expected_call_count, \
            f"Expected {expected_call_count} calls, got {publisher_mock.publish.call_count}"


def assert_service_response(future_mock, response_mock):
    """Assert that a service call received a response."""
    assert future_mock.done(), "Service call did not complete"
    assert future_mock.result() == response_mock


@pytest.fixture
def temp_urdf_file(tmp_path):
    """Create a temporary URDF file for testing."""
    urdf_content = """<?xml version="1.0" ?>
<robot name="test_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.1 0.1 0.1"/>
      </geometry>
    </visual>
  </link>
  <link name="right_leg">
    <visual>
      <geometry>
        <cylinder radius="0.02" length="0.4"/>
      </geometry>
    </visual>
  </link>
  <joint name="right_hip" type="revolute">
    <parent link="base_link"/>
    <child link="right_leg"/>
    <axis xyz="0 0 1"/>
    <limit lower="0" upper="1.57" effort="100" velocity="1"/>
  </joint>
</robot>
"""
    urdf_file = tmp_path / "test_robot.urdf"
    urdf_file.write_text(urdf_content)
    return urdf_file
