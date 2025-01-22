"""
Logs tab for YouTube Live Comment Bot.

This module contains the logs display and management tab interface.
"""

import logging
import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTextEdit, QPushButton, QFileDialog,
    QComboBox, QCheckBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat

from ..core import TaskManager
from . import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class LogsTab(QWidget):
    """Logs display and management tab widget."""

    def __init__(self, task_manager: TaskManager):
        """Initialize logs tab."""
        super().__init__()
        self.task_manager = task_manager
        self.max_lines = 1000  # Maximum number of log lines to display
        self._setup_ui()
        self._setup_log_handler()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Log Controls Group
        controls_group = QGroupBox("Log Controls")
        controls_layout = QHBoxLayout()

        # Log level selection
        self.log_level = QComboBox()
        self.log_level.addItems([
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL"
        ])
        self.log_level.setCurrentText("INFO")
        controls_layout.addWidget(QLabel("Log Level:"))
        controls_layout.addWidget(self.log_level)

        # Auto-scroll checkbox
        self.auto_scroll = QCheckBox("Auto-scroll")
        self.auto_scroll.setChecked(True)
        controls_layout.addWidget(self.auto_scroll)

        # Word wrap checkbox
        self.word_wrap = QCheckBox("Word Wrap")
        self.word_wrap.setChecked(True)
        controls_layout.addWidget(self.word_wrap)

        # Clear button
        self.clear_button = QPushButton("Clear Logs")
        controls_layout.addWidget(self.clear_button)

        # Save button
        self.save_button = QPushButton("Save Logs")
        controls_layout.addWidget(self.save_button)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Filter Group
        filter_group = QGroupBox("Log Filters")
        filter_layout = QHBoxLayout()

        # Filter checkboxes
        self.show_debug = QCheckBox("Debug")
        self.show_info = QCheckBox("Info")
        self.show_warning = QCheckBox("Warning")
        self.show_error = QCheckBox("Error")
        self.show_critical = QCheckBox("Critical")

        # Set initial states
        self.show_debug.setChecked(False)
        self.show_info.setChecked(True)
        self.show_warning.setChecked(True)
        self.show_error.setChecked(True)
        self.show_critical.setChecked(True)

        filter_layout.addWidget(self.show_debug)
        filter_layout.addWidget(self.show_info)
        filter_layout.addWidget(self.show_warning)
        filter_layout.addWidget(self.show_error)
        filter_layout.addWidget(self.show_critical)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Log Display Group
        display_group = QGroupBox("Log Output")
        display_layout = QVBoxLayout()

        # Log text display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
            if self.word_wrap.isChecked()
            else QTextEdit.LineWrapMode.NoWrap
        )
        display_layout.addWidget(self.log_display)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Status bar
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.status_bar)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect control signals
        self.log_level.currentTextChanged.connect(self._update_log_level)
        self.word_wrap.stateChanged.connect(self._toggle_word_wrap)
        self.clear_button.clicked.connect(self._clear_logs)
        self.save_button.clicked.connect(self._save_logs)

        # Connect filter signals
        self.show_debug.stateChanged.connect(self._apply_filters)
        self.show_info.stateChanged.connect(self._apply_filters)
        self.show_warning.stateChanged.connect(self._apply_filters)
        self.show_error.stateChanged.connect(self._apply_filters)
        self.show_critical.stateChanged.connect(self._apply_filters)

        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_status_bar)
        self.update_timer.start(1000)  # Update every second

    def _setup_log_handler(self) -> None:
        """Setup custom log handler for the display."""

        class QTextEditHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
                self.log_formats = {
                    logging.DEBUG: ('gray', 'Debug'),
                    logging.INFO: ('black', 'Info'),
                    logging.WARNING: ('orange', 'Warning'),
                    logging.ERROR: ('red', 'Error'),
                    logging.CRITICAL: ('dark red', 'Critical')
                }

            def emit(self, record):
                color, level_name = self.log_formats.get(
                    record.levelno,
                    ('black', 'Unknown')
                )

                # Create timestamp
                timestamp = datetime.datetime.fromtimestamp(record.created)
                time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                # Format message
                msg = f"[{time_str}] [{level_name}] {record.getMessage()}"

                # Create text format with color
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(color))

                # Append text with format
                cursor = self.widget.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(msg + '\n', fmt)

                # Auto-scroll if enabled
                if self.widget.parent().auto_scroll.isChecked():
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.widget.setTextCursor(cursor)

                # Limit number of lines
                self._limit_lines()

            def _limit_lines(self):
                doc = self.widget.document()
                while doc.lineCount() > self.widget.parent().max_lines:
                    cursor = QTextCursor(doc.firstBlock())
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()  # Remove newline

        # Create and set handler
        self.log_handler = QTextEditHandler(self.log_display)
        self.log_handler.setLevel(logging.INFO)
        logger.addHandler(self.log_handler)

    def _update_log_level(self, level: str) -> None:
        """Update the log level.

        Args:
            level: New log level string.
        """
        numeric_level = getattr(logging, level.upper(), None)
        if numeric_level:
            self.log_handler.setLevel(numeric_level)
            logger.debug(f"Log level changed to {level}")

    def _toggle_word_wrap(self, state: int) -> None:
        """Toggle word wrap mode.

        Args:
            state: Checkbox state.
        """
        self.log_display.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
            if state
            else QTextEdit.LineWrapMode.NoWrap
        )

    def _clear_logs(self) -> None:
        """Clear the log display."""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear the logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log_display.clear()
            logger.debug("Logs cleared")

    def _save_logs(self) -> None:
        """Save logs to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Logs",
            "",
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(
                    self,
                    "Save Successful",
                    "Logs saved successfully."
                )
                logger.debug(f"Logs saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save logs: {str(e)}"
                )
                logger.error(f"Failed to save logs: {e}")

    def _apply_filters(self) -> None:
        """Apply log level filters."""
        # TODO: Implement log filtering
        pass

    def _update_status_bar(self) -> None:
        """Update the status bar with log statistics."""
        total_lines = self.log_display.document().lineCount()
        self.status_bar.setText(f"Total log entries: {total_lines}")

    def log_message(self, level: str, message: str) -> None:
        """Log a message at the specified level.

        Args:
            level: Log level string.
            message: Message to log.
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(numeric_level, message)

    def log_error(self, message: str) -> None:
        """Log an error message.

        Args:
            message: Error message to log.
        """
        self.log_message("ERROR", message)