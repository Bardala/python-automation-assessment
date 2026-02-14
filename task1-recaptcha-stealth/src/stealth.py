"""Stealth browser configuration — replays recorded real browser fingerprint."""

import json
import os
import subprocess
import time

from playwright.sync_api import sync_playwright, Browser, Page
from playwright_stealth import Stealth

# Paths
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROFILE_DIR = os.path.join(_BASE_DIR, ".chrome_profile")
FINGERPRINT_PATH = os.path.join(_BASE_DIR, "outputs", "fingerprint.json")


from functools import lru_cache

@lru_cache(maxsize=1)
def _load_fingerprint() -> dict | None:
    """Load the recorded fingerprint from outputs/fingerprint.json (Cached)."""
    if os.path.exists(FINGERPRINT_PATH):
        try:
            with open(FINGERPRINT_PATH) as f:
                fp = json.load(f)
                # print("📋 Fingerprint loaded (disk)") # Debug
                return fp
        except Exception:
            pass
    return None


def _build_stealth(fp: dict | None) -> Stealth:
    """Build a Stealth config using recorded fingerprint data."""
    kwargs = {
        "chrome_runtime": True,
        "navigator_webdriver": True,  # Patch webdriver to false
    }

    if fp:
        kwargs["navigator_user_agent_override"] = fp.get("userAgent")
        kwargs["navigator_platform_override"] = fp.get("platform", "Linux x86_64")
        kwargs["navigator_vendor_override"] = fp.get("vendor", "Google Inc.")

        if fp.get("webgl"):
            kwargs["webgl_vendor_override"] = fp["webgl"].get("vendor")
            kwargs["webgl_renderer_override"] = fp["webgl"].get("renderer")

    return Stealth(**kwargs)


def _build_context_options(fp: dict | None) -> dict:
    """Build Playwright context options from recorded fingerprint."""
    opts = {
        "java_script_enabled": True,
        "has_touch": False,
    }

    if fp:
        opts["user_agent"] = fp.get("userAgent")
        opts["locale"] = fp.get("language", "en-US")
        opts["timezone_id"] = fp.get("timezone", "America/New_York")
        opts["device_scale_factor"] = fp.get("devicePixelRatio", 1)

        screen = fp.get("screen", {})
        opts["viewport"] = {
            "width": screen.get("width", 1920),
            "height": screen.get("height", 1080),
        }
        opts["screen"] = {
            "width": screen.get("width", 1920),
            "height": screen.get("height", 1080),
        }
    else:
        opts["user_agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        opts["viewport"] = {"width": 1920, "height": 1080}
        opts["screen"] = {"width": 1920, "height": 1080}
        opts["locale"] = "en-US"
        opts["timezone_id"] = "America/New_York"
        opts["device_scale_factor"] = 1

    return opts


def _extra_fingerprint_script(fp: dict | None) -> str:
    """Generate JS to override properties not covered by playwright-stealth."""
    if not fp:
        return ""

    overrides = []

    # Hardware concurrency
    hc = fp.get("hardwareConcurrency")
    if hc:
        overrides.append(
            f"Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hc}}});"
        )

    # Device memory
    dm = fp.get("deviceMemory")
    if dm:
        overrides.append(
            f"Object.defineProperty(navigator, 'deviceMemory', {{get: () => {dm}}});"
        )

    # Max touch points
    mtp = fp.get("maxTouchPoints", 0)
    overrides.append(
        f"Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {mtp}}});"
    )

    # Languages
    langs = fp.get("languages")
    if langs:
        langs_json = json.dumps(langs)
        overrides.append(
            f"Object.defineProperty(navigator, 'languages', {{get: () => {langs_json}}});"
        )

    return "\n".join(overrides)


def _find_chrome_binary() -> str:
    """Find the system Chrome binary path."""
    for path in [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
    ]:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Google Chrome not found")


def _kill_existing_chrome(debug_port: int) -> None:
    """Kill any existing Chrome process on the debug port and clean up lock files."""
    try:
        # Kill by port
        result = subprocess.run(
            ["lsof", "-ti", f":{debug_port}"],
            capture_output=True, text=True,
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            for pid in pids:
                subprocess.run(["kill", "-9", pid], capture_output=True)

        # Also kill by command-line match
        subprocess.run(
            ["pkill", "-f", f"remote-debugging-port={debug_port}"],
            capture_output=True,
        )
        time.sleep(1)
    except Exception:
        pass

    # Remove stale Chrome profile locks
    for lock_file in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lock_path = os.path.join(PROFILE_DIR, lock_file)
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass


def _wait_for_port(port: int, timeout: float = 10.0) -> bool:
    """Wait until a TCP port is accepting connections."""
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def create_stealth_persistent(headless: bool = False, debug_port: int = 9222, proxy: str | None = None):
    """Launch real Chrome cleanly and connect via CDP with fingerprint replay.

    Args:
        headless: Run in headless mode if True.
        debug_port: Port for Chrome remote debugging.
        proxy: Proxy server URL (e.g., "http://user:pass@host:port").

    Returns:
        Tuple of (Browser, Page, Playwright instance, Chrome subprocess).
    """
    fp = _load_fingerprint()
    if fp:
        print(f"📋 Loaded fingerprint: {fp.get('userAgent', 'N/A')[:60]}...")
    else:
        print("⚠️  No recorded fingerprint found. Run record_fingerprint.py first.")
        print("   Using default values.")

    # Kill any leftover Chrome from a previous run
    _kill_existing_chrome(debug_port)

    chrome_binary = _find_chrome_binary()
    os.makedirs(PROFILE_DIR, exist_ok=True)

    chrome_args = [
        chrome_binary,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-infobars",
        "--disable-dev-shm-usage",
        "about:blank",
    ]

    if proxy:
        chrome_args.append(f"--proxy-server={proxy}")

    if headless:
        chrome_args.insert(1, "--headless=new")

    # Launch Chrome cleanly — NO automation flags, NO pipe (avoids blocking)
    chrome_process = subprocess.Popen(
        chrome_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for debug port to accept connections
    if not _wait_for_port(debug_port, timeout=10):
        chrome_process.terminate()
        raise RuntimeError(
            f"Chrome failed to start on port {debug_port}. "
            "Try killing all Chrome processes: pkill -f google-chrome"
        )

    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")

    # For context-based testing, we might want to manage contexts manually.
    # However, to keep backward compatibility with main.py, we'll try to get the default context.
    try:
        context = browser.contexts[0]
        
        # Apply playwright-stealth with fingerprint overrides
        stealth = _build_stealth(fp)
        # We apply it to the default context, but subsequent contexts need it re-applied manually
        try:
            stealth.apply_stealth_sync(context)
        except Exception as e:
            pass # Ignore if already applied

        # Inject additional fingerprint overrides not covered by stealth
        extra_script = _extra_fingerprint_script(fp)
        if extra_script:
            context.add_init_script(extra_script)

        page = context.pages[0] if context.pages else context.new_page()
    except IndexError:
        # If no context exists (rare with CDP but possible), create one
        context = browser.new_context()
        page = context.new_page()

    return browser, page, pw, chrome_process

