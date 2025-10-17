#!/usr/bin/env python3
"""
Selenium-based Telegram Web Launcher and Scraper (bootstrap)
===========================================================
- Launches Telegram Web login page reliably
- Supports Chrome or Firefox, profile persistence, headless mode, and proxy
- Prepares environment for subsequent scraping steps

Note: Member extraction is intentionally minimal here; the first milestone is a
robust launch + login preparation so the user can authenticate interactively.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Optional
import os
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
except Exception:
    # Will be surfaced by check_selenium_requirements
    webdriver = None  # type: ignore
    By = None  # type: ignore
    WebDriverWait = None  # type: ignore
    EC = None  # type: ignore
    TimeoutException = Exception  # type: ignore
    WebDriverException = Exception  # type: ignore

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

TELEGRAM_WEB_URL = "https://web.telegram.org/k/"


def setup_selenium_driver(profile_dir: Optional[str] = None,
                          headless: bool = False,
                          proxy_url: Optional[str] = None):
    """Create a Selenium WebDriver for Chrome or Firefox.

    Prefers Chrome/Chromium if available (chromedriver), otherwise falls back to Firefox (geckodriver).
    """
    if webdriver is None:
        raise RuntimeError("selenium is not installed")

    # Try Chrome/Chromium first
    driver = None
    chrome_error = None
    try:
        chrome_options = ChromeOptions()
        # Avoid automation banners
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if headless:
            chrome_options.add_argument("--headless=new")
        if profile_dir:
            chrome_options.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
        if proxy_url:
            chrome_options.add_argument(f"--proxy-server={proxy_url}")
        # Service: let Selenium locate chromedriver if available in PATH
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        chrome_error = e
        driver = None

    if driver is None:
        # Fallback to Firefox
        try:
            ff_options = FirefoxOptions()
            if headless:
                ff_options.add_argument("-headless")
            # Firefox profile
            if profile_dir and os.path.isdir(profile_dir):
                ff_options.set_preference("profile", os.path.abspath(profile_dir))
            # Proxy
            if proxy_url:
                # Expect proxy_url like socks5://host:port or http://host:port
                from urllib.parse import urlparse
                pu = urlparse(proxy_url)
                if pu.scheme in ("http", "https"):
                    ff_options.set_preference("network.proxy.type", 1)
                    ff_options.set_preference("network.proxy.http", pu.hostname)
                    ff_options.set_preference("network.proxy.http_port", int(pu.port or 80))
                elif pu.scheme.startswith("socks"):
                    ff_options.set_preference("network.proxy.type", 1)
                    ff_options.set_preference("network.proxy.socks", pu.hostname)
                    ff_options.set_preference("network.proxy.socks_port", int(pu.port or 1080))
            driver = webdriver.Firefox(options=ff_options)
        except Exception as ff_e:
            raise RuntimeError(f"Failed to create WebDriver. Chrome error: {chrome_error}; Firefox error: {ff_e}")

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    return driver


def wait_for_telegram_loaded(driver, timeout: int = 60) -> bool:
    """Wait until Telegram Web app shell is loaded or login screen is visible."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.url_contains("web.telegram.org/k"),
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="auth-qr"]')),  # QR login box
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="tg_head"]')),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]')),
            )
        )
        return True
    except TimeoutException:
        return False


def ensure_logged_in_prompt(driver) -> None:
    """If not logged in, ensure we're on the login page with QR/SMS options visible."""
    try:
        # If URL diverged, navigate back to Telegram Web root
        if "web.telegram.org" not in driver.current_url:
            driver.get(TELEGRAM_WEB_URL)
        # Wait a bit for the login UI
        wait_for_telegram_loaded(driver, timeout=30)
    except Exception:
        pass


def scrape_group_members_via_web(group_url: str,
                                max_members: int = 1000,
                                profile_dir: Optional[str] = None,
                                headless: bool = False,
                                proxy_url: Optional[str] = None) -> List[Dict]:
    """Bootstrap Selenium to Telegram Web and navigate to group/channel if provided.

    Returns an empty list for now; primary goal is to reliably launch and prepare for login/scrape.
    """
    LOGGER.info("Launching Selenium for Telegram Web…")
    driver = setup_selenium_driver(profile_dir=profile_dir, headless=headless, proxy_url=proxy_url)

    try:
        # Open Telegram Web
        driver.get(TELEGRAM_WEB_URL)
        loaded = wait_for_telegram_loaded(driver, timeout=60)
        if not loaded:
            LOGGER.warning("Telegram Web did not signal ready state within timeout")
        ensure_logged_in_prompt(driver)

        # If a target group/channel URL is provided, attempt to navigate after initial load
        if group_url and group_url.strip():
            # If it's a t.me link, open it; Telegram Web will route appropriately
            LOGGER.info(f"Navigating to target: {group_url}")
            driver.get(group_url.strip())
            # Give Telegram time to handle deep link
            wait_for_telegram_loaded(driver, timeout=30)

        # Keep browser open for interactive login unless headless
        if not headless:
            LOGGER.info("Browser launched. Please complete Telegram login if required.")
            # Poll for up to 5 minutes while user logs in; caller may decide to close earlier
            end = time.time() + 300
            while time.time() < end:
                time.sleep(1)
        else:
            # In headless mode we just wait briefly
            time.sleep(3)

        # TODO: Implement actual member extraction post-login
        return []
    except WebDriverException as e:
        LOGGER.error(f"Selenium error: {e}")
        return []
    finally:
        try:
            # Do not close if visible; caller may want to keep it open. Close only in headless mode
            if headless:
                driver.quit()
        except Exception:
            pass


def extract_member_info(member_element) -> Dict:
    """Placeholder for future member extraction."""
    return {
        'username': '',
        'user_id': '',
        'first_name': '',
        'last_name': '',
        'phone': '',
        'status': 'online'
    }


def get_group_info_via_web(group_url: str) -> Dict:
    """Basic placeholder group info."""
    return {
        'title': '',
        'member_count': 0,
        'description': '',
        'type': 'channel'
    }


def check_selenium_requirements() -> bool:
    try:
        import selenium  # noqa: F401
        return True
    except Exception:
        return False
