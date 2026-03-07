"""
Module 4 VLA Data Models

Python dataclasses for voice commands, task plans, and execution traces.
Used in non-ROS 2 contexts and for local testing.

Maps to ROS 2 message types defined in custom_msgs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal
from enum import Enum


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ActionType(str, Enum):
    """Valid action types in a task plan."""
    NAVIGATE = "navigate"
    PERCEIVE = "perceive"
    MANIPULATE = "manipulate"
    REQUEST_CLARIFICATION = "request_clarification"


class StepStatus(str, Enum):
    """Status of an executed step."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class VoiceCommand:
    """
    Transcribed voice command from Whisper.

    Represents a single audio input, its transcription, and confidence.
    """
    id: str
    timestamp: datetime
    transcript: str
    confidence_score: float
    duration_seconds: float
    language: str = "en"
    model_version: str = "base"
    raw_audio_path: Optional[str] = None

    def __post_init__(self):
        """Validate data after initialization."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"confidence_score must be 0.0-1.0, got {self.confidence_score}")
        if self.duration_seconds <= 0:
            raise ValueError(f"duration_seconds must be > 0, got {self.duration_seconds}")
        if self.duration_seconds > 300:
            raise ValueError(f"duration_seconds must be <= 300s, got {self.duration_seconds}")

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if transcription meets confidence threshold."""
        return self.confidence_score >= threshold

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'transcript': self.transcript,
            'confidence_score': self.confidence_score,
            'duration_seconds': self.duration_seconds,
            'language': self.language,
            'model_version': self.model_version,
            'raw_audio_path': self.raw_audio_path,
        }


@dataclass
class ExecutionStep:
    """
    Single actionable step within a task plan.

    Represents one action: navigate, perceive, manipulate, or request clarification.
    """
    step_index: int
    action_type: ActionType
    parameters: Dict
    expected_outcome: str
    timeout_seconds: int = 30

    def __post_init__(self):
        """Validate data after initialization."""
        if self.step_index < 1:
            raise ValueError(f"step_index must be >= 1, got {self.step_index}")
        if not isinstance(self.action_type, ActionType):
            try:
                self.action_type = ActionType(self.action_type)
            except ValueError:
                raise ValueError(f"Invalid action_type: {self.action_type}")
        if not (1 <= self.timeout_seconds <= 120):
            raise ValueError(f"timeout_seconds must be 1-120, got {self.timeout_seconds}")

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'step_index': self.step_index,
            'action_type': self.action_type.value,
            'parameters': self.parameters,
            'expected_outcome': self.expected_outcome,
            'timeout_seconds': self.timeout_seconds,
        }


@dataclass
class TaskPlan:
    """
    Decomposed task plan from LLM.

    Represents a high-level goal broken into actionable steps.
    """
    id: str
    timestamp: datetime
    voice_command_id: str
    goal: str
    steps: List[ExecutionStep]
    metadata: Dict = field(default_factory=dict)
    estimated_duration_seconds: float = 30.0

    def __post_init__(self):
        """Validate data after initialization."""
        if not (1 <= len(self.steps) <= 20):
            raise ValueError(f"steps must be 1-20, got {len(self.steps)}")
        if self.estimated_duration_seconds <= 0:
            raise ValueError(f"estimated_duration_seconds must be > 0")

    @property
    def step_count(self) -> int:
        """Get total number of steps."""
        return len(self.steps)

    @property
    def confidence(self) -> str:
        """Get LLM confidence level from metadata."""
        return self.metadata.get('confidence', 'unknown')

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'voice_command_id': self.voice_command_id,
            'goal': self.goal,
            'steps': [step.to_dict() for step in self.steps],
            'metadata': self.metadata,
            'estimated_duration_seconds': self.estimated_duration_seconds,
        }


@dataclass
class ExecutedStep:
    """
    Result record for a single executed step.

    Records actual outcome vs expected, used within ExecutionTrace.
    """
    step_index: int
    action_type: ActionType
    status: StepStatus
    actual_duration_seconds: float
    outcome: str
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate data after initialization."""
        if self.step_index < 1:
            raise ValueError(f"step_index must be >= 1, got {self.step_index}")
        if not isinstance(self.status, StepStatus):
            try:
                self.status = StepStatus(self.status)
            except ValueError:
                raise ValueError(f"Invalid status: {self.status}")
        if self.actual_duration_seconds < 0:
            raise ValueError(f"actual_duration_seconds must be >= 0")

    @property
    def is_success(self) -> bool:
        """Check if step completed successfully."""
        return self.status == StepStatus.SUCCESS

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'step_index': self.step_index,
            'action_type': self.action_type.value,
            'status': self.status.value,
            'actual_duration_seconds': self.actual_duration_seconds,
            'outcome': self.outcome,
            'error_message': self.error_message,
        }


@dataclass
class ExecutionTrace:
    """
    Complete execution record of a task plan.

    Records actual outcomes, latencies, and debugging information.
    """
    id: str
    plan_id: str
    start_timestamp: datetime
    end_timestamp: datetime
    total_duration_seconds: float
    executed_steps: List[ExecutedStep]
    success_rate: float
    safety_incidents: int = 0
    failure_reason: Optional[str] = None
    logs: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate data after initialization."""
        if not (0.0 <= self.success_rate <= 1.0):
            raise ValueError(f"success_rate must be 0.0-1.0, got {self.success_rate}")
        if self.total_duration_seconds < 0:
            raise ValueError(f"total_duration_seconds must be >= 0")
        if self.safety_incidents < 0:
            raise ValueError(f"safety_incidents must be >= 0")

    @property
    def is_success(self) -> bool:
        """Check if execution succeeded (all steps successful)."""
        return self.success_rate == 1.0 and self.safety_incidents == 0

    @property
    def successful_steps(self) -> int:
        """Count successful steps."""
        return sum(1 for step in self.executed_steps if step.is_success)

    @property
    def failed_steps(self) -> int:
        """Count failed steps."""
        return len(self.executed_steps) - self.successful_steps

    def add_log(self, message: str) -> None:
        """
        Add debug log entry.

        Args:
            message: Log message
        """
        timestamp = datetime.now().isoformat()
        self.logs.append(f"{timestamp}: {message}")

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'start_timestamp': self.start_timestamp.isoformat(),
            'end_timestamp': self.end_timestamp.isoformat(),
            'total_duration_seconds': self.total_duration_seconds,
            'executed_steps': [step.to_dict() for step in self.executed_steps],
            'success_rate': self.success_rate,
            'safety_incidents': self.safety_incidents,
            'failure_reason': self.failure_reason,
            'logs': self.logs,
        }


__all__ = [
    'ActionType',
    'StepStatus',
    'VoiceCommand',
    'ExecutionStep',
    'TaskPlan',
    'ExecutedStep',
    'ExecutionTrace',
]
