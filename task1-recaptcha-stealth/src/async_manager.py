"""Async Browser Lifecycle Manager (Singleton Pattern)."""

import asyncio
import os
import subprocess
from playwright.async_api import async_playwright, Browser, Playwright

from config.settings import DEFAULT_DEBUG_PORT, PROFILE_DIR
from src.helpers.stealth import (
    _find_chrome_binary, _kill_existing_chrome, _wait_for_port, _load_fingerprint
)

class AsyncBrowserManager:
    """Manages the lifecycle of a persistent Chrome process + Async Playwright."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncBrowserManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.browser: Browser | None = None
        self.playwright: Playwright | None = None
        self.chrome_proc: subprocess.Popen | None = None
        self.debug_port = DEFAULT_DEBUG_PORT
        self.fingerprint = _load_fingerprint()
        self.initialized = True

    async def start(self, headless: bool = True):
        """Clean launch real Chrome and connect AsyncPlaywright."""
        if self.browser:
            return self.browser

        # 1. Kill old processes
        _kill_existing_chrome(self.debug_port)
        
        # 2. Prepare Launch Args
        binary = _find_chrome_binary()
        os.makedirs(PROFILE_DIR, exist_ok=True)
        
        args = [
            binary,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "about:blank",
        ]
        
        if headless:
            args.insert(1, "--headless=new")

        # 3. Launch Process
        self.chrome_proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 4. Wait for Port
        if not _wait_for_port(self.debug_port):
            self.stop()
            raise RuntimeError("Chrome failed to start (Async)")

        # 5. Connect Async Playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(
            f"http://127.0.0.1:{self.debug_port}"
        )
        
        return self.browser

    async def stop(self):
        """Cleanup Resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.chrome_proc:
            self.chrome_proc.terminate()
            try:
                self.chrome_proc.wait(timeout=2)
            except:
                self.chrome_proc.kill()
