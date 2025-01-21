"""
Custom widgets module for YouTube Live Comment Bot GUI.

This module provides custom widgets used throughout the application's GUI.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import widgets
try:
    from .proxy_widget import ProxyWidget
    from .comment_widget import CommentWidget
    from .browser_widget import BrowserWidget
    from .schedule_widget import ScheduleWidget
    from .status_bar import StatusBar
except ImportError as e:
    logger.error(f"Error importing widgets: {e}")
    raise

# Constants for widget styling
BUTTON_HEIGHT = 30
WIDGET_MARGIN = 5
WIDGET_SPACING = 10
GROUP_BOX_MARGIN = 15


# Widget state management
class WidgetState:
    """Class for managing widget states."""

    def __init__(self):
        self._states: Dict[str, Any] = {}

    def set(self, widget_id: str, state: Any) -> None:
        """Set state for a widget."""
        self._states[widget_id] = state

    def get(self, widget_id: str, default: Any = None) -> Any:
        """Get state of a widget."""
        return self._states.get(widget_id, default)

    def clear(self, widget_id: str) -> None:
        """Clear state of a widget."""
        self._states.pop(widget_id, None)

    def clear_all(self) -> None:
        """Clear all widget states."""
        self._states.clear()


# Global widget state manager
widget_state = WidgetState()

# Default widget styles
DEFAULT_STYLE = """
QGroupBox {
    border: 1px solid gray;
    border-radius: 5px;
    margin-top: 0.5em;
    padding-top: 0.5em;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QPushButton {
    min-height: 25px;
    padding: 5px;
}

QLineEdit, QSpinBox, QComboBox {
    padding: 3px;
    min-height: 20px;
}

QTextEdit {
    padding: 5px;
}
"""

# Export widgets and utilities
__all__ = [
    'ProxyWidget',
    'CommentWidget',
    'BrowserWidget',
    'ScheduleWidget',
    'StatusBar',
    'WidgetState',
    'widget_state',
    'DEFAULT_STYLE',
    'BUTTON_HEIGHT',
    'WIDGET_MARGIN',
    'WIDGET_SPACING',
    'GROUP_BOX_MARGIN'
]


# Custom exceptions
class WidgetError(Exception):
    """Base exception for widget-related errors."""
    pass


class WidgetStateError(WidgetError):
    """Raised when there's an error with widget state management."""
    pass


class WidgetStyleError(WidgetError):
    """Raised when there's an error with widget styling."""
    pass


# Utility functions
def create_widget_id(base: str, suffix: str = None) -> str:
    """Create a unique widget identifier.

    Args:
        base: Base name for the widget.
        suffix: Optional suffix to add.

    Returns:
        str: Unique widget identifier.
    """
    if suffix:
        return f"{base}_{suffix}"
    return base


def apply_widget_style(widget: Any, style: str = None) -> None:
    """Apply style to a widget.

    Args:
        widget: Widget to style.
        style: Style string to apply.
    """
    try:
        widget.setStyleSheet(style or DEFAULT_STYLE)
    except Exception as e:
        logger.error(f"Failed to apply widget style: {e}")
        raise WidgetStyleError(f"Failed to apply style to widget: {e}")


# Clean up namespace
del logging