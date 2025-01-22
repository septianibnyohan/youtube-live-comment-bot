"""
Utility functions for core module.
"""

import uuid
from typing import Optional
from datetime import datetime


def create_task_id() -> str:
    """Generate a unique task ID.

    Returns:
        str: Unique task identifier.
    """
    return str(uuid.uuid4())


def calculate_task_duration(start: float, end: float) -> float:
    """Calculate the duration of a task in seconds.

    Args:
        start: Start timestamp.
        end: End timestamp.

    Returns:
        float: Duration in seconds.
    """
    return end - start