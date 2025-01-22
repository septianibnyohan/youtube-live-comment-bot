"""
Comments tab for YouTube Live Comment Bot.

This module contains the comments management tab interface.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QSpinBox, QTextEdit,
    QPushButton, QFileDialog, QMessageBox,
    QScrollArea, QTableWidget, QTableWidgetItem,
    QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core import TaskManager
from . import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class CommentsTab(QWidget):
    """Comments management tab widget."""

    # Signal emitted when comments are updated
    comments_updated = pyqtSignal(list)

    def __init__(self, task_manager: TaskManager):
        """Initialize comments tab."""
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

        # Comments Settings Group
        settings_group = QGroupBox("Comment Settings")
        settings_layout = QVBoxLayout()

        # Comment delay
        delay_layout = QHBoxLayout()
        self.comment_delay = QSpinBox()
        self.comment_delay.setRange(1, 3600)
        self.comment_delay.setValue(5)
        self.comment_delay.setSuffix(" seconds")
        delay_layout.addWidget(QLabel("Comment Delay:"))
        delay_layout.addWidget(self.comment_delay)
        settings_layout.addLayout(delay_layout)

        # Max comments per user
        max_comments_layout = QHBoxLayout()
        self.max_comments = QSpinBox()
        self.max_comments.setRange(1, 100)
        self.max_comments.setValue(5)
        max_comments_layout.addWidget(QLabel("Max Comments per User:"))
        max_comments_layout.addWidget(self.max_comments)
        settings_layout.addLayout(max_comments_layout)

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
        settings_layout.addLayout(random_delay_layout)

        settings_group.setLayout(settings_layout)
        content_layout.addWidget(settings_group)

        # Comments Pool Group
        pool_group = QGroupBox("Comments Pool")
        pool_layout = QVBoxLayout()

        # Comments input
        self.comments_input = QTextEdit()
        self.comments_input.setPlaceholderText("Enter comments (one per line)")
        pool_layout.addWidget(self.comments_input)

        # Import/Export buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import from File")
        self.export_button = QPushButton("Export to File")
        self.clear_button = QPushButton("Clear All")

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.clear_button)
        pool_layout.addLayout(button_layout)

        # Variable placeholders info
        placeholders_layout = QVBoxLayout()
        placeholders_label = QLabel(
            "Available variables:\n"
            "{username} - Channel name\n"
            "{time} - Current time\n"
            "{video_title} - Video title\n"
            "{random_emoji} - Random emoji"
        )
        placeholders_layout.addWidget(placeholders_label)
        pool_layout.addLayout(placeholders_layout)

        pool_group.setLayout(pool_layout)
        content_layout.addWidget(pool_group)

        # Comment Options Group
        options_group = QGroupBox("Comment Options")
        options_layout = QVBoxLayout()

        self.randomize_comments = QCheckBox("Randomize Comments")
        self.use_emojis = QCheckBox("Include Emojis")
        self.filter_duplicates = QCheckBox("Filter Duplicate Comments")

        options_layout.addWidget(self.randomize_comments)
        options_layout.addWidget(self.use_emojis)
        options_layout.addWidget(self.filter_duplicates)

        # Comment language
        language_layout = QHBoxLayout()
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
        language_layout.addWidget(QLabel("Comment Language:"))
        language_layout.addWidget(self.comment_language)
        options_layout.addLayout(language_layout)

        options_group.setLayout(options_layout)
        content_layout.addWidget(options_group)

        # Spinner and Like Options Group
        actions_group = QGroupBox("Additional Actions")
        actions_layout = QVBoxLayout()

        self.auto_like = QCheckBox("Auto Like Videos")
        self.auto_subscribe = QCheckBox("Auto Subscribe")

        actions_layout.addWidget(self.auto_like)
        actions_layout.addWidget(self.auto_subscribe)

        actions_group.setLayout(actions_layout)
        content_layout.addWidget(actions_group)

        # Add stretch to bottom
        content_layout.addStretch()

        # Set scroll widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect settings changes
        self.comment_delay.valueChanged.connect(self._update_config)
        self.max_comments.valueChanged.connect(self._update_config)
        self.random_delay_min.valueChanged.connect(self._update_config)
        self.random_delay_max.valueChanged.connect(self._update_config)

        # Connect comments pool changes
        self.comments_input.textChanged.connect(self._update_config)

        # Connect option changes
        self.randomize_comments.stateChanged.connect(self._update_config)
        self.use_emojis.stateChanged.connect(self._update_config)
        self.filter_duplicates.stateChanged.connect(self._update_config)
        self.comment_language.currentTextChanged.connect(self._update_config)

        # Connect action changes
        self.auto_like.stateChanged.connect(self._update_config)
        self.auto_subscribe.stateChanged.connect(self._update_config)

        # Connect buttons
        self.import_button.clicked.connect(self._import_comments)
        self.export_button.clicked.connect(self._export_comments)
        self.clear_button.clicked.connect(self._clear_comments)

    def _load_config(self) -> None:
        """Load configuration into UI elements."""
        config = self.task_manager.config

        # Load comment settings
        self.comment_delay.setValue(config.automation.comment_delay)
        self.max_comments.setValue(config.automation.max_comments_per_user)
        self.random_delay_min.setValue(config.automation.random_delay_min)
        self.random_delay_max.setValue(config.automation.random_delay_max)

        # Load comments
        if config.automation.comments:
            self.comments_input.setPlainText("\n".join(config.automation.comments))

        # Load options
        self.randomize_comments.setChecked(config.automation.randomize_comments)
        self.use_emojis.setChecked(config.automation.use_emojis)
        self.filter_duplicates.setChecked(config.automation.filter_duplicates)
        self.comment_language.setCurrentText(config.automation.comment_language)

        # Load actions
        self.auto_like.setChecked(config.automation.auto_like)
        self.auto_subscribe.setChecked(config.automation.auto_subscribe)

    def _update_config(self) -> None:
        """Update configuration from UI elements."""
        config = {
            'automation': {
                'comment_delay': self.comment_delay.value(),
                'max_comments_per_user': self.max_comments.value(),
                'random_delay_min': self.random_delay_min.value(),
                'random_delay_max': self.random_delay_max.value(),
                'comments': self._get_comments_list(),
                'randomize_comments': self.randomize_comments.isChecked(),
                'use_emojis': self.use_emojis.isChecked(),
                'filter_duplicates': self.filter_duplicates.isChecked(),
                'comment_language': self.comment_language.currentText(),
                'auto_like': self.auto_like.isChecked(),
                'auto_subscribe': self.auto_subscribe.isChecked()
            }
        }

        self.comments_updated.emit(self._get_comments_list())

    def _get_comments_list(self) -> List[str]:
        """Get list of comments from input.

        Returns:
            list: List of comments.
        """
        text = self.comments_input.toPlainText().strip()
        if not text:
            return []

        return [line.strip() for line in text.split('\n') if line.strip()]

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
                QMessageBox.information(
                    self,
                    "Import Successful",
                    "Comments imported successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import comments: {str(e)}"
                )

    def _export_comments(self) -> None:
        """Export comments to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Comments",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.comments_input.toPlainText())
                QMessageBox.information(
                    self,
                    "Export Successful",
                    "Comments exported successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export comments: {str(e)}"
                )

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

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            dict: Current configuration.
        """
        return {
            'automation': {
                'comment_delay': self.comment_delay.value(),
                'max_comments_per_user': self.max_comments.value(),
                'random_delay_min': self.random_delay_min.value(),
                'random_delay_max': self.random_delay_max.value(),
                'comments': self._get_comments_list(),
                'randomize_comments': self.randomize_comments.isChecked(),
                'use_emojis': self.use_emojis.isChecked(),
                'filter_duplicates': self.filter_duplicates.isChecked(),
                'comment_language': self.comment_language.currentText(),
                'auto_like': self.auto_like.isChecked(),
                'auto_subscribe': self.auto_subscribe.isChecked()
            }
        }