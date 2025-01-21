"""
Proxy tab for YouTube Live Comment Bot.

This module contains the proxy configuration tab interface.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QFileDialog, QSpinBox, QScrollArea,
    QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core import TaskManager
from ..utils.helpers import parse_proxy_string, validate_proxy_string
from . import DEFAULT_SPACING, DEFAULT_MARGIN

logger = logging.getLogger(__name__)


class ProxyTab(QWidget):
    """Proxy configuration tab widget."""

    # Signal emitted when proxy configuration changes
    proxy_changed = pyqtSignal(dict)

    def __init__(self, task_manager: TaskManager):
        """Initialize proxy tab."""
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

        # Proxy Settings Group
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QVBoxLayout()

        # Enable proxy checkbox
        self.enable_proxy = QCheckBox("Enable Proxy")
        proxy_layout.addWidget(self.enable_proxy)

        # Proxy type selection
        type_layout = QHBoxLayout()
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        type_layout.addWidget(QLabel("Proxy Type:"))
        type_layout.addWidget(self.proxy_type)
        proxy_layout.addLayout(type_layout)

        proxy_group.setLayout(proxy_layout)
        content_layout.addWidget(proxy_group)

        # Proxy List Group
        list_group = QGroupBox("Proxy List")
        list_layout = QVBoxLayout()

        # Proxy list input
        self.proxy_list = QTextEdit()
        self.proxy_list.setPlaceholderText(
            "Enter proxies (one per line)\nFormat: protocol://username:password@host:port")
        list_layout.addWidget(self.proxy_list)

        # Import/Export buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import from File")
        self.export_button = QPushButton("Export to File")
        self.verify_button = QPushButton("Verify Proxies")

        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.verify_button)
        list_layout.addLayout(button_layout)

        list_group.setLayout(list_layout)
        content_layout.addWidget(list_group)

        # Proxy Verification Group
        verify_group = QGroupBox("Proxy Verification")
        verify_layout = QVBoxLayout()

        # Verification settings
        self.check_whoer = QCheckBox("Check Whoer.net Score")
        self.check_residential = QCheckBox("Verify Residential IP")
        self.check_timeout = QCheckBox("Check Response Time")

        verify_layout.addWidget(self.check_whoer)
        verify_layout.addWidget(self.check_residential)
        verify_layout.addWidget(self.check_timeout)

        # Minimum score
        score_layout = QHBoxLayout()
        self.min_score = QSpinBox()
        self.min_score.setRange(0, 100)
        self.min_score.setValue(70)
        self.min_score.setSuffix("%")
        score_layout.addWidget(QLabel("Minimum Whoer Score:"))
        score_layout.addWidget(self.min_score)
        verify_layout.addLayout(score_layout)

        # Timeout setting
        timeout_layout = QHBoxLayout()
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(10)
        self.timeout.setSuffix(" seconds")
        timeout_layout.addWidget(QLabel("Connection Timeout:"))
        timeout_layout.addWidget(self.timeout)
        verify_layout.addLayout(timeout_layout)

        verify_group.setLayout(verify_layout)
        content_layout.addWidget(verify_group)

        # Proxy Rotation Group
        rotation_group = QGroupBox("Proxy Rotation")
        rotation_layout = QVBoxLayout()

        self.enable_rotation = QCheckBox("Enable Proxy Rotation")
        rotation_layout.addWidget(self.enable_rotation)

        # Rotation interval
        interval_layout = QHBoxLayout()
        self.rotation_interval = QSpinBox()
        self.rotation_interval.setRange(1, 3600)
        self.rotation_interval.setValue(300)
        self.rotation_interval.setSuffix(" seconds")
        interval_layout.addWidget(QLabel("Rotation Interval:"))
        interval_layout.addWidget(self.rotation_interval)
        rotation_layout.addLayout(interval_layout)

        rotation_group.setLayout(rotation_layout)
        content_layout.addWidget(rotation_group)

        # Add stretch to bottom
        content_layout.addStretch()

        # Set scroll widget
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        self.enable_proxy.stateChanged.connect(self._update_config)
        self.proxy_type.currentTextChanged.connect(self._update_config)
        self.proxy_list.textChanged.connect(self._update_config)
        self.check_whoer.stateChanged.connect(self._update_config)
        self.check_residential.stateChanged.connect(self._update_config)
        self.check_timeout.stateChanged.connect(self._update_config)
        self.min_score.valueChanged.connect(self._update_config)
        self.timeout.valueChanged.connect(self._update_config)
        self.enable_rotation.stateChanged.connect(self._update_config)
        self.rotation_interval.valueChanged.connect(self._update_config)

        # Button connections
        self.import_button.clicked.connect(self._import_proxies)
        self.export_button.clicked.connect(self._export_proxies)
        self.verify_button.clicked.connect(self._verify_proxies)

    def _load_config(self) -> None:
        """Load configuration into UI elements."""
        config = self.task_manager.config.proxy

        self.enable_proxy.setChecked(config.enabled)
        self.proxy_type.setCurrentText(config.type.upper())

        if config.proxy_list:
            self.proxy_list.setPlainText("\n".join(config.proxy_list))

        self.check_whoer.setChecked(config.check_whoer)
        self.check_residential.setChecked(config.check_residential)
        self.check_timeout.setChecked(config.check_timeout)
        self.min_score.setValue(config.min_score)
        self.timeout.setValue(config.timeout)
        self.enable_rotation.setChecked(config.enable_rotation)
        self.rotation_interval.setValue(config.rotation_interval)

    def _update_config(self) -> None:
        """Update configuration from UI elements."""
        config = {
            'proxy': {
                'enabled': self.enable_proxy.isChecked(),
                'type': self.proxy_type.currentText().lower(),
                'proxy_list': self._get_proxy_list(),
                'check_whoer': self.check_whoer.isChecked(),
                'check_residential': self.check_residential.isChecked(),
                'check_timeout': self.check_timeout.isChecked(),
                'min_score': self.min_score.value(),
                'timeout': self.timeout.value(),
                'enable_rotation': self.enable_rotation.isChecked(),
                'rotation_interval': self.rotation_interval.value()
            }
        }

        self.proxy_changed.emit(config)

    def _get_proxy_list(self) -> List[str]:
        """Get list of proxies from input.

        Returns:
            list: List of proxy strings.
        """
        text = self.proxy_list.toPlainText().strip()
        if not text:
            return []

        return [line.strip() for line in text.split('\n') if line.strip()]

    def _import_proxies(self) -> None:
        """Import proxies from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Proxies",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    proxies = f.read()
                self.proxy_list.setPlainText(proxies)
                QMessageBox.information(
                    self,
                    "Import Successful",
                    "Proxies imported successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import proxies: {str(e)}"
                )

    def _export_proxies(self) -> None:
        """Export proxies to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Proxies",
            "",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.proxy_list.toPlainText())
                QMessageBox.information(
                    self,
                    "Export Successful",
                    "Proxies exported successfully."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export proxies: {str(e)}"
                )

    def _verify_proxies(self) -> None:
        """Verify proxy list."""
        proxies = self._get_proxy_list()
        if not proxies:
            QMessageBox.warning(
                self,
                "No Proxies",
                "Please add proxies to verify."
            )
            return

        # TODO: Implement proxy verification
        QMessageBox.information(
            self,
            "Verification",
            "Proxy verification not implemented yet."
        )

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            dict: Current configuration.
        """
        return {
            'proxy': {
                'enabled': self.enable_proxy.isChecked(),
                'type': self.proxy_type.currentText().lower(),
                'proxy_list': self._get_proxy_list(),
                'check_whoer': self.check_whoer.isChecked(),
                'check_residential': self.check_residential.isChecked(),
                'check_timeout': self.check_timeout.isChecked(),
                'min_score': self.min_score.value(),
                'timeout': self.timeout.value(),
                'enable_rotation': self.enable_rotation.isChecked(),
                'rotation_interval': self.rotation_interval.value()
            }
        }