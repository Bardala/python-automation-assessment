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

    def _load_proxies(self):
        try:
            proxy_file = os.path.join(os.path.dirname(__file__), "proxies.txt")
            if not os.path.exists(proxy_file):
                print(f"⚠️ Proxy file not found at {proxy_file}, using direct connection.")
                return [None]
            with open(proxy_file) as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if not proxies:
                 print("⚠️ Proxy file is empty, using direct connection.")
                 return [None]
            return proxies
        except Exception as e:
            print(f"⚠️ Error loading proxies: {e}")
            return [None]

    async def _validate_proxy(self, proxy):
        """Checks if a proxy is alive using curl (matching user's manual test)."""
        if not proxy: return True
        try:
            print(f"🔎 Validating {proxy.split('@')[1]}...")
            proc = await asyncio.create_subprocess_exec(
                "curl", "--max-time", "5", "-I", "-x", proxy, "https://www.google.com",
                stdout=asyncio.subprocess.DEVNULL, 
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            return proc.returncode == 0
        except Exception as e:
            print(f"⚠️ Validation Error: {e}")
            return False

    async def run(self):
        proxies = self._load_proxies()
        total_proxies = len(proxies)
        
        # Calculate distribution: split runs evenly among proxies
        if total_proxies > 0:
            runs_per_proxy = (self.count // total_proxies)
            remainder = self.count % total_proxies
        else:
             runs_per_proxy = self.count
             remainder = 0

        print(f"🚀 Starting Async Test: {self.count} tasks")
        print(f"🔄 Proxy Configuration: {total_proxies} proxies available")
        
        start_global = time.time()
        results = []
        
        task_id = 1
        
        for p_idx, proxy in enumerate(proxies):
            if task_id > self.count:
                break
                
            # Distribute remainder to first few proxies
            current_batch_size = runs_per_proxy + (1 if p_idx < remainder else 0)
            
            if current_batch_size <= 0:
                continue

            proxy_display = proxy.split('@')[1] if proxy and '@' in proxy else (proxy or "Direct")
            print(f"\n🌐 [Proxy {p_idx+1}/{total_proxies}] {proxy_display} | Batch: {current_batch_size} runs")
            
            # Validate before launch
            is_valid = await self._validate_proxy(proxy)
            if not is_valid:
                print(f"❌ Proxy {proxy_display} failed validation (curl). Skipping.")
                continue

            # Restart browser for each proxy to clear state and apply new proxy settings
            try:
                await self.browser_manager.stop()
                # For reCAPTCHA v3, headed mode is often required for 0.9 scores
                await self.browser_manager.start(headless=False, proxy_url=proxy)

                # Create tasks for this batch
                batch_tasks = []
                for _ in range(current_batch_size):
                     batch_tasks.append(self._worker(task_id))
                     task_id += 1
                
                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)

            except Exception as e:
                print(f"❌ Proxy Batch Failed: {e}")
            
        # Cleanup
        await self.browser_manager.stop()
        duration = time.time() - start_global
        
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
