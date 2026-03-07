"""
Module 4 VLA Common Utilities

Provides shared logging, configuration management, and error handling
for Whisper, LLM planning, and task execution components.
"""

import logging
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for a module.

    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(__name__, level="DEBUG")
        >>> logger.info("System started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level.upper())

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level.upper())
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class Config:
    """
    Configuration manager for Module 4.

    Loads environment variables from .env file and provides type-safe access.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration from environment.

        Args:
            env_file: Path to .env file (default: .env in current directory)
        """
        # Load environment file if specified
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file, override=True)
        elif os.path.exists('.env'):
            load_dotenv('.env', override=True)

        # Initialize logger
        self.logger = setup_logging(
            'module_4_config',
            level=os.getenv('LOG_LEVEL', 'INFO')
        )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Configuration value or default

        Example:
            >>> config = Config()
            >>> api_key = config.get('OPENAI_API_KEY')
        """
        return os.getenv(key, default)

    def get_required(self, key: str) -> str:
        """
        Get required configuration value.

        Args:
            key: Environment variable name

        Returns:
            Configuration value

        Raises:
            ValueError: If key not found

        Example:
            >>> config = Config()
            >>> api_key = config.get_required('OPENAI_API_KEY')
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required configuration '{key}' not found in environment")
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        try:
            return int(os.getenv(key, default))
        except (TypeError, ValueError):
            self.logger.warning(f"Could not parse {key} as integer, using default {default}")
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value."""
        try:
            return float(os.getenv(key, default))
        except (TypeError, ValueError):
            self.logger.warning(f"Could not parse {key} as float, using default {default}")
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key (required)."""
        return self.get_required('OPENAI_API_KEY')

    @property
    def openai_org_id(self) -> Optional[str]:
        """Get OpenAI organization ID (optional)."""
        return self.get('OPENAI_ORG_ID')

    @property
    def ros_domain_id(self) -> int:
        """Get ROS domain ID (default: 0)."""
        return self.get_int('ROS_DOMAIN_ID', 0)

    @property
    def log_level(self) -> str:
        """Get logging level (default: INFO)."""
        return self.get('LOG_LEVEL', 'INFO')

    @property
    def debug_mode(self) -> bool:
        """Get debug mode flag."""
        return self.get_bool('DEBUG_MODE', False)


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class Module4Error(Exception):
    """Base exception for Module 4."""
    pass


class VoiceError(Module4Error):
    """Exception from voice/Whisper processing."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code or "VOICE_ERROR"
        super().__init__(self.message)


class LLMError(Module4Error):
    """Exception from LLM planning."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code or "LLM_ERROR"
        super().__init__(self.message)


class ExecutionError(Module4Error):
    """Exception from task execution."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code or "EXECUTION_ERROR"
        super().__init__(self.message)


class ValidationError(Module4Error):
    """Exception from validation failures."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


# ============================================================================
# UTILITIES
# ============================================================================

def load_json_file(path: str) -> Dict[str, Any]:
    """
    Load JSON from file.

    Args:
        path: File path

    Returns:
        Parsed JSON object

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(path, 'r') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], path: str, indent: int = 2) -> None:
    """
    Save data to JSON file.

    Args:
        data: Data to save
        path: File path
        indent: JSON indentation (default: 2)
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Default configuration instance
config = Config()

# Default logger
logger = setup_logging('module_4', level=config.log_level)

__all__ = [
    'setup_logging',
    'Config',
    'config',
    'logger',
    'Module4Error',
    'VoiceError',
    'LLMError',
    'ExecutionError',
    'ValidationError',
    'load_json_file',
    'save_json_file',
]
