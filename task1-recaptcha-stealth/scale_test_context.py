"""Context-based Scaled Test Runner — Opens browser once, cycles through CONTEXTS (Incognito-like) for speed & isolation."""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# Add root to path so we can import src
sys.path.append(os.path.dirname(__file__))

# Import SSOT (Single Source of Truth) logic
from src.core import solve_recaptcha
from src.stealth import create_stealth_persistent, _load_fingerprint, _build_stealth, _extra_fingerprint_script
from src.main import OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="Context-based Scaled reCAPTCHA v3 test (Unified)")
    parser.add_argument("--count", type=int, default=100, help="Number of iterations")
    parser.add_argument("--headed", action="store_true", default=True, help="Run in headed mode")
    parser.add_argument("--headless", action="store_false", dest="headed", help="Run in headless mode")
    args = parser.parse_args()
    
    count = args.count
    print(f"🚀 Starting context-based scaled test: {count} iterations")
    
    # 1. Start browser ONCE (Persistent process)
    browser, init_page, pw, chrome_proc = create_stealth_persistent(headless=not args.headed)
    
    # We won't use the initial page for tests, but keep it open to stabilize the CDP session
    # init_page.close() # DO NOT CLOSE

    # Pre-load stealth configuration once
    fp = _load_fingerprint()
    stealth = _build_stealth(fp)
    extra_script = _extra_fingerprint_script(fp)

    results = []
    scores = []
    start_time = time.time()
    
    try:
        for i in range(1, count + 1):
            print(f"\n🔄 Attempt {i}/{count} [Context: New]")
            
            # 2. Create FRESH Context (Clean slate)
            context = browser.new_context()
            
            # Apply Stealth Configuration Manually
            try:
                stealth.apply_stealth_sync(context)
            except Exception:
                pass # Ignore if already applied
            
            if extra_script:
                context.add_init_script(extra_script)
                
            page = context.new_page()
            
            try:
                # 3. Execute Core Logic (The SSOT)
                result = solve_recaptcha(page)
                
                # Augment result
                result["iteration"] = i
                result["timestamp"] = datetime.now().isoformat()
                
                scores.append(result["score"])
                results.append(result)

            finally:
                # 4. Cleanup Context (Reset for next run)
                context.close()

            # Progress Update
            if i % 5 == 0 or i == count:
                _save_progress(i, count, scores, results)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user. Saving partial results...")
    
    finally:
        browser.close()
        chrome_proc.terminate()
        chrome_proc.wait()
        pw.stop()
        
        # Save Final Report
        _save_final_report(count, scores, results, start_time)

def _save_progress(i, count, scores, results):
    """Save incremental progress JSON."""
    high_09 = len([s for s in scores if s >= 0.9])
    pct_09 = (high_09/i) * 100 if i > 0 else 0
    print(f"  📈 Progress: {i}/{count} | 0.9 Scores: {high_09} ({pct_09:.1f}%)")
    
    summary = {
        "total": i,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "high_scores_0.9": high_09,
        "high_score_pct": pct_09
    }
    output_file = os.path.join(OUTPUT_DIR, "context_test_progress.json")
    with open(output_file, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

def _save_final_report(count, scores, results, start_time):
    """Generate and save the comprehensive final report."""
    end_time = time.time()
    duration = end_time - start_time
    
    high_score_count = len([s for s in scores if s >= 0.9])
    score_counts = {}
    for s in scores:
        s_str = str(s)
        score_counts[s_str] = score_counts.get(s_str, 0) + 1

    actual_count = len(results)
    final_summary = {
        "total_attempts": actual_count,
        "successful_solves": len([r for r in results if r.get("success", False)]),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "high_score_count": high_score_count,
        "high_score_pct": (high_score_count / actual_count) * 100 if actual_count > 0 else 0,
        "score_distribution": score_counts,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }

    print("\n" + "="*50)
    print("🏁 CONTEXT-BASED TEST COMPLETE")
    print("="*50)
    print(f"Average Score: {final_summary['average_score']:.2f}")
    print(f"0.9 Score Count: {final_summary['high_score_count']} ({final_summary['high_score_pct']:.1f}%)")
    print(f"Total Time: {duration/60:.1f} minutes")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(OUTPUT_DIR, f"results_context_{timestamp}.json")
    with open(final_path, "w") as f:
        json.dump({"summary": final_summary, "results": results}, f, indent=2)
    print(f"Final report saved to: {final_path}")

if __name__ == "__main__":
    main()
