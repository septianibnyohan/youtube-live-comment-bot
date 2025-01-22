"""
YouTube bot implementation for YouTube Live Comment Bot.
"""

import logging
import random
import time
from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..core.config import Config

logger = logging.getLogger(__name__)


class YouTubeBot:
    """YouTube automation bot."""

    def __init__(self, config: Config):
        """Initialize YouTube bot.

        Args:
            config: Bot configuration.
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.running = False
        self.paused = False

    def start(self) -> None:
        """Start the bot."""
        if self.running:
            return

        self._setup_driver()
        self.running = True
        logger.info("YouTube bot started")

    def stop(self) -> None:
        """Stop the bot."""
        self.running = False
        self._cleanup()
        logger.info("YouTube bot stopped")

    def pause(self) -> None:
        """Pause bot operations."""
        self.paused = True
        logger.info("YouTube bot paused")

    def resume(self) -> None:
        """Resume bot operations."""
        self.paused = False
        logger.info("YouTube bot resumed")

    def _setup_driver(self) -> None:
        """Setup and configure webdriver."""
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

            # Create driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.browser.page_load_timeout)

        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise

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

    def get_status(self) -> Dict[str, Any]:
        """Get bot status.

        Returns:
            dict: Bot status information.
        """
        return {
            'running': self.running,
            'paused': self.paused,
            'url': self.current_url,
            'is_live': self.is_live() if self.running else False,
        }