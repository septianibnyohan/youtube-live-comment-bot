"""
Helper functions for YouTube Live Comment Bot.

This module provides various utility functions used throughout the application.
"""

import os
import sys
import random
import string
import logging
import platform
import tempfile
import subprocess
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import traceback

logger = logging.getLogger(__name__)


def setup_crash_handler() -> None:
    """Setup system-wide exception handler for crash reporting."""

    def handle_exception(exc_type: type, exc_value: Exception, exc_traceback: Any) -> None:
        """Handle uncaught exceptions.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            exc_traceback: Exception traceback.
        """
        # Check if it's a keyboard interrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log the full exception with traceback
        logger.critical("Uncaught exception:",
                        exc_info=(exc_type, exc_value, exc_traceback))

        # Create crash report
        crash_dir = Path(os.getcwd()) / 'crash_reports'
        crash_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        crash_file = crash_dir / f"crash_report_{timestamp}.txt"

        try:
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write(f"Crash Report - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")

                # System information
                f.write("System Information:\n")
                f.write(f"Python Version: {platform.python_version()}\n")
                f.write(f"OS: {platform.system()} {platform.release()}\n")
                f.write(f"Platform: {platform.platform()}\n\n")

                # Exception information
                f.write("Exception Information:\n")
                f.write(f"Type: {exc_type.__name__}\n")
                f.write(f"Message: {str(exc_value)}\n\n")

                # Traceback
                f.write("Traceback:\n")
                f.write(''.join(traceback.format_tb(exc_traceback)))

                logger.info(f"Crash report saved to {crash_file}")

        except Exception as e:
            logger.error(f"Failed to write crash report: {e}")

    # Set the exception handler
    sys.excepthook = handle_exception


def setup_exception_logging() -> None:
    """Configure exception logging for the application."""
    log_dir = Path(os.getcwd()) / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"exceptions_{datetime.now().strftime('%Y%m%d')}.log"

    # Configure file handler for exceptions
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to root logger
    logging.getLogger().addHandler(handler)

def generate_random_string(length: int = 10, include_digits: bool = True) -> str:
    """Generate a random string of specified length.

    Args:
        length: Length of string to generate.
        include_digits: Whether to include numbers.

    Returns:
        str: Random string.
    """
    characters = string.ascii_letters
    if include_digits:
        characters += string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL.

    Args:
        url: YouTube video URL.

    Returns:
        str: Video ID or None if not found.
    """
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/live/'):
                return parsed_url.path.split('/')[2]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        return None
    except Exception:
        return None


def get_system_info() -> Dict[str, str]:
    """Get system information.

    Returns:
        dict: System information.
    """
    return {
        'os': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def is_process_running(process_name: str) -> bool:
    """Check if a process is running.

    Args:
        process_name: Name of process to check.

    Returns:
        bool: True if process is running.
    """
    if platform.system() == "Windows":
        cmd = f'tasklist /FI "IMAGENAME eq {process_name}"'
        output = subprocess.check_output(cmd, shell=True).decode()
        return process_name in output
    else:
        cmd = f'pgrep -f {process_name}'
        try:
            subprocess.check_output(cmd, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False


def create_temp_file(content: str, suffix: Optional[str] = None) -> str:
    """Create a temporary file with given content.

    Args:
        content: Content to write to file.
        suffix: Optional file suffix.

    Returns:
        str: Path to temporary file.
    """
    try:
        with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=suffix,
                delete=False
        ) as temp_file:
            temp_file.write(content)
            return temp_file.name
    except Exception as e:
        logger.error(f"Failed to create temporary file: {e}")
        raise


def parse_time_string(time_str: str) -> Optional[timedelta]:
    """Parse time string into timedelta.

    Args:
        time_str: Time string (e.g., "1h30m", "45s", "2h30m15s").

    Returns:
        timedelta: Parsed time or None if invalid.
    """
    try:
        total_seconds = 0
        current_num = ""

        for char in time_str:
            if char.isdigit():
                current_num += char
            elif char in ['h', 'm', 's']:
                if current_num:
                    num = int(current_num)
                    if char == 'h':
                        total_seconds += num * 3600
                    elif char == 'm':
                        total_seconds += num * 60
                    else:  # 's'
                        total_seconds += num
                    current_num = ""

        return timedelta(seconds=total_seconds)
    except ValueError:
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.

    Args:
        filename: Filename to sanitize.

    Returns:
        str: Sanitized filename.
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')

    # Trim whitespace and dots
    filename = filename.strip('. ')

    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'

    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes.

    Returns:
        str: Formatted size string.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def ensure_unique_filename(filepath: Union[str, Path]) -> Path:
    """Ensure filename is unique by adding number suffix if needed.

    Args:
        filepath: Original file path.

    Returns:
        Path: Unique file path.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return filepath

    counter = 1
    while True:
        new_filepath = filepath.parent / f"{filepath.stem}_{counter}{filepath.suffix}"
        if not new_filepath.exists():
            return new_filepath
        counter += 1


