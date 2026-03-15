"""
T020: Logging and error handling framework for Module 3.

Provides consistent error messages, debugging output, and logging configuration.
"""

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Module3Logger:
    """Consistent logger for Module 3 examples and exercises."""

    _instance: Optional['Module3Logger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'Module3Logger':
        """Singleton pattern for logger."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger."""
        if self._logger is None:
            self._logger = self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Set up logger with handlers and formatters.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger('module-3')
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # File handler
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'module-3.log')
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Get logger instance.

        Returns:
            Logger instance
        """
        return self._logger

    @staticmethod
    def debug(message: str):
        """Log debug message."""
        Module3Logger().get_logger().debug(message)

    @staticmethod
    def info(message: str):
        """Log info message."""
        Module3Logger().get_logger().info(message)

    @staticmethod
    def warning(message: str):
        """Log warning message."""
        Module3Logger().get_logger().warning(message)

    @staticmethod
    def error(message: str, exception: Optional[Exception] = None):
        """Log error message.

        Args:
            message: Error message
            exception: Optional exception object
        """
        logger = Module3Logger().get_logger()
        if exception:
            logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            logger.error(message)

    @staticmethod
    def critical(message: str):
        """Log critical message."""
        Module3Logger().get_logger().critical(message)


class Module3Error(Exception):
    """Base exception for Module 3."""
    pass


class IsaacSimError(Module3Error):
    """Isaac Sim related error."""
    pass


class VslamError(Module3Error):
    """VSLAM related error."""
    pass


class Nav2Error(Module3Error):
    """Nav2 related error."""
    pass


class PhysicsError(Module3Error):
    """Physics simulation error."""
    pass


class SyntheticDataError(Module3Error):
    """Synthetic data generation error."""
    pass


def handle_error(error_type: type, message: str) -> None:
    """Handle and log error with appropriate type.

    Args:
        error_type: Type of error
        message: Error message
    """
    Module3Logger.error(message)
    raise error_type(message)


def safe_execution(func, error_type: type, error_message: str):
    """Execute function with error handling.

    Args:
        func: Function to execute
        error_type: Error type to raise on failure
        error_message: Message for error
    """
    try:
        return func()
    except Exception as e:
        handle_error(error_type, f"{error_message}: {str(e)}")


# Common error messages
ERROR_MESSAGES = {
    'isaac_sim_not_found': 'Isaac Sim installation not found. Set ISAAC_SIM_PATH environment variable.',
    'gpu_not_found': 'NVIDIA GPU not found. Ensure NVIDIA drivers are installed.',
    'ros2_not_found': 'ROS 2 Humble not found. Run quickstart setup.',
    'vslam_failed': 'VSLAM pipeline failed. Check camera feed and sensor configuration.',
    'nav2_failed': 'Nav2 planning failed. Check costmap and planner configuration.',
    'physics_divergence': 'Physics simulation diverged. Check gravity and friction parameters.',
    'gpu_memory': 'Insufficient GPU memory. Reduce batch size or image resolution.',
}


def get_error_message(key: str) -> str:
    """Get error message by key.

    Args:
        key: Error message key

    Returns:
        Error message string
    """
    return ERROR_MESSAGES.get(key, 'Unknown error')


# Initialize logger at module load
logger = Module3Logger()
