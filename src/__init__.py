"""
YouTube Live Comment Bot

A powerful and customizable YouTube automation tool built with Python and PyQt6
for managing YouTube live chat interactions.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Package metadata
__title__ = 'youtube_live_bot'
__version__ = '1.0.0'
__author__ = 'Your Name'
__author_email__ = 'your.email@example.com'
__license__ = 'MIT'
__copyright__ = f'Copyright 2024 {__author__}'

# Set up package-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure rotating file handler
log_file = os.path.join(logs_dir, 'youtube_bot.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Configure console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Type aliases for commonly used types
ProxyConfig = Dict[str, Any]
BrowserConfig = Dict[str, Any]
CommentList = List[str]
TimeRange = Tuple[int, int]
ScheduleConfig = Optional[Dict[str, Any]]


# Custom exceptions
class YouTubeBotError(Exception):
    """Base exception for YouTube Bot errors."""
    pass


class BrowserError(YouTubeBotError):
    """Raised when there's an error with browser operations."""
    pass


class ProxyError(YouTubeBotError):
    """Raised when there's an error with proxy operations."""
    pass


class ValidationError(YouTubeBotError):
    """Raised when validation fails."""
    pass


class ConfigError(YouTubeBotError):
    """Raised when there's a configuration error."""
    pass


# Version info tuple
VERSION_INFO = tuple(map(int, __version__.split('.')))


def get_version() -> str:
    """Return the package version."""
    return __version__


def get_logger() -> logging.Logger:
    """Return the package logger."""
    return logger


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging with custom level.

    Args:
        level: The logging level to set. Defaults to logging.INFO.
    """
    logger.setLevel(level)
    file_handler.setLevel(level)
    console_handler.setLevel(level)


# Path utilities
def get_package_root() -> str:
    """Return the package root directory."""
    return os.path.dirname(os.path.dirname(__file__))


def get_resource_path(resource: str) -> str:
    """Get the full path to a resource file.

    Args:
        resource: Resource file name or relative path.

    Returns:
        str: Full path to the resource.

    Raises:
        FileNotFoundError: If the resource doesn't exist.
    """
    resource_path = os.path.join(get_package_root(), 'resources', resource)
    if not os.path.exists(resource_path):
        raise FileNotFoundError(f"Resource not found: {resource}")
    return resource_path


# Import main package components
try:
    from .youtube_bot import gui, utils, core
    from . import browser
    from . import proxy
    from . import youtube
    from . import security
    from . import storage
except ImportError as e:
    logger.error(f"Error importing package components: {e}")
    raise

# Clean up namespace
del os
del sys
del logging
del RotatingFileHandler
del datetime