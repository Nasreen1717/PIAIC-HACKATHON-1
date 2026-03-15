"""
Module 4 Common Utilities and Data Models

Provides shared infrastructure for Whisper, LLM planning, and task execution.
"""

from .common import (
    setup_logging,
    Config,
    config,
    logger,
    Module4Error,
    VoiceError,
    LLMError,
    ExecutionError,
    ValidationError,
    load_json_file,
    save_json_file,
)

from .data_models import (
    ActionType,
    StepStatus,
    VoiceCommand,
    ExecutionStep,
    TaskPlan,
    ExecutedStep,
    ExecutionTrace,
)

__version__ = "0.1.0"

__all__ = [
    # Configuration and logging
    'setup_logging',
    'Config',
    'config',
    'logger',
    # Exceptions
    'Module4Error',
    'VoiceError',
    'LLMError',
    'ExecutionError',
    'ValidationError',
    # Utilities
    'load_json_file',
    'save_json_file',
    # Data models
    'ActionType',
    'StepStatus',
    'VoiceCommand',
    'ExecutionStep',
    'TaskPlan',
    'ExecutedStep',
    'ExecutionTrace',
]
