"""Scaled Async Test Runner (Concurrent Execution).

Usage:
  python3 task1_recaptcha_stealth/scale_test_async.py --count 50 --concurrency 5
"""

import argparse
import asyncio
import json
import os
import time

from config.settings import OUTPUT_DIR, CONCURRENCY_LIMIT
from src.async_manager import AsyncBrowserManager
from src.async_worker import run_async_test

class AsyncScaler:
    def __init__(self, count: int, concurrency: int = CONCURRENCY_LIMIT):
        self.count = count
        self.concurrency = concurrency
        self.results = []
        self.semaphore = asyncio.Semaphore(concurrency)
        self.browser_manager = AsyncBrowserManager()

    async def _worker(self, iteration: int):
        async with self.semaphore:
            ctx = await self.browser_manager.browser.new_context()
            try:
                result = await run_async_test(ctx, iteration)
                return result
            finally:
                await ctx.close()

    async def run(self):
        print(f"🚀 Starting Async Test: {self.count} tasks (Limit: {self.concurrency})")
        start = time.time()
        
        # 1. Start Browser
        # For reCAPTCHA v3, headed mode is often required for 0.9 scores
        # due to rendering checks (WebGL/Canvas) often failing in headless.
        await self.browser_manager.start(headless=False)
        
        # 2. Create Tasks
        tasks = [self._worker(i) for i in range(1, self.count+1)]
        
        # 3. Gather Results
        # For simplicity, gather all. For 250 tasks, this is fine.
        # For 10k tasks, we would use asyncio.as_completed
        results = await asyncio.gather(*tasks)
        
        # 4. Cleanup
        await self.browser_manager.stop()
        duration = time.time() - start
        
        # 5. Report
        scores = [r.get("score", 0.0) for r in results]
        high_scores = len([s for s in scores if s >= 0.9])
        
        summary = {
            "total": self.count,
            "success": len([r for r in results if r.get("success")]),
            "high_scores": high_scores,
            "pct_0.9": (high_scores/self.count)*100,
            "duration": duration
        }
        
        print(f"\n✅ Completed in {duration:.1f}s")
        print(f"📈 0.9 Scores: {high_scores} ({summary['pct_0.9']:.1f}%)")
        
        with open(os.path.join(OUTPUT_DIR, "results_async.json"), "w") as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    
    scaler = AsyncScaler(args.count, args.concurrency)
    asyncio.run(scaler.run())
