"""
Main window for YouTube Live Comment Bot.

This module contains the primary window interface and its components.
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QCloseEvent

from ..core import TaskManager, TaskStatus
from ..core.task_manager import TaskPriority
from ..core.config import Config
from .settings_tab import SettingsTab
from .browser_tab import BrowserTab
from .proxy_tab import ProxyTab
from .comments_tab import CommentsTab
from .logs_tab import LogsTab
from .widgets.status_bar import StatusBar
from . import (
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_SPACING,
    DEFAULT_MARGIN,
    TabID
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, task_manager: TaskManager):
        """Initialize main window.

        Args:
            task_manager: Application task manager instance.
        """
        super().__init__()

        self.task_manager = task_manager
        self.current_task_id: Optional[str] = None
        self._setup_ui()
        self._setup_connections()
        self._setup_status_timer()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Set window properties
        self.setWindowTitle("YouTube Live Comment Bot")
        self.setMinimumSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Add tabs
        self.settings_tab = SettingsTab(self.task_manager)
        self.browser_tab = BrowserTab(self.task_manager)
        self.proxy_tab = ProxyTab(self.task_manager)
        self.comments_tab = CommentsTab(self.task_manager)
        self.logs_tab = LogsTab(self.task_manager)

        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.browser_tab, "Browser")
        self.tab_widget.addTab(self.proxy_tab, "Proxy")
        self.tab_widget.addTab(self.comments_tab, "Comments")
        self.tab_widget.addTab(self.logs_tab, "Logs")

        layout.addWidget(self.tab_widget)

        # Create control panel
        control_layout = QHBoxLayout()

        # Status label
        self.status_label = QLabel("Ready")
        control_layout.addWidget(self.status_label)

        # Add stretch to push buttons to the right
        control_layout.addStretch()

        # Control buttons
        self.start_button = QPushButton("Start")
        self.start_button.setFixedWidth(100)
        self.start_button.clicked.connect(self._on_start_clicked)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)

        layout.addLayout(control_layout)

        # Create status bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect tab signals
        self.settings_tab.config_changed.connect(self._on_config_changed)
        self.browser_tab.browser_ready.connect(self._on_browser_ready)
        self.proxy_tab.proxy_changed.connect(self._on_proxy_changed)
        self.comments_tab.comments_updated.connect(self._on_comments_updated)

        # Connect task manager signals
        self.task_manager.callbacks.register('on_start', self._on_task_start)
        self.task_manager.callbacks.register('on_complete', self._on_task_complete)
        self.task_manager.callbacks.register('on_error', self._on_task_error)

    def _setup_status_timer(self) -> None:
        """Setup timer for status updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)  # Update every second

    def _update_status(self) -> None:
        """Update status display."""
        if self.current_task_id:
            status = self.task_manager.get_task_status(self.current_task_id)
            if status:
                self.status_label.setText(f"Status: {status.name}")
                self.status_bar.update_task_info(status)

    def _on_start_clicked(self) -> None:
        """Handle start button click."""
        try:
            # Get configuration from tabs
            config = self._collect_config()

            # Create new task with proper TaskPriority enum
            self.current_task_id = self.task_manager.create_task(
                priority=TaskPriority.NORMAL,  # Use enum instead of string
                max_duration=config.get('max_duration'),
                max_retries=config.get('max_retries', 3)
            )

            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Starting...")

            logger.info("Started new task with ID: %s", self.current_task_id)

        except Exception as e:
            self.logs_tab.log_error(f"Failed to start task: {e}")
            self.status_bar.show_error("Failed to start task")

        except Exception as e:
            self.logs_tab.log_error(f"Failed to start task: {e}")
            self.status_bar.show_error("Failed to start task")

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        try:
            if self.current_task_id:
                self.task_manager.cancel_task(self.current_task_id)
                self.current_task_id = None

            # Update UI
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("Stopped")

            logger.info("Task stopped by user")

        except Exception as e:
            self.logs_tab.log_error(f"Failed to stop task: {e}")
            self.status_bar.show_error("Failed to stop task")

    def _collect_config(self) -> Dict[str, Any]:
        """Collect configuration from all tabs.

        Returns:
            dict: Combined configuration from all tabs.
        """
        config = {}

        # Collect settings from each tab
        config.update(self.settings_tab.get_config())
        config.update(self.browser_tab.get_config())
        config.update(self.proxy_tab.get_config())
        config.update(self.comments_tab.get_config())

        return config

    def _on_config_changed(self, config: Dict[str, Any]) -> None:
        """Handle configuration changes.

        Args:
            config: Updated configuration.
        """
        try:
            # Update task manager configuration
            self.task_manager.config = Config(**config)
            logger.debug("Configuration updated")
        except Exception as e:
            self.logs_tab.log_error(f"Failed to update configuration: {e}")

    def _on_browser_ready(self, ready: bool) -> None:
        """Handle browser ready status change.

        Args:
            ready: Whether browser is ready.
        """
        self.start_button.setEnabled(ready)
        if not ready:
            self.status_bar.show_warning("Browser not ready")

    def _on_proxy_changed(self, proxy_config: Dict[str, Any]) -> None:
        """Handle proxy configuration changes.

        Args:
            proxy_config: Updated proxy configuration.
        """
        try:
            self.task_manager.config.proxy = proxy_config
            logger.debug("Proxy configuration updated")
        except Exception as e:
            self.logs_tab.log_error(f"Failed to update proxy configuration: {e}")

    def _on_comments_updated(self, comments: list) -> None:
        """Handle comments list updates.

        Args:
            comments: Updated comments list.
        """
        try:
            if self.current_task_id:
                # Update task with new comments
                self.task_manager.update_task_comments(
                    self.current_task_id,
                    comments
                )
            logger.debug("Comments updated")
        except Exception as e:
            self.logs_tab.log_error(f"Failed to update comments: {e}")

    def _on_task_start(self, task: Any) -> None:
        """Handle task start event.

        Args:
            task: Started task instance.
        """
        self.status_label.setText(f"Running task: {task.id}")
        self.status_bar.show_info("Task started")
        logger.info(f"Task {task.id} started")

    def _on_task_complete(self, task: Any) -> None:
        """Handle task completion event.

        Args:
            task: Completed task instance.
        """
        self.status_label.setText("Task completed")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.show_success("Task completed successfully")
        logger.info(f"Task {task.id} completed")

    def _on_task_error(self, task: Any) -> None:
        """Handle task error event.

        Args:
            task: Failed task instance.
        """
        self.status_label.setText("Task failed")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.show_error(f"Task failed: {task.result.error}")
        logger.error(f"Task {task.id} failed: {task.result.error}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.

        Args:
            event: Close event instance.
        """
        try:
            # Stop current task if running
            if self.current_task_id:
                self.task_manager.cancel_task(self.current_task_id)

            # Cleanup
            self.status_timer.stop()
            self.task_manager.shutdown()

            event.accept()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()  # Accept anyway to allow closing