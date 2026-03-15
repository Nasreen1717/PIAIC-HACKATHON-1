"""
Test suite for Exercise 1.1: Create a Publisher Node.

Tests validate:
- Publisher node initializes correctly
- Publishes to correct topic
- Uses correct message type (Int32)
- Publishing frequency is 1 Hz
- Counter increments correctly
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


# Add parent directory to path
EXERCISE_DIR = Path(__file__).parent
sys.path.insert(0, str(EXERCISE_DIR))


@pytest.mark.ros2
class TestCounterPublisher:
    """Test suite for CounterPublisher class."""

    def test_solution_file_exists(self):
        """Test that solution.py file exists."""
        solution_file = EXERCISE_DIR / "solution.py"
        assert solution_file.exists(), "solution.py should exist"

    def test_solution_imports(self):
        """Test that solution imports correctly."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "import rclpy" in content, "Should import rclpy"
        assert "from rclpy.node import Node" in content, "Should import Node"
        assert "from std_msgs.msg import Int32" in content, "Should import Int32"

    def test_counter_publisher_class_exists(self):
        """Test that CounterPublisher class is defined."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "class CounterPublisher" in content, "Should define CounterPublisher class"
        assert "class CounterPublisher(Node)" in content, "Should inherit from Node"

    def test_node_name_is_correct(self):
        """Test that node is named 'counter_publisher'."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "'counter_publisher'" in content or '"counter_publisher"' in content, \
            "Node should be named 'counter_publisher'"

    def test_publisher_created(self):
        """Test that publisher is created."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "create_publisher" in content, "Should create publisher with create_publisher()"
        assert "'counter_topic'" in content or '"counter_topic"' in content, \
            "Should publish to 'counter_topic'"

    def test_publisher_uses_int32_type(self):
        """Test that publisher uses Int32 message type."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "Int32" in content, "Should use Int32 message type"
        # Check that Int32 is passed to create_publisher
        assert "create_publisher(Int32" in content, "create_publisher should use Int32"

    def test_timer_created(self):
        """Test that timer is created for periodic publishing."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "create_timer" in content, "Should create timer with create_timer()"
        assert "timer_callback" in content, "Should have timer_callback method"

    def test_timer_period_correct(self):
        """Test that timer period is 1 second."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        # Look for timer creation with 1 second period
        assert "create_timer(1" in content or "create_timer(1.0" in content, \
            "Timer period should be 1 second"

    def test_message_created_and_published(self):
        """Test that Int32 message is created and published."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "msg = Int32()" in content, "Should create Int32 message"
        assert "msg.data" in content, "Should set msg.data to counter value"
        assert "publish(msg)" in content, "Should publish the message"

    def test_counter_incremented(self):
        """Test that counter increments."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "self.counter" in content, "Should have counter variable"
        assert "self.counter += 1" in content or "self.counter = self.counter + 1" in content, \
            "Should increment counter"

    def test_logging_implemented(self):
        """Test that logging is implemented."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "get_logger()" in content, "Should use get_logger()"
        assert ".info(" in content, "Should log info messages"

    def test_error_handling(self):
        """Test that error handling is implemented."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "try:" in content, "Should have try block"
        assert "except" in content, "Should have except block"
        assert "KeyboardInterrupt" in content or "Exception" in content, \
            "Should handle exceptions"

    def test_cleanup_implemented(self):
        """Test that proper cleanup is implemented."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "destroy_node()" in content, "Should call destroy_node()"
        assert "rclpy.shutdown()" in content, "Should call rclpy.shutdown()"
        assert "finally:" in content, "Should use finally block for cleanup"

    def test_main_function_exists(self):
        """Test that main() function is defined."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "def main(" in content, "Should define main() function"
        assert "rclpy.init()" in content, "main() should initialize rclpy"
        assert "rclpy.spin(" in content, "main() should spin node"

    def test_if_name_main_block(self):
        """Test that script has __main__ block."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "if __name__ == '__main__':" in content, \
            "Script should have if __name__ == '__main__': block"


@pytest.mark.ros2
class TestCounterPublisherFunctionality:
    """Test suite for Counter Publisher functionality."""

    def test_counter_starts_at_zero(self):
        """Test that counter starts at 0."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        assert "self.counter = 0" in content, "Counter should initialize to 0"

    def test_queue_size_specified(self):
        """Test that queue size is specified for publisher."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        # Should have queue_size parameter
        assert "create_publisher" in content and ("10" in content or "queue_size" in content), \
            "Should specify queue_size for publisher"

    def test_docstrings_present(self):
        """Test that classes and methods have docstrings."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        # Count docstrings
        docstring_count = content.count('"""')
        assert docstring_count >= 4, \
            f"Should have docstrings (found {docstring_count//2}, need at least 2)"


@pytest.mark.ros2
class TestCounterPublisherStyle:
    """Test suite for code style and quality."""

    def test_imports_organized(self):
        """Test that imports are organized."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()
        lines = content.split('\n')

        # rclpy should come before std_msgs in imports
        rclpy_line = next((i for i, l in enumerate(lines) if "import rclpy" in l), None)
        std_msgs_line = next((i for i, l in enumerate(lines) if "std_msgs" in l), None)

        assert rclpy_line is not None, "Should import rclpy"
        if std_msgs_line is not None:
            assert rclpy_line < std_msgs_line, "rclpy should be imported before std_msgs"

    def test_class_organization(self):
        """Test that class methods are well organized."""
        solution_file = EXERCISE_DIR / "solution.py"
        content = solution_file.read_text()

        # __init__ should come before timer_callback
        init_pos = content.find("def __init__")
        callback_pos = content.find("def timer_callback")

        assert init_pos != -1, "Should have __init__ method"
        assert callback_pos != -1, "Should have timer_callback method"
        assert init_pos < callback_pos, "__init__ should come before timer_callback"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
