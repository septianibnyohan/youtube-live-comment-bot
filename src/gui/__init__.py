"""
GUI module for YouTube Live Comment Bot.

This module contains all the graphical user interface components
including the main window, tabs, and custom widgets.
"""

from typing import Dict, List, Optional, Any
import os
import logging
from pathlib import Path

# Get the module logger
logger = logging.getLogger(__name__)

# GUI Constants
DEFAULT_WINDOW_WIDTH = 1024
DEFAULT_WINDOW_HEIGHT = 768
DEFAULT_SPACING = 10
DEFAULT_MARGIN = 20


# Tab identifiers
class TabID:
    SETTINGS = "settings"
    BROWSER = "browser"
    PROXY = "proxy"
    COMMENTS = "comments"
    LOGS = "logs"


# Style configurations
STYLE_DIR = Path(__file__).parent / "styles"
DEFAULT_STYLE = "default.qss"


def load_stylesheet(name: str = DEFAULT_STYLE) -> str:
    """Load a QSS stylesheet.

    Args:
        name: Name of the stylesheet file.

    Returns:
        str: Content of the stylesheet.

    Raises:
        FileNotFoundError: If stylesheet file doesn't exist.
    """
    try:
        style_path = STYLE_DIR / name
        if not style_path.exists():
            logger.warning(f"Stylesheet not found: {name}")
            return ""

        with open(style_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading stylesheet {name}: {e}")
        return ""


# Widget state management
class WidgetState:
    """Class for managing widget states."""

    def __init__(self):
        self._states: Dict[str, Any] = {}

    def set_state(self, widget_id: str, state: Any) -> None:
        """Set state for a widget.

        Args:
            widget_id: Unique identifier for the widget.
            state: State data to store.
        """
        self._states[widget_id] = state

    def get_state(self, widget_id: str, default: Any = None) -> Any:
        """Get state of a widget.

        Args:
            widget_id: Unique identifier for the widget.
            default: Default value if state doesn't exist.

        Returns:
            Stored state or default value.
        """
        return self._states.get(widget_id, default)

    def clear_state(self, widget_id: str) -> None:
        """Clear state of a widget.

        Args:
            widget_id: Unique identifier for the widget.
        """
        self._states.pop(widget_id, None)

    def clear_all(self) -> None:
        """Clear all widget states."""
        self._states.clear()


# Global widget state manager
widget_state = WidgetState()

# Import GUI components
try:
    from .main_window import MainWindow
    from .settings_tab import SettingsTab
    from .browser_tab import BrowserTab
    from .proxy_tab import ProxyTab
    from .comments_tab import CommentsTab
    from .logs_tab import LogsTab
    from .widgets import (
        ProxyWidget,
        CommentWidget,
        BrowserWidget,
        ScheduleWidget,
        StatusBar
    )
except ImportError as e:
    logger.error(f"Error importing GUI components: {e}")
    raise

__all__ = [
    'MainWindow',
    'SettingsTab',
    'BrowserTab',
    'ProxyTab',
    'CommentsTab',
    'LogsTab',
    'ProxyWidget',
    'CommentWidget',
    'BrowserWidget',
    'ScheduleWidget',
    'StatusBar',
    'TabID',
    'load_stylesheet',
    'widget_state',
    'DEFAULT_WINDOW_WIDTH',
    'DEFAULT_WINDOW_HEIGHT',
    'DEFAULT_SPACING',
    'DEFAULT_MARGIN'
]


# Custom exceptions
class GUIError(Exception):
    """Base exception for GUI-related errors."""
    pass


class StylesheetError(GUIError):
    """Raised when there's an error with stylesheets."""
    pass


class WidgetError(GUIError):
    """Raised when there's an error with widgets."""
    pass


# Utility functions
def get_resource_path(name: str) -> Path:
    """Get the path to a GUI resource.

    Args:
        name: Resource name or relative path.

    Returns:
        Path: Full path to the resource.

    Raises:
        FileNotFoundError: If resource doesn't exist.
    """
    resource_path = Path(__file__).parent / 'resources' / name
    if not resource_path.exists():
        raise FileNotFoundError(f"Resource not found: {name}")
    return resource_path


def create_widget_id(base: str, suffix: Optional[str] = None) -> str:
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


# Clean up namespace
del os
del logging
del Path