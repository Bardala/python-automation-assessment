"""Scaled Test Runner — Automates multiple reCAPTCHA v3 attempts to verify stealth consistency."""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# Add root to path so we can import src
sys.path.append(os.path.dirname(__file__))

from src.main import TARGET_URL, OUTPUT_DIR, parse_recaptcha_response
from src.stealth import create_stealth_persistent
from src.interceptor import TokenInterceptor
from src.human import random_mouse_movements, random_scroll, human_click

def run_single_attempt(headless=True, proxy=None):
    """Executes a single reCAPTCHA solving cycle and returns results."""
    browser, page, pw, chrome_proc = create_stealth_persistent(headless=headless, proxy=proxy)
    result = {"success": False, "score": 0, "token": None, "error": None}

    try:
        interceptor = TokenInterceptor()
        interceptor.attach(page, TARGET_URL)

        # Navigate directly to target URL for maximum speed
        page.goto(TARGET_URL, wait_until="load", timeout=20000)

        # Minimal human behavior for scale
        random_mouse_movements(page, count=3)
        random_scroll(page)
        # reCAPTCHA v3 likes at least 2-3 seconds on page, but let's cut 2s to 1s
        page.wait_for_timeout(2000)

        human_click(page, "#btn")

        # Wait for result
        page.wait_for_function(
            """() => {
                const el = document.getElementById('out');
                if (!el || !el.textContent) return false;
                try { JSON.parse(el.textContent); return true; }
                catch { return false; }
            }""",
            timeout=15000,
        )

        raw_json = page.inner_text("#out")
        extracted = parse_recaptcha_response(raw_json)
        
        result["success"] = extracted.get("success", False)
        result["score"] = extracted.get("score", 0)
        result["token"] = interceptor.token
        result["timestamp"] = datetime.now().isoformat()

    except Exception as e:
        result["error"] = str(e)
    finally:
        try:
            browser.close()
            chrome_proc.terminate()
            chrome_proc.wait(timeout=2)
            pw.stop()
        except:
            pass

    return result

def main():
    parser = argparse.ArgumentParser(description="Scaled reCAPTCHA v3 test")
    parser.add_argument("--count", type=int, default=250, help="Number of iterations")
    parser.add_argument("--headed", action="store_true", default=True, help="Run in headed mode (default)")
    parser.add_argument("--headless", action="store_false", dest="headed", help="Run in headless mode")
    args = parser.parse_args()
    
    count = args.count
    print(f"🚀 Starting scaled test: {count} iterations")
    print(f"📊 Target: 100% success, at least 15% scores >= 0.9")
    
    results = []
    scores = []
    
    start_time = time.time()
    
    for i in range(1, count + 1):
        print(f"\n🔄 Attempt {i}/{count}...")
        res = run_single_attempt(headless=not args.headed)
        results.append(res)
        
        if res["error"]:
            print(f"❌ Failed: {res['error']}")
        else:
            scores.append(res["score"])
            print(f"✅ Score: {res['score']} | Success: {res['success']}")

        # Save incremental results every 5 iterations
        if i % 5 == 0 or i == count:
            summary = {
                "total": i,
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "high_scores_0.9": len([s for s in scores if s >= 0.9]),
                "high_score_pct": (len([s for s in scores if s >= 0.9]) / i) * 100
            }
            print(f"\n📈 Progress: {i}/{count} | Avg {summary['avg_score']:.2f} | 0.9 hits: {summary['high_scores_0.9']} ({summary['high_score_pct']:.1f}%)")
            
            output_file = os.path.join(OUTPUT_DIR, "scaled_test_progress.json")
            with open(output_file, "w") as f:
                json.dump({"summary": summary, "results": results}, f, indent=2)

    end_time = time.time()
    duration = end_time - start_time
    
    final_summary = {
        "total_attempts": count,
        "successful_solves": len([r for r in results if r["success"]]),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "high_score_count": len([s for s in scores if s >= 0.9]),
        "high_score_pct": (len([s for s in scores if s >= 0.9]) / count) * 100,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }

    print("\n" + "="*50)
    print("🏁 SCALED TEST COMPLETE")
    print("="*50)
    print(f"Average Score: {final_summary['average_score']:.2f}")
    print(f"0.9 Score Count: {final_summary['high_score_count']} ({final_summary['high_score_pct']:.1f}%)")
    print(f"Success Rate: {(final_summary['successful_solves']/count)*100:.1f}%")
    print(f"Total Time: {duration/60:.1f} minutes")
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(OUTPUT_DIR, f"results_scaled_{timestamp_str}.json")
    with open(final_path, "w") as f:
        json.dump({"summary": final_summary, "results": results}, f, indent=2)
    
    print(f"Final report saved to: {final_path}")

if __name__ == "__main__":
    main()
