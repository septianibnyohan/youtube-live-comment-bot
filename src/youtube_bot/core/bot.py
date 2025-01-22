"""
Bot module for YouTube Live Comment Bot.

This module contains the core bot functionality for YouTube automation.
"""

import logging
import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dataclasses import dataclass

from .config import Config
from . import CoreError

logger = logging.getLogger(__name__)


class BotError(CoreError):
    """Bot-specific error."""
    pass


class Bot:
    """Core bot class for YouTube automation."""

    def __init__(self, config: Config):
        """Initialize bot.

        Args:
            config: Bot configuration.
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.running = False
        self.paused = False

    def start(self) -> None:
        """Start the bot.

        Raises:
            BotError: If bot fails to start.
        """
        try:
            if self.running:
                return

            self._setup_driver()
            self.running = True
            logger.info("Bot started")

        except Exception as e:
            raise BotError(f"Failed to start bot: {e}")

    def stop(self) -> None:
        """Stop the bot."""
        self.running = False
        self._cleanup()
        logger.info("Bot stopped")

    def pause(self) -> None:
        """Pause bot operations."""
        self.paused = True
        logger.info("Bot paused")

    def resume(self) -> None:
        """Resume bot operations."""
        self.paused = False
        logger.info("Bot resumed")

    def _setup_driver(self) -> None:
        """Setup and configure webdriver.

        Raises:
            BotError: If driver setup fails.
        """
        try:
            options = webdriver.ChromeOptions()

            # Configure browser settings
            if self.config.browser.headless:
                options.add_argument('--headless')

            if self.config.browser.user_agent:
                options.add_argument(f'user-agent={self.config.browser.user_agent}')

            # Proxy configuration
            if self.config.proxy.enabled and self.config.proxy.host:
                proxy_string = f"{self.config.proxy.type}://{self.config.proxy.host}:{self.config.proxy.port}"
                options.add_argument(f'--proxy-server={proxy_string}')

            # Additional settings
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            if self.config.browser.block_images:
                options.add_argument('--blink-settings=imagesEnabled=false')

            # Create driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.browser.page_load_timeout)

            logger.debug("WebDriver setup complete")

        except Exception as e:
            raise BotError(f"Failed to setup WebDriver: {e}")

    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.driver:
            try:
                if self.config.browser.clear_cookies:
                    self.driver.delete_all_cookies()
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.driver = None

    def navigate_to_video(self, video_id: str) -> bool:
        """Navigate to a YouTube video.

        Args:
            video_id: YouTube video ID.

        Returns:
            bool: True if navigation successful.
        """
        if not self.driver:
            return False

        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            self.driver.get(url)

            # Wait for video player to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "movie_player"))
            )

            return True

        except Exception as e:
            logger.error(f"Failed to navigate to video: {e}")
            return False

    def post_comment(self, comment: str) -> bool:
        """Post a comment on the current video.

        Args:
            comment: Comment text to post.

        Returns:
            bool: True if comment posted successfully.
        """
        if not self.driver:
            return False

        try:
            # Find and click comment box
            comment_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#comment-input"))
            )
            comment_box.click()

            # Type comment
            comment_box.send_keys(comment)
            time.sleep(random.uniform(1, 3))  # Human-like delay

            # Submit comment
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "#submit-button")
            submit_button.click()

            return True

        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return False

    def like_video(self) -> bool:
        """Like the current video.

        Returns:
            bool: True if like successful.
        """
        if not self.driver:
            return False

        try:
            like_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#like-button"))
            )
            like_button.click()
            return True

        except Exception as e:
            logger.error(f"Failed to like video: {e}")
            return False

    def subscribe_to_channel(self) -> bool:
        """Subscribe to the current channel.

        Returns:
            bool: True if subscription successful.
        """
        if not self.driver:
            return False

        try:
            subscribe_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#subscribe-button"))
            )
            subscribe_button.click()
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")
            return False

    def is_live(self) -> bool:
        """Check if current video is live.

        Returns:
            bool: True if video is live.
        """
        if not self.driver:
            return False

        try:
            return bool(self.driver.find_elements(By.CSS_SELECTOR, ".ytp-live-badge"))
        except Exception:
            return False

    def wait_for_duration(self, duration: int) -> None:
        """Wait for specified duration with human-like behavior.

        Args:
            duration: Time to wait in seconds.
        """
        end_time = time.time() + duration
        while time.time() < end_time and self.running and not self.paused:
            # Simulate human-like interaction
            if random.random() < 0.1:  # 10% chance each second
                scroll_amount = random.randint(-300, 300)
                try:
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                except Exception:
                    pass
            time.sleep(1)

    def clear_history(self) -> None:
        """Clear browser history if enabled."""
        if not self.driver or not self.config.browser.clear_history:
            return

        try:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            self.driver.delete_all_cookies()
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")

    @property
    def current_url(self) -> Optional[str]:
        """Get current URL.

        Returns:
            str: Current URL or None if not available.
        """
        if self.driver:
            try:
                return self.driver.current_url
            except Exception:
                pass
        return None

@dataclass
class BotConfig:
    """Configuration settings for the bot."""

    # Browser settings
    browser_type: str = "chrome"
    headless: bool = False
    user_agent: Optional[str] = None
    page_load_timeout: int = 30

    # Automation settings
    comment_delay: int = 5
    watch_duration_min: int = 30
    watch_duration_max: int = 300
    max_comments_per_user: int = 5
    randomize_comments: bool = True

    # Actions
    auto_like: bool = False
    auto_subscribe: bool = False
    use_emojis: bool = True

    # Browser behavior
    clear_cookies: bool = True
    clear_history: bool = True
    block_images: bool = False

    # Video settings
    video_quality: str = "auto"
    autoplay: bool = True
    mute_video: bool = False

    # Safety settings
    max_daily_comments: int = 100
    max_daily_likes: int = 50
    max_daily_subscribes: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            dict: Configuration as dictionary.
        """
        return {
            'browser': {
                'type': self.browser_type,
                'headless': self.headless,
                'user_agent': self.user_agent,
                'page_load_timeout': self.page_load_timeout
            },
            'automation': {
                'comment_delay': self.comment_delay,
                'watch_duration_min': self.watch_duration_min,
                'watch_duration_max': self.watch_duration_max,
                'max_comments_per_user': self.max_comments_per_user,
                'randomize_comments': self.randomize_comments
            },
            'actions': {
                'auto_like': self.auto_like,
                'auto_subscribe': self.auto_subscribe,
                'use_emojis': self.use_emojis
            },
            'browser_behavior': {
                'clear_cookies': self.clear_cookies,
                'clear_history': self.clear_history,
                'block_images': self.block_images
            },
            'video': {
                'quality': self.video_quality,
                'autoplay': self.autoplay,
                'mute': self.mute_video
            },
            'safety': {
                'max_daily_comments': self.max_daily_comments,
                'max_daily_likes': self.max_daily_likes,
                'max_daily_subscribes': self.max_daily_subscribes
            }
        }

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'BotConfig':
        """Create configuration from dictionary.

        Args:
            config: Configuration dictionary.

        Returns:
            BotConfig: Configuration instance.
        """
        return cls(
            browser_type=config.get('browser', {}).get('type', 'chrome'),
            headless=config.get('browser', {}).get('headless', False),
            user_agent=config.get('browser', {}).get('user_agent'),
            page_load_timeout=config.get('browser', {}).get('page_load_timeout', 30),

            comment_delay=config.get('automation', {}).get('comment_delay', 5),
            watch_duration_min=config.get('automation', {}).get('watch_duration_min', 30),
            watch_duration_max=config.get('automation', {}).get('watch_duration_max', 300),
            max_comments_per_user=config.get('automation', {}).get('max_comments_per_user', 5),
            randomize_comments=config.get('automation', {}).get('randomize_comments', True),

            auto_like=config.get('actions', {}).get('auto_like', False),
            auto_subscribe=config.get('actions', {}).get('auto_subscribe', False),
            use_emojis=config.get('actions', {}).get('use_emojis', True),

            clear_cookies=config.get('browser_behavior', {}).get('clear_cookies', True),
            clear_history=config.get('browser_behavior', {}).get('clear_history', True),
            block_images=config.get('browser_behavior', {}).get('block_images', False),

            video_quality=config.get('video', {}).get('quality', 'auto'),
            autoplay=config.get('video', {}).get('autoplay', True),
            mute_video=config.get('video', {}).get('mute', False),

            max_daily_comments=config.get('safety', {}).get('max_daily_comments', 100),
            max_daily_likes=config.get('safety', {}).get('max_daily_likes', 50),
            max_daily_subscribes=config.get('safety', {}).get('max_daily_subscribes', 10)
        )

# Rest of the Bot class implementation follows...