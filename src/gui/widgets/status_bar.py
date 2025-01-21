"""
Status bar widget for YouTube Live Comment Bot.
"""

from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import Qt


class StatusBar(QStatusBar):
    """Custom status bar widget."""

    def __init__(self, parent=None):
        """Initialize status bar."""
        super().__init__(parent)

        # Create status labels
        self.status_label = QLabel()
        self.task_label = QLabel()
        self.info_label = QLabel()

        # Add widgets to status bar
        self.addWidget(self.status_label, 1)
        self.addWidget(self.task_label)
        self.addWidget(self.info_label)

        # Set initial messages
        self.status_label.setText("Ready")
        self.clear_task_info()

    def show_message(self, message: str, timeout: int = 5000) -> None:
        """Show a temporary message in the status bar.

        Args:
            message: Message to display.
            timeout: Message display duration in milliseconds.
        """
        self.showMessage(message, timeout)

    def show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display.
        """
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: red")

    def show_success(self, message: str) -> None:
        """Show success message.

        Args:
            message: Success message to display.
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green")

    def show_warning(self, message: str) -> None:
        """Show warning message.

        Args:
            message: Warning message to display.
        """
        self.status_label.setText(f"Warning: {message}")
        self.status_label.setStyleSheet("color: orange")

    def show_info(self, message: str) -> None:
        """Show info message.

        Args:
            message: Info message to display.
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet("")

    def update_task_info(self, status: str) -> None:
        """Update task status information.

        Args:
            status: Current task status.
        """
        self.task_label.setText(f"Task: {status}")

    def clear_task_info(self) -> None:
        """Clear task status information."""
        self.task_label.setText("No active task")