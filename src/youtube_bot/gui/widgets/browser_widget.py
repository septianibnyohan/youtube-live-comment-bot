"""
Browser widget for YouTube Live Comment Bot.

This module contains a reusable browser configuration widget.
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QSpinBox
)
from PyQt6.QtCore import pyqtSignal

from ... utils.helpers import get_chrome_executable
from .. import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class BrowserWidget(QWidget):
    """Widget for browser configuration."""

    # Signal emitted when browser configuration changes
    browser_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize browser widget."""
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Browser Type
        type_layout = QHBoxLayout()
        self.browser_type = QComboBox()
        self.browser_type.addItems(["Chrome", "Firefox", "Edge"])
        type_layout.addWidget(QLabel("Browser Type:"))
        type_layout.addWidget(self.browser_type)
        layout.addLayout(type_layout)

        # Browser Path
        path_layout = QHBoxLayout()
        self.browser_path = QLineEdit()
        self.browser_path.setPlaceholderText("Browser executable path")
        self.browse_button = QPushButton("Browse")
        path_layout.addWidget(QLabel("Browser Path:"))
        path_layout.addWidget(self.browser_path)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)

        # Browser Options
        self.show_browser = QCheckBox("Show Browser Window")
        self.clear_cookies = QCheckBox("Clear Cookies After Session")
        self.clear_history = QCheckBox("Clear History After Session")

        layout.addWidget(self.show_browser)
        layout.addWidget(self.clear_cookies)
        layout.addWidget(self.clear_history)

        # Page Load Timeout
        timeout_layout = QHBoxLayout()
        self.page_timeout = QSpinBox()
        self.page_timeout.setRange(10, 300)
        self.page_timeout.setValue(30)
        self.page_timeout.setSuffix(" seconds")
        timeout_layout.addWidget(QLabel("Page Load Timeout:"))
        timeout_layout.addWidget(self.page_timeout)
        layout.addLayout(timeout_layout)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        self.browser_type.currentTextChanged.connect(self._update_config)
        self.browser_path.textChanged.connect(self._update_config)
        self.show_browser.stateChanged.connect(self._update_config)
        self.clear_cookies.stateChanged.connect(self._update_config)
        self.clear_history.stateChanged.connect(self._update_config)
        self.page_timeout.valueChanged.connect(self._update_config)
        self.browse_button.clicked.connect(self._browse_browser_path)

    def _update_config(self) -> None:
        """Update and emit browser configuration."""
        config = {
            'type': self.browser_type.currentText().lower(),
            'executable_path': self.browser_path.text() or None,
            'headless': not self.show_browser.isChecked(),
            'clear_cookies': self.clear_cookies.isChecked(),
            'clear_history': self.clear_history.isChecked(),
            'page_load_timeout': self.page_timeout.value()
        }

        # Validate configuration
        if self._validate_config(config):
            self.browser_changed.emit(config)

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate browser configuration.

        Args:
            config: Browser configuration to validate.

        Returns:
            bool: True if configuration is valid.
        """
        browser_path = config['executable_path'] or get_chrome_executable()
        if not browser_path:
            self.status_label.setText("Browser executable not found")
            return False

        self.status_label.setText("Valid configuration")
        return True

    def _browse_browser_path(self) -> None:
        """Open file dialog to select browser executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Browser Executable",
            "",
            "Executable files (*)"
        )

        if file_path:
            self.browser_path.setText(file_path)

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set browser configuration.

        Args:
            config: Browser configuration dictionary.
        """
        try:
            self.browser_type.setCurrentText(config.get('type', 'chrome').capitalize())
            self.browser_path.setText(config.get('executable_path', ''))
            self.show_browser.setChecked(not config.get('headless', False))
            self.clear_cookies.setChecked(config.get('clear_cookies', True))
            self.clear_history.setChecked(config.get('clear_history', True))
            self.page_timeout.setValue(config.get('page_load_timeout', 30))

        except Exception as e:
            logger.error(f"Failed to set browser configuration: {e}")
            self.status_label.setText("Failed to load configuration")

    def get_config(self) -> Dict[str, Any]:
        """Get current browser configuration.

        Returns:
            dict: Current browser configuration.
        """
        return {
            'type': self.browser_type.currentText().lower(),
            'executable_path': self.browser_path.text() or None,
            'headless': not self.show_browser.isChecked(),
            'clear_cookies': self.clear_cookies.isChecked(),
            'clear_history': self.clear_history.isChecked(),
            'page_load_timeout': self.page_timeout.value()
        }