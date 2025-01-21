#!/usr/bin/env python3
"""
Main entry point for the YouTube Live Comment Bot application.
"""

import sys
import logging
import argparse
import traceback
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from . import get_logger, setup_logging, __version__
from .core.config import Config, load_config
from .core.task_manager import TaskManager
from .gui.main_window import MainWindow
from .utils import helpers  # Import the helpers module directly

logger = get_logger()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='YouTube Live Comment Bot',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no GUI)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'YouTube Live Comment Bot v{__version__}'
    )
    return parser.parse_args()


def setup_application() -> QApplication:
    """Initialize and configure the QApplication instance."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Live Comment Bot")
    app.setApplicationVersion(__version__)

    # Set application style
    try:
        style_path = Path(__file__).parent / 'resources' / 'ui' / 'styles' / 'main.qss'
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        logger.warning(f"Failed to load application style: {e}")

    return app


def show_error_dialog(error_msg: str, detail_msg: Optional[str] = None):
    """Display error message in a dialog box."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setText(error_msg)
    if detail_msg:
        msg_box.setDetailedText(detail_msg)
    msg_box.setWindowTitle("Error")
    msg_box.exec()


def run_gui_mode(config: Config) -> int:
    """Run the application in GUI mode."""
    try:
        app = setup_application()

        # Create task manager
        task_manager = TaskManager(config)

        # Create and show main window
        main_window = MainWindow(task_manager)
        main_window.show()

        # Start application event loop
        return app.exec()

    except Exception as e:
        error_msg = "Failed to start application"
        detail_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        logger.error(detail_msg)
        show_error_dialog(error_msg, detail_msg)
        return 1


def run_headless_mode(config: Config) -> int:
    """Run the application in headless mode."""
    try:
        # Create task manager
        task_manager = TaskManager(config)

        # Start automated tasks
        task_manager.start_scheduled_tasks()

        # Keep the application running
        while True:
            if not task_manager.has_active_tasks():
                logger.info("No active tasks remaining, shutting down.")
                break

        return 0

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Error in headless mode: {e}\n{traceback.format_exc()}")
        return 1


def main() -> int:
    """Main entry point of the application."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Setup logging
        log_level = logging.DEBUG if args.debug else logging.INFO
        setup_logging(log_level)

        # Setup crash handling
        helpers.setup_crash_handler()  # Use the correct import

        logger.info(f"Starting YouTube Live Comment Bot v{__version__}")

        # Load configuration
        try:
            config = load_config(args.config) if args.config else load_config()
        except Exception as e:
            error_msg = "Failed to load configuration"
            detail_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logger.error(detail_msg)
            show_error_dialog(error_msg, detail_msg)
            return 1

        # Run in appropriate mode
        if args.headless:
            return run_headless_mode(config)
        else:
            return run_gui_mode(config)

    except Exception as e:
        logger.critical(f"Unhandled exception: {e}\n{traceback.format_exc()}")
        return 1
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    sys.exit(main())