"""
Browser tab for YouTube Live Comment Bot.

This module contains the browser configuration tab interface.
"""

import logging
from typing import Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QFileDialog, QSpinBox, QScrollArea,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core import TaskManager
from ..utils.helpers import get_chrome_executable
from . import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)

class BrowserTab(QWidget):
    """Browser configuration tab widget."""

    # Signals
    browser_ready = pyqtSignal(bool)
    config_changed = pyqtSignal(dict)

    def __init__(self, task_manager: TaskManager):
        """Initialize browser tab."""
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

        # Browser Type Group
        browser_group = QGroupBox("Browser Type")
        browser_layout = QVBoxLayout()
        self.browser_type = QComboBox()
        self.browser_type.addItems(["Chrome", "Firefox", "Edge"])
        browser_layout.addWidget(self.browser_type)
        browser_group.setLayout(browser_layout)
        content_layout.addWidget(browser_group)

        # User Agent Group
        useragent_group = QGroupBox("User Agent")
        useragent_layout = QVBoxLayout()
        self.useragent_options = QButtonGroup()

        self.ua_desktop = QRadioButton("Desktop")
        self.ua_mobile = QRadioButton("Mobile")
        self.ua_random = QRadioButton("Random")

        self.useragent_options.addButton(self.ua_desktop)
        self.useragent_options.addButton(self.ua_mobile)
        self.useragent_options.addButton(self.ua_random)

        useragent_layout.addWidget(self.ua_desktop)
        useragent_layout.addWidget(self.ua_mobile)
        useragent_layout.addWidget(self.ua_random)
        useragent_group.setLayout(useragent_layout)
        content_layout.addWidget(useragent_group)

        # Fingerprint Group
        fingerprint_group = QGroupBox("Fingerprint")
        fingerprint_layout = QVBoxLayout()
        self.use_fingerprint = QCheckBox("Use Premium Fingerprint")
        fingerprint_layout.addWidget(self.use_fingerprint)
        fingerprint_group.setLayout(fingerprint_layout)
        content_layout.addWidget(fingerprint_group)

        # Connection Group
        connection_group = QGroupBox("Connection")
        connection_layout = QVBoxLayout()
        self.connection_type = QComboBox()
        self.connection_type.addItems(["Direct", "Proxy", "VPN"])
        connection_layout.addWidget(self.connection_type)
        connection_group.setLayout(connection_layout)
        content_layout.addWidget(connection_group)

        # Device Group
        device_group = QGroupBox("Device")
        device_layout = QVBoxLayout()
        self.device_type = QComboBox()
        self.device_type.addItems(["Desktop", "Mobile", "Random"])
        device_layout.addWidget(self.device_type)
        device_group.setLayout(device_layout)
        content_layout.addWidget(device_group)

        # Cookies Group
        cookies_group = QGroupBox("Cookies")
        cookies_layout = QVBoxLayout()
        self.use_cookies = QCheckBox("Use Cookies")
        self.clear_cookies = QCheckBox("Clear After Session")
        cookies_layout.addWidget(self.use_cookies)
        cookies_layout.addWidget(self.clear_cookies)
        cookies_group.setLayout(cookies_layout)
        content_layout.addWidget(cookies_group)

        # Browser Options Group
        options_group = QGroupBox("Browser Options")
        options_layout = QVBoxLayout()
        self.clear_history = QCheckBox("Clear History")
        self.block_images = QCheckBox("Block Images")
        self.block_js = QCheckBox("Block JavaScript")
        options_layout.addWidget(self.clear_history)
        options_layout.addWidget(self.block_images)
        options_layout.addWidget(self.block_js)
        options_group.setLayout(options_layout)
        content_layout.addWidget(options_group)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect all widgets to update config
        self.browser_type.currentTextChanged.connect(self._update_config)
        self.useragent_options.buttonClicked.connect(self._update_config)
        self.use_fingerprint.stateChanged.connect(self._update_config)
        self.connection_type.currentTextChanged.connect(self._update_config)
        self.device_type.currentTextChanged.connect(self._update_config)
        self.use_cookies.stateChanged.connect(self._update_config)
        self.clear_cookies.stateChanged.connect(self._update_config)
        self.clear_history.stateChanged.connect(self._update_config)
        self.block_images.stateChanged.connect(self._update_config)
        self.block_js.stateChanged.connect(self._update_config)

    def _load_config(self) -> None:
        """Load configuration into UI elements."""
        config = self.task_manager.config.browser

        # Load values into UI elements
        self.browser_type.setCurrentText(config.type.capitalize())

        # Set user agent option
        if config.user_agent == "desktop":
            self.ua_desktop.setChecked(True)
        elif config.user_agent == "mobile":
            self.ua_mobile.setChecked(True)
        else:
            self.ua_random.setChecked(True)

        self.use_fingerprint.setChecked(config.use_fingerprint)
        self.connection_type.setCurrentText(config.connection_type.capitalize())
        self.device_type.setCurrentText(config.device_type.capitalize())
        self.use_cookies.setChecked(config.use_cookies)
        self.clear_cookies.setChecked(config.clear_cookies)
        self.clear_history.setChecked(config.clear_history)
        self.block_images.setChecked(config.block_images)
        self.block_js.setChecked(config.block_javascript)

    def _update_config(self) -> None:
        """Update configuration from UI elements."""
        config = {
            'browser': {
                'type': self.browser_type.currentText().lower(),
                'user_agent': self._get_user_agent_setting(),
                'use_fingerprint': self.use_fingerprint.isChecked(),
                'connection_type': self.connection_type.currentText().lower(),
                'device_type': self.device_type.currentText().lower(),
                'use_cookies': self.use_cookies.isChecked(),
                'clear_cookies': self.clear_cookies.isChecked(),
                'clear_history': self.clear_history.isChecked(),
                'block_images': self.block_images.isChecked(),
                'block_javascript': self.block_js.isChecked()
            }
        }

        # Validate and emit configuration
        self.config_changed.emit(config)
        self.browser_ready.emit(self._validate_config(config))

    def _get_user_agent_setting(self) -> str:
        """Get the selected user agent setting."""
        if self.ua_desktop.isChecked():
            return "desktop"
        elif self.ua_mobile.isChecked():
            return "mobile"
        return "random"

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate browser configuration.

        Args:
            config: Configuration to validate.

        Returns:
            bool: True if configuration is valid.
        """
        try:
            browser_config = config['browser']
            # Check browser executable
            if browser_config['type'] == 'chrome' and not get_chrome_executable():
                logger.warning("Chrome executable not found")
                return False

            # Add additional validation as needed
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            dict: Current configuration.
        """
        return {
            'browser': {
                'type': self.browser_type.currentText().lower(),
                'user_agent': self._get_user_agent_setting(),
                'use_fingerprint': self.use_fingerprint.isChecked(),
                'connection_type': self.connection_type.currentText().lower(),
                'device_type': self.device_type.currentText().lower(),
                'use_cookies': self.use_cookies.isChecked(),
                'clear_cookies': self.clear_cookies.isChecked(),
                'clear_history': self.clear_history.isChecked(),
                'block_images': self.block_images.isChecked(),
                'block_javascript': self.block_js.isChecked()
            }
        }