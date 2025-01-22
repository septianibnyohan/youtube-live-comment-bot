"""
Settings tab for YouTube Live Comment Bot.

This module contains the settings tab interface and configuration controls.
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QSpinBox, QComboBox,
    QCheckBox, QPushButton, QTimeEdit, QCalendarWidget,
    QStackedWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QIntValidator

from ..core import TaskManager
from ..core.config import Config
from ..utils.helpers import parse_time_string
from . import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class SettingsTab(QWidget):
    """Settings tab widget."""

    # Signal emitted when configuration changes
    config_changed = pyqtSignal(dict)

    def __init__(self, task_manager: TaskManager):
        """Initialize settings tab.

        Args:
            task_manager: Application task manager instance.
        """
        super().__init__()
        self.task_manager = task_manager
        self._setup_ui()
        self._load_config()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Add settings groups
        content_layout.addWidget(self._create_start_group())
        content_layout.addWidget(self._create_mode_group())
        content_layout.addWidget(self._create_behavior_group())
        content_layout.addWidget(self._create_limits_group())

        # Add stretch to bottom
        content_layout.addStretch()

        # Set scroll widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _create_start_group(self) -> QGroupBox:
        """Create start options group.

        Returns:
            QGroupBox: Start options group widget.
        """
        group = QGroupBox("Start Options")
        layout = QVBoxLayout(group)

        # Start type selection
        start_layout = QHBoxLayout()
        self.start_type = QComboBox()
        self.start_type.addItems(["Run Now", "Schedule"])
        start_layout.addWidget(QLabel("Start Type:"))
        start_layout.addWidget(self.start_type)
        layout.addLayout(start_layout)

        # Schedule options (stacked widget)
        self.schedule_stack = QStackedWidget()

        # Empty widget for "Run Now"
        self.schedule_stack.addWidget(QWidget())

        # Schedule widget
        schedule_widget = QWidget()
        schedule_layout = QVBoxLayout(schedule_widget)

        # Time selection
        time_layout = QHBoxLayout()
        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(QLabel("Time:"))
        time_layout.addWidget(self.schedule_time)
        schedule_layout.addLayout(time_layout)

        # Calendar
        self.schedule_calendar = QCalendarWidget()
        schedule_layout.addWidget(self.schedule_calendar)

        self.schedule_stack.addWidget(schedule_widget)
        layout.addWidget(self.schedule_stack)

        return group

    def _create_mode_group(self) -> QGroupBox:
        """Create mode options group.

        Returns:
            QGroupBox: Mode options group widget.
        """
        group = QGroupBox("Mode Settings")
        layout = QVBoxLayout(group)

        # Traffic mode
        mode_layout = QHBoxLayout()
        self.traffic_mode = QComboBox()
        self.traffic_mode.addItems([
            "Browse",
            "Keywords",
            "YouTube Music",
            "Channel Playlist",
            "External"
        ])
        mode_layout.addWidget(QLabel("Traffic Mode:"))
        mode_layout.addWidget(self.traffic_mode)
        layout.addLayout(mode_layout)

        # Keywords input
        keywords_layout = QHBoxLayout()
        self.keywords_input = QLineEdit()
        keywords_layout.addWidget(QLabel("Keywords:"))
        keywords_layout.addWidget(self.keywords_input)
        layout.addLayout(keywords_layout)

        return group

    def _create_behavior_group(self) -> QGroupBox:
        """Create behavior options group.

        Returns:
            QGroupBox: Behavior options group widget.
        """
        group = QGroupBox("Behavior Settings")
        layout = QVBoxLayout(group)

        # Watch duration
        duration_layout = QHBoxLayout()
        self.min_duration = QSpinBox()
        self.min_duration.setRange(0, 3600)
        self.min_duration.setSuffix(" seconds")
        self.max_duration = QSpinBox()
        self.max_duration.setRange(0, 3600)
        self.max_duration.setSuffix(" seconds")

        duration_layout.addWidget(QLabel("Watch Duration:"))
        duration_layout.addWidget(self.min_duration)
        duration_layout.addWidget(QLabel("to"))
        duration_layout.addWidget(self.max_duration)
        layout.addLayout(duration_layout)

        # Behavior checkboxes
        self.clear_history = QCheckBox("Clear Browser History")
        self.autoplay = QCheckBox("Enable Autoplay")
        self.random_watch = QCheckBox("Watch Random Videos")
        self.skip_ads = QCheckBox("Skip Ads")

        layout.addWidget(self.clear_history)
        layout.addWidget(self.autoplay)
        layout.addWidget(self.random_watch)
        layout.addWidget(self.skip_ads)

        # Skip ads delay
        skip_layout = QHBoxLayout()
        self.skip_delay = QSpinBox()
        self.skip_delay.setRange(0, 30)
        self.skip_delay.setSuffix(" seconds")
        skip_layout.addWidget(QLabel("Skip Ads After:"))
        skip_layout.addWidget(self.skip_delay)
        layout.addLayout(skip_layout)

        return group

    def _create_limits_group(self) -> QGroupBox:
        """Create limits options group.

        Returns:
            QGroupBox: Limits options group widget.
        """
        group = QGroupBox("Limits & Restrictions")
        layout = QVBoxLayout(group)

        # View count
        views_layout = QHBoxLayout()
        self.view_count = QSpinBox()
        self.view_count.setRange(1, 1000)
        views_layout.addWidget(QLabel("View Count:"))
        views_layout.addWidget(self.view_count)
        layout.addLayout(views_layout)

        # Thread count
        thread_layout = QHBoxLayout()
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 10)
        thread_layout.addWidget(QLabel("Thread Count:"))
        thread_layout.addWidget(self.thread_count)
        layout.addLayout(thread_layout)

        # Browser interval
        interval_layout = QHBoxLayout()
        self.browser_interval = QSpinBox()
        self.browser_interval.setRange(0, 3600)
        self.browser_interval.setSuffix(" seconds")
        interval_layout.addWidget(QLabel("Browser Interval:"))
        interval_layout.addWidget(self.browser_interval)
        layout.addLayout(interval_layout)

        return group

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect start type changes
        self.start_type.currentIndexChanged.connect(
            self.schedule_stack.setCurrentIndex
        )

        # Connect value changes to config update
        self.start_type.currentIndexChanged.connect(self._update_config)
        self.schedule_time.timeChanged.connect(self._update_config)
        self.schedule_calendar.selectionChanged.connect(self._update_config)
        self.traffic_mode.currentIndexChanged.connect(self._update_config)
        self.keywords_input.textChanged.connect(self._update_config)
        self.min_duration.valueChanged.connect(self._update_config)
        self.max_duration.valueChanged.connect(self._update_config)
        self.clear_history.stateChanged.connect(self._update_config)
        self.autoplay.stateChanged.connect(self._update_config)
        self.random_watch.stateChanged.connect(self._update_config)
        self.skip_ads.stateChanged.connect(self._update_config)
        self.skip_delay.valueChanged.connect(self._update_config)
        self.view_count.valueChanged.connect(self._update_config)
        self.thread_count.valueChanged.connect(self._update_config)
        self.browser_interval.valueChanged.connect(self._update_config)

    def _load_config(self) -> None:
        """Load configuration into UI elements."""
        config = self.task_manager.config

        # Load start options
        self.start_type.setCurrentText("Schedule" if config.schedule.enabled else "Run Now")
        if config.schedule.enabled and config.schedule.start_time:
            time = QTime.fromString(config.schedule.start_time, "HH:mm")
            self.schedule_time.setTime(time)

        # Load mode settings
        self.traffic_mode.setCurrentText(config.automation.mode_traffic)
        self.keywords_input.setText(", ".join(config.automation.keywords))

        # Load behavior settings
        self.min_duration.setValue(config.automation.watch_duration_min)
        self.max_duration.setValue(config.automation.watch_duration_max)
        self.clear_history.setChecked(config.browser.clear_history)
        self.autoplay.setChecked(config.automation.auto_play)
        self.random_watch.setChecked(config.automation.watch_random)
        self.skip_ads.setChecked(config.automation.skip_ads)
        self.skip_delay.setValue(config.automation.skip_ads_after)

        # Load limits
        self.view_count.setValue(config.automation.view_count)
        self.thread_count.setValue(config.automation.thread_count)
        self.browser_interval.setValue(config.automation.browser_interval)

    def _update_config(self) -> None:
        """Update configuration from UI elements."""
        config = {
            'schedule': {
                'enabled': self.start_type.currentText() == "Schedule",
                'start_time': self.schedule_time.time().toString("HH:mm"),
                'date': self.schedule_calendar.selectedDate().toPyDate()
            },
            'automation': {
                'mode_traffic': self.traffic_mode.currentText(),
                'keywords': [k.strip() for k in self.keywords_input.text().split(',') if k.strip()],
                'watch_duration_min': self.min_duration.value(),
                'watch_duration_max': self.max_duration.value(),
                'auto_play': self.autoplay.isChecked(),
                'watch_random': self.random_watch.isChecked(),
                'skip_ads': self.skip_ads.isChecked(),
                'skip_ads_after': self.skip_delay.value(),
                'view_count': self.view_count.value(),
                'thread_count': self.thread_count.value(),
                'browser_interval': self.browser_interval.value()
            },
            'browser': {
                'clear_history': self.clear_history.isChecked()
            }
        }

        # Emit configuration change signal
        self.config_changed.emit(config)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            dict: Current configuration.
        """
        return {
            'schedule': {
                'enabled': self.start_type.currentText() == "Schedule",
                'start_time': self.schedule_time.time().toString("HH:mm"),
                'date': self.schedule_calendar.selectedDate().toPyDate()
            },
            'automation': {
                'mode_traffic': self.traffic_mode.currentText(),
                'keywords': [k.strip() for k in self.keywords_input.text().split(',') if k.strip()],
                'watch_duration_min': self.min_duration.value(),
                'watch_duration_max': self.max_duration.value(),
                'auto_play': self.autoplay.isChecked(),
                'watch_random': self.random_watch.isChecked(),
                'skip_ads': self.skip_ads.isChecked(),
                'skip_ads_after': self.skip_delay.value(),
                'view_count': self.view_count.value(),
                'thread_count': self.thread_count.value(),
                'browser_interval': self.browser_interval.value()
            },
            'browser': {
                'clear_history': self.clear_history.isChecked()
            }
        }