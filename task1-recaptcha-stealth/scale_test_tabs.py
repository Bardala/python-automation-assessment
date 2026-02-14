"""Tab-based Scaled Test Runner — Opens browser once, cycles through tabs for speed & persistence."""

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
from src.stealth import create_stealth_persistent
from src.main import OUTPUT_DIR, parse_recaptcha_response

def main():
    parser = argparse.ArgumentParser(description="Tab-based Scaled reCAPTCHA v3 test (Unified)")
    parser.add_argument("--count", type=int, default=10, help="Number of iterations")
    parser.add_argument("--headed", action="store_true", default=True, help="Run in headed mode")
    parser.add_argument("--headless", action="store_false", dest="headed", help="Run in headless mode")
    args = parser.parse_args()
    
    count = args.count
    print(f"🚀 Starting tab-based scaled test: {count} iterations")
    
    # Start browser ONCE
    browser, current_page, pw, chrome_proc = create_stealth_persistent(headless=not args.headed)
    context = browser.contexts[0]
    
    try:
        results = []
        scores = []
        start_time = time.time()
        
        for i in range(1, count + 1):
            print(f"\n🔄 Attempt {i}/{count}...")
            
            # Use 'solve_recaptcha' (The SSOT)
            # This function returns a fully processed result dict
            attempt_result = solve_recaptcha(current_page)
            
            # Augment result with timestamp
            attempt_result["iteration"] = i
            attempt_result["timestamp"] = datetime.now().isoformat()
            
            scores.append(attempt_result["score"])
            results.append(attempt_result)
            
            print(f"  ✅ Score: {attempt_result['score']} | Success: {attempt_result.get('success', False)}")

            # Prepare next tab if not last run
            if i < count:
                print("  -> Closing current tab and opening new one...")
                old_page = current_page
                current_page = context.new_page()
                old_page.close()
                time.sleep(1) # Small cooldown for Chrome protocol

            # Save progress every 5
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
    pct_09 = (high_09/i) * 100
    print(f"  📈 Progress: {i}/{count} | 0.9 Scores: {high_09} ({pct_09:.1f}%)")
    
    summary = {
        "total": i,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "high_scores_0.9": high_09,
        "high_score_pct": pct_09
    }
    output_file = os.path.join(OUTPUT_DIR, "tab_test_progress.json")
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
    print("🏁 TAB-BASED TEST COMPLETE")
    print("="*50)
    print(f"Average Score: {final_summary['average_score']:.2f}")
    print(f"0.9 Score Count: {final_summary['high_score_count']} ({final_summary['high_score_pct']:.1f}%)")
    print(f"Total Time: {duration/60:.1f} minutes")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(OUTPUT_DIR, f"results_tabs_{timestamp}.json")
    with open(final_path, "w") as f:
        json.dump({"summary": final_summary, "results": results}, f, indent=2)
    print(f"Final report saved to: {final_path}")

if __name__ == "__main__":
    main()
