"""
Utilities module for YouTube Live Comment Bot.

This module provides common utility functions, decorators, and helper classes
used throughout the application.
"""

import os
import sys
import time
import logging
import functools
import traceback
from typing import Any, Callable, TypeVar, Optional, Dict
from pathlib import Path
from datetime import datetime

# Type variables for generic functions
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Configure module logger
logger = logging.getLogger(__name__)


class UtilsError(Exception):
    """Base exception for utilities module."""
    pass


def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """Decorator for retrying operations.

    Args:
        max_attempts: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplicative factor for delay between retries.
        exceptions: Tuple of exceptions to catch and retry.

    Returns:
        Callable: Decorated function.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in "
                            f"{current_delay} seconds: {str(e)}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    continue

            raise last_exception

        return wrapper

    return decorator


def timing_decorator(func: F) -> F:
    """Decorator to measure function execution time.

    Args:
        func: Function to measure.

    Returns:
        Callable: Decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logger.debug(
            f"Function {func.__name__} took "
            f"{end_time - start_time:.2f} seconds"
        )
        return result

    return wrapper


def setup_crash_handler() -> None:
    """Setup system-wide exception handler for crash reporting."""

    def handle_exception(exc_type: type, exc_value: Exception, exc_traceback: Any) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def setup_exception_logging() -> None:
    """Configure exception logging for the application."""
    log_dir = Path(os.getcwd()) / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"exceptions_{datetime.now().strftime('%Y%m%d')}.log"

    # Configure file handler for exceptions
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to root logger
    logging.getLogger().addHandler(handler)


def get_app_path() -> Path:
    """Get the application's root directory path.

    Returns:
        Path: Application root directory.
    """
    return Path(__file__).parent.parent.parent


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure.

    Raises:
        UtilsError: If directory creation fails.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise UtilsError(f"Failed to create directory {path}: {e}")


def format_time_delta(seconds: float) -> str:
    """Format time delta in seconds to human-readable string.

    Args:
        seconds: Number of seconds.

    Returns:
        str: Formatted time string.
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length.

    Args:
        text: String to truncate.
        max_length: Maximum length.

    Returns:
        str: Truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


class Singleton:
    """Singleton metaclass for ensuring only one instance of a class."""

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def memoize(func: F) -> F:
    """Decorator to memoize function results.

    Args:
        func: Function to memoize.

    Returns:
        Callable: Decorated function.
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


# Import utility modules
try:
    from . import validators
    from . import helpers
    from . import decorators
except ImportError as e:
    logger.error(f"Error importing utility modules: {e}")
    raise

__all__ = [
    'retry',
    'timing_decorator',
    'setup_crash_handler',
    'setup_exception_logging',
    'get_app_path',
    'ensure_dir',
    'format_time_delta',
    'truncate_string',
    'Singleton',
    'memoize',
    'UtilsError',
]

# Clean up namespace
del os
del sys
del time
del logging
del functools
del traceback
del datetime
del Path