def parse_proxy_string(proxy_str: str) -> Dict[str, str]:
    """Parse proxy string into components.

    Args:
        proxy_str: Proxy string (e.g., "http://user:pass@host:port").

    Returns:
        dict: Proxy components.
    """
    try:
        parsed = urlparse(proxy_str)
        auth = parsed.username, parsed.password
        return {
            'protocol': parsed.scheme,
            'host': parsed.hostname,
            'port': str(parsed.port),
            'username': auth[0],
            'password': auth[1]
        }
    except Exception as e:
        logger.error(f"Failed to parse proxy string: {e}")
        raise


def get_chrome_executable() -> Optional[str]:
    """Get path to Chrome executable.

    Returns:
        str: Path to Chrome executable or None if not found.
    """
    system = platform.system()

    if system == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
    elif system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser"
        ]

    for path in paths:
        if os.path.exists(path):
            return path

    return None


def calculate_time_diff(start_time: datetime, end_time: datetime) -> Tuple[int, int, int]:
    """Calculate time difference in hours, minutes, and seconds.

    Args:
        start_time: Start datetime.
        end_time: End datetime.

    Returns:
        tuple: Hours, minutes, seconds difference.
    """
    diff = end_time - start_time
    total_seconds = int(diff.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return hours, minutes, seconds


def parse_comments_file(filepath: Union[str, Path]) -> List[str]:
    """Parse comments from a text file.

    Args:
        filepath: Path to comments file.

    Returns:
        list: List of comments.
    """
    comments = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                comment = line.strip()
                if comment and not comment.startswith('#'):
                    comments.append(comment)
        return comments
    except Exception as e:
        logger.error(f"Failed to parse comments file: {e}")
        raise


def clean_temp_files(pattern: str = "*", max_age: int = 86400) -> None:
    """Clean temporary files older than specified age.

    Args:
        pattern: File pattern to match.
        max_age: Maximum file age in seconds.
    """
    temp_dir = Path(tempfile.gettempdir())
    cutoff_time = datetime.now() - timedelta(seconds=max_age)

    try:
        for file_path in temp_dir.glob(pattern):
            if file_path.stat().st_mtime < cutoff_time.timestamp():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning temp files: {e}")


def validate_proxy_string(proxy_str: str) -> bool:
    """Validate proxy string format.

    Args:
        proxy_str: Proxy string to validate (format: protocol://username:password@host:port)

    Returns:
        bool: True if proxy string is valid.
    """
    try:
        if not proxy_str:
            return False

        # Check basic format first
        if '://' not in proxy_str:
            return False

        # Split protocol and rest
        protocol, rest = proxy_str.split('://', 1)

        # Verify protocol
        if protocol not in ['http', 'https', 'socks4', 'socks5']:
            return False

        # Check if authentication is present
        if '@' in rest:
            auth, host_port = rest.rsplit('@', 1)
            if ':' not in auth:  # Must have username:password
                return False
        else:
            host_port = rest

        # Verify host:port format
        if ':' not in host_port:
            return False

        host, port = host_port.rsplit(':', 1)

        # Verify port is numeric and in valid range
        if not port.isdigit() or not (1 <= int(port) <= 65535):
            return False

        # Verify host is not empty
        if not host:
            return False

        return True

    except Exception:
        return False