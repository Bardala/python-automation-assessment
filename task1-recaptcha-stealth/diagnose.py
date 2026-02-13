"""Diagnostic: opens real Chrome via CDP with stealth and waits for YOU to click manually.
This isolates whether the low score is due to browser config vs mouse automation."""

import json
import subprocess
import time
import os

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

PROFILE_DIR = os.path.join(os.path.dirname(__file__), ".chrome_profile_diag")
TARGET_URL = "https://cd.captchaaiplus.com/recaptcha-v3-2.php"

stealth = Stealth(
    chrome_runtime=True,
    navigator_platform_override="Linux x86_64",
    navigator_vendor_override="Google Inc.",
)


def main():
    os.makedirs(PROFILE_DIR, exist_ok=True)

    # Launch Chrome cleanly — no --enable-automation
    chrome_proc = subprocess.Popen(
        [
            "/usr/bin/google-chrome",
            "--remote-debugging-port=9333",
            f"--user-data-dir={PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)

    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9333")
    context = browser.contexts[0]
    stealth.apply_stealth_sync(context)
    page = context.pages[0] if context.pages else context.new_page()

    page.goto(TARGET_URL, wait_until="networkidle")
    print("✅ Page loaded — real Chrome via CDP + stealth patches.")
    print("👉 NOW CLICK THE BUTTON MANUALLY IN THE BROWSER!")
    print("   Waiting for JSON result to appear (60s timeout)...")

    page.wait_for_function(
        """() => {
            const el = document.getElementById('out');
            if (!el || !el.textContent) return false;
            try { JSON.parse(el.textContent); return true; }
            catch { return false; }
        }""",
        timeout=60000,
    )

    raw_json = page.inner_text("#out")
    result = json.loads(raw_json)
    score = result.get("google_response", {}).get("score")
    print(f"\n🎯 SCORE: {score}")
    print(f"📋 Full response:\n{json.dumps(result, indent=2)}")

    input("\nPress Enter to close browser...")
    browser.close()
    chrome_proc.terminate()
    chrome_proc.wait()
    pw.stop()


if __name__ == "__main__":
    main()
