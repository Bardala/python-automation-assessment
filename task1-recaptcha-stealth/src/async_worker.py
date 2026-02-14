"""Async Worker Logic - The Brain of Parallel Execution."""

import asyncio
import random
import time
from datetime import datetime

from playwright.async_api import BrowserContext, Page
from playwright_stealth import Stealth

from config.settings import TARGET_URL, GOOGLE_URL, NAV_TIMEOUT, WARMUP_TIMEOUT
from config.logging_config import setup_logger
from src.helpers.stealth import _build_stealth, _extra_fingerprint_script, _load_fingerprint
from src.helpers.async_human import random_mouse_movements, random_scroll, human_click
from src.helpers.extractor import parse_recaptcha_response

logger = setup_logger(__name__)

async def run_async_test(context: BrowserContext, iteration: int) -> dict:
    """Executes one full reCAPTCHA test in an isolated context asynchronously."""
    
    page = await context.new_page()
    fp = _load_fingerprint()
    
    # 1. Apply Stealth (Async Safe)
    stealth = _build_stealth(fp)
    await stealth.apply_stealth_async(page)
    
    extra_script = _extra_fingerprint_script(fp)
    if extra_script:
        await page.add_init_script(extra_script)

    result = {
        "iteration": iteration,
        "success": False,
        "score": 0.0,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }

    try:
        # 2. Setup Token Capture
        token_future = asyncio.Future()
        
        async def handle_route(route):
            req = route.request
            if req.method == "POST" and "token" in str(req.post_data):
                # Simplified extraction for async speed
                try:
                    import re
                    match = re.search(r'name="token"\r?\n\r?\n(.+?)(?:\r?\n--)', req.post_data, re.DOTALL)
                    if match and not token_future.done():
                        token_future.set_result(match.group(1).strip())
                except:
                   pass
            await route.continue_()

        await page.route(TARGET_URL, handle_route)

        # 3. Warm-up (Async)
        try:
            # logger.info(f"[{iteration}] Warming up...")
            await page.goto(GOOGLE_URL, wait_until="domcontentloaded", timeout=WARMUP_TIMEOUT)
            await page.wait_for_timeout(random.randint(800, 1500))
            await random_mouse_movements(page, count=2)
        except Exception:
            pass # Non-critical

        # 4. Navigate to Target
        logger.info(f"[{iteration}] Navigating...")
        await page.goto(TARGET_URL, wait_until="load", timeout=NAV_TIMEOUT)

        # 5. Human Simulation
        await random_mouse_movements(page, count=3)
        await random_scroll(page)
        await page.wait_for_timeout(random.randint(2000, 3500))

        # 6. Click & Extract
        await human_click(page, "#btn")
        
        # Wait for results
        await page.wait_for_function(
            "() => document.getElementById('out') && document.getElementById('out').textContent.includes('{')"
        )
        
        raw_json = await page.inner_text("#out")
        data = parse_recaptcha_response(raw_json)
        
        if not token_future.done():
            token_future.set_result(None)
            
        token = await token_future

        result.update({
            "success": data.get("success", False),
            "score": data.get("score", 0.0),
            "token": token
        })
        
        logger.info(f"[{iteration}] ✅ Score: {result['score']}")

    except Exception as e:
        logger.error(f"[{iteration}] ❌ Error: {e}")
        result["error"] = str(e)
    finally:
        await page.close()
        
    return result
