"""
Main Entry Point for reCAPTCHA v3 Stealth Automation.

Execute a single test run using the centralized logic in src/core.py.
"""

import argparse
import json
import os
import sys

# Ensure src is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core import solve_recaptcha
from src.stealth import create_stealth_persistent

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run(headless: bool = False, proxy: str | None = None):
    """
    Run a single reCAPTCHA test cycle.
    """
    print(f"🚀 Starting Single Run (Focus: {headless and 'Headless' or 'Headed'})")

    # 1. Initialize Browser
    browser, page, pw, chrome_proc = create_stealth_persistent(
        headless=headless, 
        proxy=proxy
    )

    try:
        # 2. Execute Core Logic (The Single Source of Truth)
        result = solve_recaptcha(page)

        # 3. Output Results
        print("\n" + "="*40)
        print(f"✅ Final Score: {result['score']}")
        print(f"✅ Success: {result['success']}")
        if result['token']:
            print(f"✅ Token: {result['token'][:40]}...")
        else:
            print("⚠️  No token captured")
        print("="*40)

        # 4. Save to File
        timestamp = result.get("timestamp", "").replace(":", "-").replace(".", "-")
        filename = f"result_single_{timestamp}.json"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"📄 Result saved to: {output_path}")

    finally:
        # 5. Cleanup
        browser.close()
        chrome_proc.terminate()
        chrome_proc.wait()
        pw.stop()
        print("🏁 Browser Session Closed")

def main():
    parser = argparse.ArgumentParser(description="reCAPTCHA v3 Single Run")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    parser.add_argument("--proxy", type=str, help="Proxy URL")
    args = parser.parse_args()

    run(headless=args.headless, proxy=args.proxy)

if __name__ == "__main__":
    main()
