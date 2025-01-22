"""
Utilities module for YouTube Live Comment Bot.
"""

import logging
from . import validators  # Import validators module first

logger = logging.getLogger(__name__)

# Export validation functions
validate_url = validators.validate_url
validate_proxy_string = validators.validate_proxy_string
validate_youtube_url = validators.validate_youtube_url
validate_email = validators.validate_email

# Rest of the __init__.py content...

__all__ = [
    'validate_url',
    'validate_proxy_string',
    'validate_youtube_url',
    'validate_email',
    # ... other exports
]