"""
YouTube Live Comment Bot

A powerful and customizable YouTube automation tool built with Python and PyQt6
for managing YouTube live chat interactions.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Package metadata
__version__ = '1.0.0'
__author__ = 'Your Name'
__author_email__ = 'your.email@example.com'
__license__ = 'MIT'
__copyright__ = f'Copyright 2024 {__author__}'


# Set up package-level logger
def get_logger():
    """Return the package logger."""
    return logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging with custom level.

    Args:
        level: The logging level to set. Defaults to logging.INFO.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    # Configure rotating file handler
    log_file = logs_dir / 'youtube_bot.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# Initialize logger
logger = get_logger()
setup_logging()

# Import main package components
from . import core
from . import gui
from . import utils

__all__ = [
    'get_logger',
    'setup_logging',
    '__version__',
    'core',
    'gui',
    'utils'
]