"""Core business logic for reCAPTCHA v3 automation.

This module acts as the Single Source of Truth for test execution logic.
It decouples the 'what to do' (test steps) from the 'how to run it' (single run vs scaled run).
"""

from config.settings import GOOGLE_URL, TARGET_URL
import random
from datetime import datetime
from playwright.sync_api import Page

from .human import random_mouse_movements, random_scroll, human_click
from .interceptor import TokenInterceptor
from .extractor import parse_recaptcha_response


def solve_recaptcha(page: Page) -> dict:
    """
    Executes the standard reCAPTCHA v3 solving flow on the given page.

    Flow:
    1. Setup Token Interceptor
    2. Google Warm-up (Trust Building)
    3. Navigate to Target
    4. Simulate Human Behavior
    5. Click & Extract Result

    Returns:
        dict: The result object containing score, success status, token, etc.
    """
    result = {
        "success": False,
        "score": 0.0,
        "token": None,
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # 1. Setup Interceptor
        interceptor = TokenInterceptor()
        interceptor.attach(page, TARGET_URL)

        # 2. Warm-up (Critical for 0.7-0.9 scores)
        _perform_warmup(page)

        # 3. Navigate to Target
        print("  -> Navigating to target...")
        page.goto(TARGET_URL, wait_until="load", timeout=60000)

        # 4. Human Simulation
        _simulate_human_behavior(page)

        # 5. Interaction & Extraction
        human_click(page, "#btn")

        _wait_for_result(page)

        raw_json = page.inner_text("#out")
        extracted_data = parse_recaptcha_response(raw_json)

        result.update(
            {
                "success": extracted_data.get("success", False),
                "score": extracted_data.get("score", 0.0),
                "token": interceptor.token[:20],
            }
        )

        print(f"  ✅ Score: {result['score']} | Success: {result['success']}")

    except Exception as e:
        result["error"] = str(e)
        print(f"  ❌ Error: {e}")

    return result


def _perform_warmup(page: Page):
    """Visit Google to establish a trusted session context."""
    try:
        print("  -> Warming up on Google...")
        # Randomize timeout slightly to avoid exact pattern detection
        page.goto(GOOGLE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(random.randint(800, 1500))
        random_mouse_movements(page, count=2)
    except Exception as e:
        print(f"  ⚠️  Warm-up failed (non-critical): {e}")


def _simulate_human_behavior(page: Page):
    """Perform random mouse movements and scrolls to mimic a user."""
    random_mouse_movements(page, count=3)
    random_scroll(page)
    # Dwell time: 2.0s - 3.5s is the sweet spot for v3
    page.wait_for_timeout(random.randint(2000, 3500))


def _wait_for_result(page: Page):
    """Wait for the #out element to contain valid JSON."""
    page.wait_for_function(
        """() => {
            const el = document.getElementById('out');
            if (!el || !el.textContent) return false;
            try { JSON.parse(el.textContent); return true; }
            catch { return false; }
        }""",
        timeout=20000,
    )
