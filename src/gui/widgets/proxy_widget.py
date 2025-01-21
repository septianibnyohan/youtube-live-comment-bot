"""
Proxy widget for YouTube Live Comment Bot.

This module contains a reusable proxy configuration widget.
"""

import logging
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QPushButton,
    QCheckBox, QMessageBox, QTextEdit
)
from PyQt6.QtCore import pyqtSignal

from ...utils.helpers import validate_proxy_string
from .. import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class ProxyWidget(QWidget):
    """Widget for proxy configuration."""

    # Signal emitted when proxy configuration changes
    proxy_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize proxy widget."""
        super().__init__(parent)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(DEFAULT_SPACING)
        layout.setContentsMargins(DEFAULT_MARGIN, DEFAULT_MARGIN,
                                  DEFAULT_MARGIN, DEFAULT_MARGIN)

        # Proxy Type
        type_layout = QHBoxLayout()
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        type_layout.addWidget(QLabel("Type:"))
        type_layout.addWidget(self.proxy_type)
        layout.addLayout(type_layout)

        # Host
        host_layout = QHBoxLayout()
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Proxy host")
        host_layout.addWidget(QLabel("Host:"))
        host_layout.addWidget(self.host_input)
        layout.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8080)
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        # Authentication
        self.use_auth = QCheckBox("Use Authentication")
        layout.addWidget(self.use_auth)

        # Username
        self.username_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setEnabled(False)
        self.username_layout.addWidget(QLabel("Username:"))
        self.username_layout.addWidget(self.username_input)
        layout.addLayout(self.username_layout)

        # Password
        self.password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setEnabled(False)
        self.password_layout.addWidget(QLabel("Password:"))
        self.password_layout.addWidget(self.password_input)
        layout.addLayout(self.password_layout)

        # Options
        self.verify_ssl = QCheckBox("Verify SSL")
        self.verify_ssl.setChecked(True)
        layout.addWidget(self.verify_ssl)

        # Timeout
        timeout_layout = QHBoxLayout()
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 60)
        self.timeout_input.setValue(10)
        self.timeout_input.setSuffix(" seconds")
        timeout_layout.addWidget(QLabel("Timeout:"))
        timeout_layout.addWidget(self.timeout_input)
        layout.addLayout(timeout_layout)

        # Test button
        self.test_button = QPushButton("Test Proxy")
        layout.addWidget(self.test_button)

        # Status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        layout.addStretch()

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        # Connect all inputs to update configuration
        self.proxy_type.currentTextChanged.connect(self._update_config)
        self.host_input.textChanged.connect(self._update_config)
        self.port_input.valueChanged.connect(self._update_config)
        self.use_auth.stateChanged.connect(self._toggle_auth)
        self.username_input.textChanged.connect(self._update_config)
        self.password_input.textChanged.connect(self._update_config)
        self.verify_ssl.stateChanged.connect(self._update_config)
        self.timeout_input.valueChanged.connect(self._update_config)

        # Connect test button
        self.test_button.clicked.connect(self._test_proxy)

    def _toggle_auth(self, state: int) -> None:
        """Toggle authentication input fields.

        Args:
            state: Checkbox state.
        """
        enabled = bool(state)
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self._update_config()

    def _update_config(self) -> None:
        """Update and emit proxy configuration."""
        config = {
            'type': self.proxy_type.currentText().lower(),
            'host': self.host_input.text(),
            'port': self.port_input.value(),
            'use_auth': self.use_auth.isChecked(),
            'username': self.username_input.text() if self.use_auth.isChecked() else None,
            'password': self.password_input.text() if self.use_auth.isChecked() else None,
            'verify_ssl': self.verify_ssl.isChecked(),
            'timeout': self.timeout_input.value()
        }

        # Validate configuration
        if self._validate_config(config):
            self.proxy_changed.emit(config)

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate proxy configuration.

        Args:
            config: Proxy configuration to validate.

        Returns:
            bool: True if configuration is valid.
        """
        # Build proxy string for validation
        proxy_str = f"{config['type']}://"

        if config['use_auth']:
            if not config['username'] or not config['password']:
                self.status_label.setText("Authentication credentials required")
                return False
            proxy_str += f"{config['username']}:{config['password']}@"

        proxy_str += f"{config['host']}:{config['port']}"

        # Validate proxy string
        if not validate_proxy_string(proxy_str):
            self.status_label.setText("Invalid proxy configuration")
            return False

        self.status_label.setText("Valid configuration")
        return True

    def _test_proxy(self) -> None:
        """Test proxy connection."""
        config = {
            'type': self.proxy_type.currentText().lower(),
            'host': self.host_input.text(),
            'port': self.port_input.value(),
            'use_auth': self.use_auth.isChecked(),
            'username': self.username_input.text() if self.use_auth.isChecked() else None,
            'password': self.password_input.text() if self.use_auth.isChecked() else None,
            'verify_ssl': self.verify_ssl.isChecked(),
            'timeout': self.timeout_input.value()
        }

        if not self._validate_config(config):
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please check your proxy configuration."
            )
            return

        # TODO: Implement actual proxy testing
        QMessageBox.information(
            self,
            "Test Proxy",
            "Proxy testing not implemented yet."
        )

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set proxy configuration.

        Args:
            config: Proxy configuration dictionary.
        """
        try:
            self.proxy_type.setCurrentText(config.get('type', 'http').upper())
            self.host_input.setText(config.get('host', ''))
            self.port_input.setValue(config.get('port', 8080))

            use_auth = config.get('use_auth', False)
            self.use_auth.setChecked(use_auth)
            if use_auth:
                self.username_input.setText(config.get('username', ''))
                self.password_input.setText(config.get('password', ''))

            self.verify_ssl.setChecked(config.get('verify_ssl', True))
            self.timeout_input.setValue(config.get('timeout', 10))

        except Exception as e:
            logger.error(f"Failed to set proxy configuration: {e}")
            self.status_label.setText("Failed to load configuration")

    def get_config(self) -> Dict[str, Any]:
        """Get current proxy configuration.

        Returns:
            dict: Current proxy configuration.
        """
        return {
            'type': self.proxy_type.currentText().lower(),
            'host': self.host_input.text(),
            'port': self.port_input.value(),
            'use_auth': self.use_auth.isChecked(),
            'username': self.username_input.text() if self.use_auth.isChecked() else None,
            'password': self.password_input.text() if self.use_auth.isChecked() else None,
            'verify_ssl': self.verify_ssl.isChecked(),
            'timeout': self.timeout_input.value()
        }

    def clear(self) -> None:
        """Clear proxy configuration."""
        self.host_input.clear()
        self.port_input.setValue(8080)
        self.use_auth.setChecked(False)
        self.username_input.clear()
        self.password_input.clear()
        self.verify_ssl.setChecked(True)
        self.timeout_input.setValue(10)
        self.status_label.clear()