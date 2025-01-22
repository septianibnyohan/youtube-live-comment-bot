"""
Schedule widget for YouTube Live Comment Bot.

This module contains a reusable schedule configuration widget.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QTimeEdit, QCalendarWidget,
    QCheckBox, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import pyqtSignal, QTime, Qt

from .. import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class ScheduleWidget(QWidget):
    """Widget for schedule configuration."""

    # Signal emitted when schedule configuration changes
    schedule_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize schedule widget."""
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Schedule Type Group
        type_group = QGroupBox("Schedule Type")
        type_layout = QVBoxLayout()

        self.schedule_type = QButtonGroup()
        self.run_now = QRadioButton("Run Now")
        self.run_scheduled = QRadioButton("Schedule Run")
        self.run_interval = QRadioButton("Run at Intervals")

        self.schedule_type.addButton(self.run_now)
        self.schedule_type.addButton(self.run_scheduled)
        self.schedule_type.addButton(self.run_interval)

        type_layout.addWidget(self.run_now)
        type_layout.addWidget(self.run_scheduled)
        type_layout.addWidget(self.run_interval)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Schedule Settings Group
        settings_group = QGroupBox("Schedule Settings")
        settings_layout = QVBoxLayout()

        # Start Time
        time_layout = QHBoxLayout()
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(QLabel("Start Time:"))
        time_layout.addWidget(self.start_time)
        settings_layout.addLayout(time_layout)

        # Calendar for date selection
        self.calendar = QCalendarWidget()
        settings_layout.addWidget(self.calendar)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Interval Settings Group
        interval_group = QGroupBox("Interval Settings")
        interval_layout = QVBoxLayout()

        # Interval duration
        duration_layout = QHBoxLayout()
        self.interval_value = QSpinBox()
        self.interval_unit = QComboBox()

        self.interval_value.setRange(1, 999)
        self.interval_unit.addItems(["Minutes", "Hours", "Days"])

        duration_layout.addWidget(QLabel("Repeat Every:"))
        duration_layout.addWidget(self.interval_value)
        duration_layout.addWidget(self.interval_unit)

        interval_layout.addLayout(duration_layout)

        # Days of week selection
        days_layout = QVBoxLayout()
        days_layout.addWidget(QLabel("Run on:"))

        self.day_checkboxes = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]

        for day in days:
            checkbox = QCheckBox(day)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)

        interval_layout.addLayout(days_layout)

        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)

        # End Schedule Group
        end_group = QGroupBox("End Schedule")
        end_layout = QVBoxLayout()

        # End time
        end_time_layout = QHBoxLayout()
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        end_time_layout.addWidget(QLabel("End Time:"))
        end_time_layout.addWidget(self.end_time)
        end_layout.addLayout(end_time_layout)

        # Maximum runs
        max_runs_layout = QHBoxLayout()
        self.max_runs = QSpinBox()
        self.max_runs.setRange(0, 999)
        self.max_runs.setSpecialValueText("Unlimited")
        max_runs_layout.addWidget(QLabel("Maximum Runs:"))
        max_runs_layout.addWidget(self.max_runs)
        end_layout.addLayout(max_runs_layout)

        end_group.setLayout(end_layout)
        layout.addWidget(end_group)

        # Enable/disable appropriate widgets based on initial selection
        self._update_widget_states()

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Schedule type changes
        self.schedule_type.buttonClicked.connect(self._update_widget_states)
        self.schedule_type.buttonClicked.connect(self._update_config)

        # Time changes
        self.start_time.timeChanged.connect(self._update_config)
        self.end_time.timeChanged.connect(self._update_config)

        # Calendar changes
        self.calendar.selectionChanged.connect(self._update_config)

        # Interval changes
        self.interval_value.valueChanged.connect(self._update_config)
        self.interval_unit.currentTextChanged.connect(self._update_config)

        # Day selection changes
        for checkbox in self.day_checkboxes.values():
            checkbox.stateChanged.connect(self._update_config)

        # Max runs changes
        self.max_runs.valueChanged.connect(self._update_config)

    def _update_widget_states(self) -> None:
        """Update widget enabled states based on schedule type."""
        # Get selected schedule type
        is_scheduled = self.run_scheduled.isChecked()
        is_interval = self.run_interval.isChecked()

        # Enable/disable schedule settings
        self.start_time.setEnabled(is_scheduled or is_interval)
        self.calendar.setEnabled(is_scheduled)

        # Enable/disable interval settings
        self.interval_value.setEnabled(is_interval)
        self.interval_unit.setEnabled(is_interval)
        for checkbox in self.day_checkboxes.values():
            checkbox.setEnabled(is_interval)

        # Enable/disable end settings
        self.end_time.setEnabled(is_scheduled or is_interval)
        self.max_runs.setEnabled(is_interval)

    def _update_config(self) -> None:
        """Update and emit schedule configuration."""
        config = {
            'type': self._get_schedule_type(),
            'start_time': self.start_time.time().toString("HH:mm"),
            'start_date': self.calendar.selectedDate().toPyDate(),
            'interval': {
                'value': self.interval_value.value(),
                'unit': self.interval_unit.currentText().lower(),
            },
            'days': self._get_selected_days(),
            'end_time': self.end_time.time().toString("HH:mm"),
            'max_runs': self.max_runs.value() if self.max_runs.value() > 0 else None
        }

        self.schedule_changed.emit(config)

    def _get_schedule_type(self) -> str:
        """Get the current schedule type.

        Returns:
            str: Current schedule type.
        """
        if self.run_now.isChecked():
            return "now"
        elif self.run_scheduled.isChecked():
            return "scheduled"
        else:
            return "interval"

    def _get_selected_days(self) -> List[str]:
        """Get list of selected days.

        Returns:
            list: Selected days.
        """
        return [day for day, checkbox in self.day_checkboxes.items()
                if checkbox.isChecked()]

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set schedule configuration.

        Args:
            config: Schedule configuration dictionary.
        """
        try:
            # Set schedule type
            schedule_type = config.get('type', 'now')
            if schedule_type == 'now':
                self.run_now.setChecked(True)
            elif schedule_type == 'scheduled':
                self.run_scheduled.setChecked(True)
            else:
                self.run_interval.setChecked(True)

            # Set times
            if 'start_time' in config:
                self.start_time.setTime(QTime.fromString(config['start_time'], "HH:mm"))
            if 'end_time' in config:
                self.end_time.setTime(QTime.fromString(config['end_time'], "HH:mm"))

            # Set interval settings
            if 'interval' in config:
                interval = config['interval']
                self.interval_value.setValue(interval.get('value', 1))
                self.interval_unit.setCurrentText(interval.get('unit', 'hours').capitalize())

            # Set selected days
            for day in self.day_checkboxes:
                self.day_checkboxes[day].setChecked(day in config.get('days', []))

            # Set max runs
            self.max_runs.setValue(config.get('max_runs', 0))

            # Update widget states
            self._update_widget_states()

        except Exception as e:
            logger.error(f"Failed to set schedule configuration: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Get current schedule configuration.

        Returns:
            dict: Current schedule configuration.
        """
        return {
            'type': self._get_schedule_type(),
            'start_time': self.start_time.time().toString("HH:mm"),
            'start_date': self.calendar.selectedDate().toPyDate(),
            'interval': {
                'value': self.interval_value.value(),
                'unit': self.interval_unit.currentText().lower(),
            },
            'days': self._get_selected_days(),
            'end_time': self.end_time.time().toString("HH:mm"),
            'max_runs': self.max_runs.value() if self.max_runs.value() > 0 else None
        }

    def clear(self) -> None:
        """Clear schedule configuration."""
        self.run_now.setChecked(True)
        self.start_time.setTime(QTime.currentTime())
        self.end_time.setTime(QTime.currentTime())
        self.interval_value.setValue(1)
        self.interval_unit.setCurrentText("Hours")
        for checkbox in self.day_checkboxes.values():
            checkbox.setChecked(False)
        self.max_runs.setValue(0)