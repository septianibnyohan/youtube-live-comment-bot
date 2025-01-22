"""
Core module for YouTube Live Comment Bot.

This module provides the core functionality including task management,
scheduling, configuration handling, and bot operations.
"""

from typing import Dict, List, Optional, Union, Any, TypeVar, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum, auto

# Configure module logger
logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
JsonDict = Dict[str, Any]
TaskID = str
Timestamp = float

class TaskStatus(Enum):
    """Enumeration of possible task states."""
    PENDING = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

class TaskPriority(Enum):
    """Enumeration of task priorities."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class TaskConfig:
    """Configuration for a bot task."""
    task_id: TaskID
    priority: TaskPriority = TaskPriority.NORMAL
    max_duration: Optional[int] = None
    max_retries: int = 3
    retry_delay: int = 60
    timeout: Optional[int] = None

@dataclass
class TaskResult:
    """Result of a bot task execution."""
    task_id: TaskID
    status: TaskStatus
    start_time: Timestamp
    end_time: Timestamp
    success: bool
    error: Optional[Exception] = None
    data: Optional[Dict[str, Any]] = None

class TaskCallback:
    """Callback handler for task events."""

    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_complete': [],
            'on_error': [],
            'on_pause': [],
            'on_resume': []
        }

    def register(self, event: str, callback: Callable) -> None:
        """Register a callback for an event."""
        if event not in self._callbacks:
            raise ValueError(f"Invalid event type: {event}")
        self._callbacks[event].append(callback)

    def unregister(self, event: str, callback: Callable) -> None:
        """Unregister a callback for an event."""
        if event in self._callbacks:
            try:
                self._callbacks[event].remove(callback)
            except ValueError:
                pass

    def trigger(self, event: str, *args, **kwargs) -> None:
        """Trigger callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {event} callback: {e}")

# Custom exceptions
class CoreError(Exception):
    """Base exception for core module errors."""
    pass

class TaskError(CoreError):
    """Raised when there's an error with task operations."""
    pass

class ConfigError(CoreError):
    """Raised when there's an error with configuration."""
    pass

class SchedulerError(CoreError):
    """Raised when there's an error with task scheduling."""
    pass

# Import core components
try:
    from .utils import create_task_id
    from .config import Config, load_config
    from .bot import Bot, BotConfig
    from .scheduler import Scheduler
    from .task_manager import TaskManager
except ImportError as e:
    logger.error(f"Error importing core components: {e}")
    raise

__all__ = [
    'TaskManager',
    'Scheduler',
    'Config',
    'load_config',
    'Bot',
    'BotConfig',
    'TaskStatus',
    'TaskPriority',
    'TaskConfig',
    'TaskResult',
    'TaskCallback',
    'CoreError',
    'TaskError',
    'ConfigError',
    'SchedulerError',
    'create_task_id'
]