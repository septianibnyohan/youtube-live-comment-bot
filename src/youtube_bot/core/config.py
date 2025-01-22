"""
Configuration management module for YouTube Live Comment Bot.

This module handles loading, validating, and managing application configuration.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
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
    # Basic settings
    enabled: bool = False
    type: str = "http"
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None

    # Proxy list
    proxy_list: List[str] = field(default_factory=list)

    # Verification settings
    check_whoer: bool = True
    check_residential: bool = True
    check_timeout: bool = True
    min_score: int = 70
    timeout: int = 10

    # Rotation settings
    enable_rotation: bool = False
    rotation_interval: int = 300  # seconds

    def __post_init__(self):
        """Post initialization validation."""
        # Validate proxy type
        valid_types = ["http", "https", "socks4", "socks5"]
        if self.type not in valid_types:
            raise ConfigError(f"Invalid proxy type. Must be one of: {valid_types}")

        # Validate port range
        if self.port < 0 or self.port > 65535:
            raise ConfigError("Port must be between 0 and 65535")

        # Validate timeout
        if self.timeout < 1:
            raise ConfigError("Timeout must be at least 1 second")

        # Validate min score
        if not (0 <= self.min_score <= 100):
            raise ConfigError("Minimum score must be between 0 and 100")

        # Validate rotation interval
        if self.rotation_interval < 1:
            raise ConfigError("Rotation interval must be at least 1 second")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'enabled': self.enabled,
            'type': self.type,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'proxy_list': self.proxy_list,
            'check_whoer': self.check_whoer,
            'check_residential': self.check_residential,
            'check_timeout': self.check_timeout,
            'min_score': self.min_score,
            'timeout': self.timeout,
            'enable_rotation': self.enable_rotation,
            'rotation_interval': self.rotation_interval
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyConfig':
        """Create configuration from dictionary."""
        return cls(
            enabled=data.get('enabled', False),
            type=data.get('type', 'http'),
            host=data.get('host', ''),
            port=data.get('port', 0),
            username=data.get('username'),
            password=data.get('password'),
            proxy_list=data.get('proxy_list', []),
            check_whoer=data.get('check_whoer', True),
            check_residential=data.get('check_residential', True),
            check_timeout=data.get('check_timeout', True),
            min_score=data.get('min_score', 70),
            timeout=data.get('timeout', 10),
            enable_rotation=data.get('enable_rotation', False),
            rotation_interval=data.get('rotation_interval', 300)
        )

    def get_proxy_string(self) -> Optional[str]:
        """Get proxy string in format protocol://username:password@host:port.

        Returns:
            str: Formatted proxy string or None if proxy not configured.
        """
        if not self.enabled or not self.host or not self.port:
            return None

        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"{self.type}://{auth}{self.host}:{self.port}"


@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    # Browser type and path
    type: str = "chrome"
    executable_path: Optional[str] = None
    headless: bool = False

    # Connection settings
    connection_type: str = "direct"  # direct, proxy, vpn

    # User agent and fingerprint
    user_agent: Optional[str] = None
    use_fingerprint: bool = False
    randomize_fingerprint: bool = False

    # Device settings
    device_type: str = "desktop"  # desktop, mobile, random
    screen_size: Optional[Tuple[int, int]] = None

    # Cookie and history settings
    use_cookies: bool = True
    clear_cookies: bool = True
    clear_history: bool = True
    cookie_file: Optional[str] = None

    # Browser behavior
    page_load_timeout: int = 30
    block_images: bool = False
    block_javascript: bool = False

    # Video playback settings
    video_quality: str = "auto"
    autoplay: bool = True
    start_muted: bool = False
    show_annotations: bool = False

    def __post_init__(self):
        """Post initialization validation."""
        # Validate browser type
        valid_browsers = ["chrome", "firefox", "edge"]
        if self.type not in valid_browsers:
            raise ConfigError(f"Invalid browser type. Must be one of: {valid_browsers}")

        # Validate connection type
        valid_connections = ["direct", "proxy", "vpn"]
        if self.connection_type not in valid_connections:
            raise ConfigError(f"Invalid connection type. Must be one of: {valid_connections}")

        # Validate device type
        valid_devices = ["desktop", "mobile", "random"]
        if self.device_type not in valid_devices:
            raise ConfigError(f"Invalid device type. Must be one of: {valid_devices}")

        # Validate timeout
        if self.page_load_timeout < 1:
            raise ConfigError("Page load timeout must be at least 1 second")

        # Validate screen size if provided
        if self.screen_size:
            width, height = self.screen_size
            if width < 1 or height < 1:
                raise ConfigError("Screen dimensions must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'type': self.type,
            'executable_path': self.executable_path,
            'headless': self.headless,
            'connection_type': self.connection_type,
            'user_agent': self.user_agent,
            'use_fingerprint': self.use_fingerprint,
            'randomize_fingerprint': self.randomize_fingerprint,
            'device_type': self.device_type,
            'screen_size': self.screen_size,
            'use_cookies': self.use_cookies,
            'clear_cookies': self.clear_cookies,
            'clear_history': self.clear_history,
            'cookie_file': self.cookie_file,
            'page_load_timeout': self.page_load_timeout,
            'block_images': self.block_images,
            'block_javascript': self.block_javascript,
            'video_quality': self.video_quality,
            'autoplay': self.autoplay,
            'start_muted': self.start_muted,
            'show_annotations': self.show_annotations
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserConfig':
        """Create configuration from dictionary."""
        return cls(
            type=data.get('type', 'chrome'),
            executable_path=data.get('executable_path'),
            headless=data.get('headless', False),
            connection_type=data.get('connection_type', 'direct'),
            user_agent=data.get('user_agent'),
            use_fingerprint=data.get('use_fingerprint', False),
            randomize_fingerprint=data.get('randomize_fingerprint', False),
            device_type=data.get('device_type', 'desktop'),
            screen_size=data.get('screen_size'),
            use_cookies=data.get('use_cookies', True),
            clear_cookies=data.get('clear_cookies', True),
            clear_history=data.get('clear_history', True),
            cookie_file=data.get('cookie_file'),
            page_load_timeout=data.get('page_load_timeout', 30),
            block_images=data.get('block_images', False),
            block_javascript=data.get('block_javascript', False),
            video_quality=data.get('video_quality', 'auto'),
            autoplay=data.get('autoplay', True),
            start_muted=data.get('start_muted', False),
            show_annotations=data.get('show_annotations', False)
        )


@dataclass
class AutomationConfig:
    """Automation behavior configuration."""
    # Time settings
    watch_duration_min: int = 30
    watch_duration_max: int = 300
    comment_delay: int = 5
    random_delay_min: int = 2
    random_delay_max: int = 10

    # Comment settings
    max_comments_per_user: int = 5
    randomize_comments: bool = True
    comments: List[str] = field(default_factory=list)
    comment_language: str = "English"

    # Traffic settings
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
    use_emojis: bool = True
    filter_duplicates: bool = True
    browser_interval: int = 30

    def __post_init__(self):
        """Post initialization validation."""
        # Validate watch duration
        if self.watch_duration_min > self.watch_duration_max:
            raise ConfigError("Minimum watch duration cannot be greater than maximum")

        # Validate delays
        if self.comment_delay < 1:
            raise ConfigError("Comment delay must be at least 1 second")

        if self.random_delay_min > self.random_delay_max:
            raise ConfigError("Minimum random delay cannot be greater than maximum")

        if self.random_delay_min < 0:
            raise ConfigError("Random delay minimum cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'watch_duration_min': self.watch_duration_min,
            'watch_duration_max': self.watch_duration_max,
            'comment_delay': self.comment_delay,
            'random_delay_min': self.random_delay_min,
            'random_delay_max': self.random_delay_max,
            'max_comments_per_user': self.max_comments_per_user,
            'randomize_comments': self.randomize_comments,
            'comments': self.comments,
            'comment_language': self.comment_language,
            'mode_traffic': self.mode_traffic,
            'keywords': self.keywords,
            'thread_count': self.thread_count,
            'view_count': self.view_count,
            'auto_play': self.auto_play,
            'watch_random': self.watch_random,
            'skip_ads': self.skip_ads,
            'skip_ads_after': self.skip_ads_after,
            'visit_other_videos': self.visit_other_videos,
            'auto_like': self.auto_like,
            'auto_subscribe': self.auto_subscribe,
            'use_emojis': self.use_emojis,
            'filter_duplicates': self.filter_duplicates,
            'browser_interval': self.browser_interval
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationConfig':
        """Create configuration from dictionary."""
        return cls(
            watch_duration_min=data.get('watch_duration_min', 30),
            watch_duration_max=data.get('watch_duration_max', 300),
            comment_delay=data.get('comment_delay', 5),
            random_delay_min=data.get('random_delay_min', 2),
            random_delay_max=data.get('random_delay_max', 10),
            max_comments_per_user=data.get('max_comments_per_user', 5),
            randomize_comments=data.get('randomize_comments', True),
            comments=data.get('comments', []),
            comment_language=data.get('comment_language', 'English'),
            mode_traffic=data.get('mode_traffic', 'browse'),
            keywords=data.get('keywords', []),
            thread_count=data.get('thread_count', 1),
            view_count=data.get('view_count', 1),
            auto_play=data.get('auto_play', True),
            watch_random=data.get('watch_random', True),
            skip_ads=data.get('skip_ads', True),
            skip_ads_after=data.get('skip_ads_after', 5),
            visit_other_videos=data.get('visit_other_videos', True),
            auto_like=data.get('auto_like', False),
            auto_subscribe=data.get('auto_subscribe', False),
            use_emojis=data.get('use_emojis', True),
            filter_duplicates=data.get('filter_duplicates', True),
            browser_interval=data.get('browser_interval', 30)
        )


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