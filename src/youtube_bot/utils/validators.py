"""
Validation utilities for YouTube Live Comment Bot.
"""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate.

    Returns:
        bool: True if URL is valid.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


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

        # Check basic format
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


def validate_youtube_url(url: str) -> bool:
    """Validate YouTube URL format.

    Args:
        url: URL to validate.

    Returns:
        bool: True if URL is valid YouTube URL.
    """
    try:
        patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/live/[\w-]+',
            r'^https?://youtu\.be/[\w-]+'
        ]

        return any(re.match(pattern, url) for pattern in patterns)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email to validate.

    Returns:
        bool: True if email is valid.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))