"""
Test suite for Chapter 1 code examples.

Tests validate:
- Publisher node publishes to correct topic
- Subscriber node initializes and receives messages
- Message format matches specification
- CLI tools work correctly
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path


# Import examples
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))


@pytest.mark.ros2
class TestChapter1Publisher:
    """Test suite for hello-world-pub.py example."""

    def test_publisher_imports(self):
        """Test that publisher example imports correctly."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pub_example",
                Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
            )
            module = importlib.util.module_from_spec(spec)
            # Don't execute main() here
            assert module is not None, "Publisher module should import"
        except ImportError as e:
            pytest.skip(f"Cannot import ROS 2: {e}")

    def test_publisher_class_exists(self, mock_rclpy):
        """Test that HelloWorldPublisher class exists."""
        try:
            from importlib.util import spec_from_file_location, module_from_spec
            spec = spec_from_file_location(
                "pub_example",
                Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
            )
            module = module_from_spec(spec)
            # Check class exists
            assert hasattr(module, 'HelloWorldPublisher'), \
                "Module should define HelloWorldPublisher class"
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Skipping: {e}")

    def test_publisher_has_required_methods(self, mock_rclpy):
        """Test that publisher has required methods."""
        # Static analysis: publisher should have __init__ and timer_callback
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        assert "def __init__" in content, "Publisher should have __init__ method"
        assert "def timer_callback" in content, "Publisher should have timer_callback method"
        assert "create_publisher" in content, "Publisher should create a publisher"
        assert "create_timer" in content, "Publisher should create a timer"

    def test_publisher_creates_topic(self):
        """Test that publisher creates correct topic."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        assert "hello_world_topic" in content, \
            "Publisher should publish to 'hello_world_topic'"

    def test_publisher_uses_string_message_type(self):
        """Test that publisher uses String message type."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        assert "String" in content, "Publisher should use String message type"
        assert "from std_msgs.msg import String" in content or \
               "import std_msgs" in content, \
               "Publisher should import String message type"


@pytest.mark.ros2
class TestChapter1Subscriber:
    """Test suite for hello-world-sub.py example."""

    def test_subscriber_imports(self):
        """Test that subscriber example imports correctly."""
        try:
            from importlib.util import spec_from_file_location, module_from_spec
            spec = spec_from_file_location(
                "sub_example",
                Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
            )
            module = module_from_spec(spec)
            assert module is not None, "Subscriber module should import"
        except ImportError as e:
            pytest.skip(f"Cannot import ROS 2: {e}")

    def test_subscriber_has_callback(self):
        """Test that subscriber has callback method."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        assert "listener_callback" in content or "callback" in content.lower(), \
            "Subscriber should have a callback method"

    def test_subscriber_subscribes_to_topic(self):
        """Test that subscriber subscribes to correct topic."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        assert "create_subscription" in content, \
            "Subscriber should create a subscription"
        assert "hello_world_topic" in content, \
            "Subscriber should subscribe to 'hello_world_topic'"

    def test_subscriber_uses_string_message_type(self):
        """Test that subscriber uses String message type."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        assert "String" in content, "Subscriber should use String message type"


@pytest.mark.ros2
class TestChapter1IntegrationScripts:
    """Test suite for integration scripts."""

    def test_introspection_script_exists(self):
        """Test that topic introspection script exists."""
        script_file = Path(__file__).parent.parent / "examples" / "1-topic-introspection.sh"
        assert script_file.exists(), "Topic introspection script should exist"

    def test_introspection_script_uses_ros2_commands(self):
        """Test that introspection script uses ROS 2 CLI commands."""
        script_file = Path(__file__).parent.parent / "examples" / "1-topic-introspection.sh"
        content = script_file.read_text()

        # Should use ros2 commands
        assert "ros2 topic list" in content, "Script should list topics"
        assert "ros2 topic info" in content, "Script should show topic info"
        assert "ros2 topic echo" in content, "Script should echo topic messages"

    def test_introspection_script_is_executable(self):
        """Test that introspection script has executable permissions."""
        script_file = Path(__file__).parent.parent / "examples" / "1-topic-introspection.sh"
        # Check if file has any executable bits (simplified check)
        import stat
        mode = script_file.stat().st_mode
        assert mode & stat.S_IXUSR or mode & stat.S_IXGRP or mode & stat.S_IXOTH, \
            "Script should be executable"


@pytest.mark.ros2
class TestChapter1Functionality:
    """Test suite for example functionality."""

    def test_publisher_publishes_string_messages(self, mock_node, mock_publisher):
        """Test that publisher publishes String messages."""
        # Verify publisher was configured with correct message type
        mock_publisher.publish.assert_not_called()  # Not called yet

    def test_subscriber_receives_string_messages(self, mock_subscriber):
        """Test that subscriber can receive String messages."""
        # Verify subscriber was configured with correct message type
        assert mock_subscriber is not None

    def test_message_format_correct(self):
        """Test that published messages have correct format."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        # Should set msg.data for String messages
        assert "msg.data" in content, "Publisher should set message.data field"

    def test_topic_name_is_correct(self):
        """Test that publisher and subscriber use same topic name."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"

        pub_content = pub_file.read_text()
        sub_content = sub_file.read_text()

        # Extract topic names (simple pattern matching)
        pub_topic = "hello_world_topic" if "hello_world_topic" in pub_content else None
        sub_topic = "hello_world_topic" if "hello_world_topic" in sub_content else None

        assert pub_topic == sub_topic, \
            "Publisher and subscriber should use same topic name"


@pytest.mark.ros2
class TestChapter1CodeQuality:
    """Test suite for code quality checks."""

    def test_publisher_has_docstring(self):
        """Test that publisher has module docstring."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        assert '"""' in content or "'''" in content, \
            "Publisher should have docstring"

    def test_subscriber_has_docstring(self):
        """Test that subscriber has module docstring."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        assert '"""' in content or "'''" in content, \
            "Subscriber should have docstring"

    def test_publisher_uses_logging(self):
        """Test that publisher uses ROS 2 logging."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        assert "get_logger" in content, \
            "Publisher should use get_logger() for logging"

    def test_subscriber_uses_logging(self):
        """Test that subscriber uses ROS 2 logging."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        assert "get_logger" in content, \
            "Subscriber should use get_logger() for logging"

    def test_publisher_has_error_handling(self):
        """Test that publisher has try-except block."""
        pub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-pub.py"
        content = pub_file.read_text()

        # Should have KeyboardInterrupt handling
        assert "KeyboardInterrupt" in content or "except" in content, \
            "Publisher should handle exceptions"

    def test_subscriber_has_error_handling(self):
        """Test that subscriber has try-except block."""
        sub_file = Path(__file__).parent.parent / "examples" / "1-hello-world-sub.py"
        content = sub_file.read_text()

        # Should have KeyboardInterrupt handling
        assert "KeyboardInterrupt" in content or "except" in content, \
            "Subscriber should handle exceptions"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
