"""Main automation runner — orchestrates stealth browser, human behavior, and extraction."""

import json
import os

from .stealth import create_stealth_persistent
from .interceptor import TokenInterceptor
from .extractor import parse_recaptcha_response
from .human import random_mouse_movements, random_scroll, human_click

TARGET_URL = "https://cd.captchaaiplus.com/recaptcha-v3-2.php"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    browser, page, pw, chrome_proc = create_stealth_persistent(headless=False)

    try:
        # Set up token interception before target navigation
        interceptor = TokenInterceptor()
        interceptor.attach(page, TARGET_URL)

        # Warm up Google cookies
        print("Warming up Google cookies...")
        page.goto("https://www.google.com", wait_until="networkidle")
        page.wait_for_timeout(2000)
        random_mouse_movements(page, count=3)

        print("Navigating to target URL...")
        page.goto(TARGET_URL, wait_until="networkidle")
        print("Page loaded successfully.")

        # Simulate human behavior — spend time on page
        print("Simulating human behavior...")
        random_mouse_movements(page, count=10)
        random_scroll(page)
        random_mouse_movements(page, count=5)

        # Dwell on page — reCAPTCHA v3 monitors time-on-page
        page.wait_for_timeout(3000)

        # Click the button with human-like timing
        print("Clicking button...")
        human_click(page, "#btn")

        # Wait for JSON to appear in #out
        page.wait_for_function(
            """() => {
                const el = document.getElementById('out');
                if (!el || !el.textContent) return false;
                try { JSON.parse(el.textContent); return true; }
                catch { return false; }
            }""",
            timeout=15000,
        )

        # Extract results from the DOM
        print("Extracting results...")
        raw_json = page.inner_text("#out")
        result = parse_recaptcha_response(raw_json)
        result["token"] = interceptor.token

        # Print results
        print(f"✅ Score: {result['score']}")
        print(f"✅ Success: {result['success']}")
        if result["token"]:
            print(f"✅ Token (first 50 chars): {result['token'][:50]}...")
        else:
            print("⚠️  Token not intercepted")

        # Persist to file
        output_path = os.path.join(OUTPUT_DIR, "result.json")
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {output_path}")

        page.wait_for_timeout(1000)

    finally:
        browser.close()
        chrome_proc.terminate()
        chrome_proc.wait()
        pw.stop()
        print("Browser closed.")


if __name__ == "__main__":
    run()
