"""Async Browser Lifecycle Manager (Singleton Pattern)."""

import os
import subprocess
from playwright.async_api import async_playwright, Browser, Playwright

from config.settings import DEFAULT_DEBUG_PORT, PROFILE_DIR
from src.stealth import (
    _find_chrome_binary,
    _kill_existing_chrome,
    _wait_for_port,
    _load_fingerprint,
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

    def _create_proxy_auth_extension(self, proxy_url: str) -> str:
        """Create a temporary Chrome extension to handle proxy authentication."""
        import shutil
        from urllib.parse import urlparse

        try:
            parsed = urlparse(proxy_url)
            username = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port

            if not username or not password:
                return None

            ext_dir = os.path.join(PROFILE_DIR, "proxy_auth_ext")
            if os.path.exists(ext_dir):
                shutil.rmtree(ext_dir)

            os.makedirs(ext_dir, exist_ok=True)

            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

            background_js = f"""
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{host}",
                        port: parseInt({port})
                    }},
                    bypassList: ["localhost"]
                }}
            }};

            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            function callbackFn(details) {{
                return {{
                    authCredentials: {{
                        username: "{username}",
                        password: "{password}"
                    }}
                }};
            }}

            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """

            with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
                f.write(manifest_json)
            with open(os.path.join(ext_dir, "background.js"), "w") as f:
                f.write(background_js)

            return ext_dir
        except Exception as e:
            print(f"Error creating proxy extension: {e}")
            return None

    async def start(self, headless: bool = True, proxy_url: str = None):
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

        if proxy_url:
            ext_path = self._create_proxy_auth_extension(proxy_url)
            if ext_path:
                print(f"🔒 Using Proxy Extension: {proxy_url.split('@')[1]}")
                args.append(f"--load-extension={ext_path}")
            else:
                # Simple fallback
                args.append(f"--proxy-server={proxy_url}")

        if headless:
            args.insert(1, "--headless=new")

        # 3. Launch Process
        self.chrome_proc = subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
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
            except Exception:
                self.chrome_proc.kill()
