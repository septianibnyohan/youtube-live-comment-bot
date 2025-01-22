"""
Comment widget for YouTube Live Comment Bot.

This module contains a reusable comment management widget.
"""

import logging
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QSpinBox, QComboBox,
    QCheckBox, QMessageBox, QFileDialog, QTableWidget,
    QTableWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt
import random
import emoji

from .. import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class CommentWidget(QWidget):
    """Widget for comment management."""

    # Signal emitted when comments are updated
    comments_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        """Initialize comment widget."""
        super().__init__(parent)
        self.comments = []
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Comments Pool
        pool_layout = QVBoxLayout()
        pool_layout.addWidget(QLabel("Comments Pool:"))

        self.comments_input = QTextEdit()
        self.comments_input.setPlaceholderText(
            "Enter comments (one per line)\n"
            "Available variables:\n"
            "{username} - Channel name\n"
            "{time} - Current time\n"
            "{video_title} - Video title\n"
            "{random_emoji} - Random emoji"
        )
        pool_layout.addWidget(self.comments_input)

        # Comment controls
        controls_layout = QHBoxLayout()

        # Import/Export buttons
        self.import_button = QPushButton("Import")
        self.export_button = QPushButton("Export")
        self.clear_button = QPushButton("Clear")

        controls_layout.addWidget(self.import_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.clear_button)

        pool_layout.addLayout(controls_layout)
        layout.addLayout(pool_layout)

        # Comment Options
        options_layout = QVBoxLayout()

        # Delay settings
        delay_layout = QHBoxLayout()
        self.comment_delay = QSpinBox()
        self.comment_delay.setRange(1, 3600)
        self.comment_delay.setValue(5)
        self.comment_delay.setSuffix(" seconds")
        delay_layout.addWidget(QLabel("Comment Delay:"))
        delay_layout.addWidget(self.comment_delay)
        options_layout.addLayout(delay_layout)

        # Random delay range
        random_delay_layout = QHBoxLayout()
        self.random_delay_min = QSpinBox()
        self.random_delay_max = QSpinBox()
        self.random_delay_min.setRange(0, 60)
        self.random_delay_max.setRange(1, 120)
        self.random_delay_min.setValue(2)
        self.random_delay_max.setValue(10)
        self.random_delay_min.setSuffix(" sec")
        self.random_delay_max.setSuffix(" sec")
        random_delay_layout.addWidget(QLabel("Random Delay Range:"))
        random_delay_layout.addWidget(self.random_delay_min)
        random_delay_layout.addWidget(QLabel("to"))
        random_delay_layout.addWidget(self.random_delay_max)
        options_layout.addLayout(random_delay_layout)

        # Max comments
        max_comments_layout = QHBoxLayout()
        self.max_comments = QSpinBox()
        self.max_comments.setRange(1, 1000)
        self.max_comments.setValue(5)
        max_comments_layout.addWidget(QLabel("Max Comments per User:"))
        max_comments_layout.addWidget(self.max_comments)
        options_layout.addLayout(max_comments_layout)

        layout.addLayout(options_layout)

        # Comment Settings
        settings_layout = QVBoxLayout()

        # Comment options
        self.randomize_comments = QCheckBox("Randomize Comments")
        self.use_emojis = QCheckBox("Include Emojis")
        self.filter_duplicates = QCheckBox("Filter Duplicate Comments")

        settings_layout.addWidget(self.randomize_comments)
        settings_layout.addWidget(self.use_emojis)
        settings_layout.addWidget(self.filter_duplicates)

        # Language selection
        lang_layout = QHBoxLayout()
        self.comment_language = QComboBox()
        self.comment_language.addItems([
            "English",
            "Spanish",
            "Portuguese",
            "French",
            "German",
            "Italian",
            "Mixed"
        ])
        lang_layout.addWidget(QLabel("Comment Language:"))
        lang_layout.addWidget(self.comment_language)
        settings_layout.addLayout(lang_layout)

        layout.addLayout(settings_layout)

        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Comment Preview:"))

        self.preview_table = QTableWidget(0, 2)
        self.preview_table.setHorizontalHeaderLabels(["Original", "Processed"])
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.preview_table)

        layout.addLayout(preview_layout)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect settings changes
        self.comments_input.textChanged.connect(self._update_comments)
        self.comment_delay.valueChanged.connect(self._update_config)
        self.random_delay_min.valueChanged.connect(self._update_config)
        self.random_delay_max.valueChanged.connect(self._update_config)
        self.max_comments.valueChanged.connect(self._update_config)

        # Connect option changes
        self.randomize_comments.stateChanged.connect(self._update_preview)
        self.use_emojis.stateChanged.connect(self._update_preview)
        self.filter_duplicates.stateChanged.connect(self._update_preview)
        self.comment_language.currentTextChanged.connect(self._update_preview)

        # Connect buttons
        self.import_button.clicked.connect(self._import_comments)
        self.export_button.clicked.connect(self._export_comments)
        self.clear_button.clicked.connect(self._clear_comments)

    def _update_comments(self) -> None:
        """Update comments list and preview."""
        self.comments = self._get_comments_list()
        self._update_preview()
        self.comments_updated.emit(self.comments)

    def _update_config(self) -> None:
        """Update widget configuration."""
        if self.random_delay_min.value() >= self.random_delay_max.value():
            self.random_delay_max.setValue(self.random_delay_min.value() + 1)

    def _update_preview(self) -> None:
        """Update comment preview table."""
        self.preview_table.setRowCount(0)

        for comment in self.comments[:5]:  # Show first 5 comments
            processed = self._process_comment(comment)

            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)

            self.preview_table.setItem(row, 0, QTableWidgetItem(comment))
            self.preview_table.setItem(row, 1, QTableWidgetItem(processed))

    def _process_comment(self, comment: str) -> str:
        """Process comment with current settings.

        Args:
            comment: Original comment.

        Returns:
            str: Processed comment.
        """
        if not comment:
            return ""

        result = comment

        # Add emoji if enabled
        if self.use_emojis.isChecked():
            # Get random emoji
            emoji_list = list(emoji.EMOJI_DATA.keys())
            random_emoji = random.choice(emoji_list)
            result = f"{result} {random_emoji}"

        return result

    def _get_comments_list(self) -> List[str]:
        """Get list of comments from input.

        Returns:
            list: List of comments.
        """
        text = self.comments_input.toPlainText().strip()
        if not text:
            return []

        comments = [line.strip() for line in text.split('\n') if line.strip()]

        if self.filter_duplicates.isChecked():
            comments = list(dict.fromkeys(comments))

        return comments

    def _import_comments(self) -> None:
        """Import comments from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Comments",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    comments = f.read()
                self.comments_input.setPlainText(comments)
                self.status_label.setText("Comments imported successfully")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import comments: {str(e)}"
                )
                self.status_label.setText("Failed to import comments")

    def _export_comments(self) -> None:
        """Export comments to file."""
        if not self.comments:
            QMessageBox.warning(
                self,
                "No Comments",
                "There are no comments to export."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Comments",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.comments))
                self.status_label.setText("Comments exported successfully")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export comments: {str(e)}"
                )
                self.status_label.setText("Failed to export comments")

    def _clear_comments(self) -> None:
        """Clear all comments."""
        reply = QMessageBox.question(
            self,
            "Clear Comments",
            "Are you sure you want to clear all comments?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.comments_input.clear()
            self.preview_table.setRowCount(0)
            self.comments = []
            self.comments_updated.emit([])
            self.status_label.setText("Comments cleared")

    def set_comments(self, comments: List[str]) -> None:
        """Set comment list.

        Args:
            comments: List of comments to set.
        """
        self.comments_input.setPlainText('\n'.join(comments))

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            dict: Current configuration.
        """
        return {
            'comments': self.comments,
            'comment_delay': self.comment_delay.value(),
            'random_delay_min': self.random_delay_min.value(),
            'random_delay_max': self.random_delay_max.value(),
            'max_comments': self.max_comments.value(),
            'randomize_comments': self.randomize_comments.isChecked(),
            'use_emojis': self.use_emojis.isChecked(),
            'filter_duplicates': self.filter_duplicates.isChecked(),
            'comment_language': self.comment_language.currentText()
        }