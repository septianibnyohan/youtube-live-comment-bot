"""
Configuration management module for YouTube Live Comment Bot.

This module handles loading, validating, and managing application configuration.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from pathlib import Path

from . import CoreError
from ..utils import validate_url, validate_proxy_string  # Import from utils package directly

logger = logging.getLogger(__name__)


class ConfigError(CoreError):
    """Raised when there's an error in configuration."""
    pass


@dataclass
class ProxyConfig:
    """Proxy configuration settings."""
    enabled: bool = False
    type: str = "http"
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    check_ip: bool = True
    check_score: bool = True
    min_score: int = 70
    rotation_interval: int = 300  # seconds


@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    type: str = "chrome"
    headless: bool = False
    user_agent: Optional[str] = None
    use_fingerprint: bool = True
    clear_cookies: bool = True
    clear_history: bool = True
    timeout: int = 30
    page_load_timeout: int = 30


@dataclass
class AutomationConfig:
    """Automation behavior configuration."""
    # Existing attributes
    watch_duration_min: int = 30
    watch_duration_max: int = 300
    comment_delay: int = 5
    max_comments_per_user: int = 5

    # Add new attributes
    mode_traffic: str = "browse"  # browse, keyword, channel, playlist
    keywords: List[str] = field(default_factory=list)
    thread_count: int = 1
    view_count: int = 1

    # Video behavior
    auto_play: bool = True
    watch_random: bool = True
    skip_ads: bool = True
    skip_ads_after: int = 5
    visit_other_videos: bool = True

    # Actions
    auto_like: bool = False
    auto_subscribe: bool = False
    randomize_comments: bool = True
    use_emojis: bool = True
    filter_duplicates: bool = True
    browser_interval: int = 30

    def __post_init__(self):
        """Post initialization validation."""
        if self.watch_duration_min > self.watch_duration_max:
            raise ConfigError("Minimum watch duration cannot be greater than maximum")
        if self.comment_delay < 1:
            raise ConfigError("Comment delay must be at least 1 second")


@dataclass
class ScheduleConfig:
    """Scheduling configuration."""
    enabled: bool = False
    type: str = "interval"  # "interval" or "specific"
    interval: int = 3600  # seconds
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days: List[str] = None


@dataclass
class Config:
    """Main configuration class."""
    proxy: ProxyConfig
    browser: BrowserConfig
    automation: AutomationConfig
    schedule: ScheduleConfig

    @classmethod
    def get_default(cls) -> 'Config':
        """Get default configuration."""
        return cls(
            proxy=ProxyConfig(),
            browser=BrowserConfig(),
            automation=AutomationConfig(),
            schedule=ScheduleConfig()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'proxy': asdict(self.proxy),
            'browser': asdict(self.browser),
            'automation': asdict(self.automation),
            'schedule': asdict(self.schedule)
        }

    def __post_init__(self):
        """Convert dict configs to dataclass instances if needed."""
        if isinstance(self.proxy, dict):
            self.proxy = ProxyConfig(**self.proxy)
        if isinstance(self.browser, dict):
            self.browser = BrowserConfig(**self.browser)
        if isinstance(self.automation, dict):
            self.automation = AutomationConfig(**self.automation)
        if isinstance(self.schedule, dict):
            self.schedule = ScheduleConfig(**self.schedule)

    def save(self, filepath: str) -> None:
        """Save configuration to file.

        Args:
            filepath: Path to save configuration file.

        Raises:
            ConfigError: If saving fails.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration: {e}")


def get_default_config() -> Config:
    """Get default configuration."""
    return Config(
        proxy=ProxyConfig(),
        browser=BrowserConfig(),
        automation=AutomationConfig(),
        schedule=ScheduleConfig()
    )


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ConfigError: If configuration is invalid.
    """
    required_sections = ['proxy', 'browser', 'automation', 'schedule']

    # Check required sections
    for section in required_sections:
        if section not in config:
            raise ConfigError(f"Missing required section: {section}")

    # Validate proxy configuration
    proxy_config = config['proxy']
    if proxy_config.get('enabled', False):
        if not proxy_config.get('host'):
            raise ConfigError("Proxy host is required when proxy is enabled")
        if not proxy_config.get('port'):
            raise ConfigError("Proxy port is required when proxy is enabled")

        # Validate proxy string
        proxy_string = f"{proxy_config['host']}:{proxy_config['port']}"
        if not validate_proxy_string(proxy_string):
            raise ConfigError(f"Invalid proxy string: {proxy_string}")

    # Validate browser configuration
    browser_config = config['browser']
    if browser_config['type'] not in ['chrome', 'firefox', 'edge']:
        raise ConfigError(f"Invalid browser type: {browser_config['type']}")

    # Validate automation configuration
    automation_config = config['automation']
    if automation_config['watch_duration_min'] > automation_config['watch_duration_max']:
        raise ConfigError("Minimum watch duration cannot be greater than maximum")
    if automation_config['comment_interval'] < 1:
        raise ConfigError("Comment interval must be at least 1 second")

    # Validate schedule configuration
    schedule_config = config['schedule']
    if schedule_config.get('enabled', False):
        if schedule_config['type'] not in ['interval', 'specific']:
            raise ConfigError(f"Invalid schedule type: {schedule_config['type']}")
        if schedule_config['type'] == 'specific':
            if not schedule_config.get('start_time'):
                raise ConfigError("Start time is required for specific schedule")


def load_config(filepath: Optional[str] = None) -> Config:
    """Load configuration from file.

    Args:
        filepath: Path to configuration file. If None, loads default config.

    Returns:
        Config: Loaded configuration object.

    Raises:
        ConfigError: If loading or validation fails.
    """
    try:
        if filepath is None:
            # Try to find config in default locations
            default_locations = [
                Path.cwd() / 'config.json',
                Path.home() / '.youtube_bot' / 'config.json',
                Path(__file__).parent.parent.parent / 'config' / 'config.json'
            ]

            for path in default_locations:
                if path.exists():
                    filepath = str(path)
                    break
            else:
                logger.info("No configuration file found, using defaults")
                return get_default_config()

        # Load and parse configuration file
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)

        # Validate configuration
        validate_config(config_dict)

        # Create configuration object
        return Config(**config_dict)

    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {e}")


def merge_configs(base: Config, override: Dict[str, Any]) -> Config:
    """Merge override configuration into base configuration.

    Args:
        base: Base configuration object.
        override: Override configuration dictionary.

    Returns:
        Config: Merged configuration object.
    """
    base_dict = base.to_dict()

    # Deep merge dictionaries
    for key, value in override.items():
        if key in base_dict and isinstance(base_dict[key], dict):
            base_dict[key].update(value)
        else:
            base_dict[key] = value

    return Config(**base_dict)