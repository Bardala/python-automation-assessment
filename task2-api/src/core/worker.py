import asyncio
import sys
import os
from contextlib import asynccontextmanager

# Robust module loading to avoid 'src' namespace collision
import importlib.util

TASK1_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../task1-recaptcha-stealth/src"))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

try:
    # Manually load the modules we need from task1
    # This bypasses the vague "from src import..." which is ambiguous
    async_manager_mod = load_module("task1_async_manager", os.path.join(TASK1_SRC, "async_manager.py"))
    async_worker_mod = load_module("task1_async_worker", os.path.join(TASK1_SRC, "async_worker.py"))
    
    AsyncBrowserManager = async_manager_mod.AsyncBrowserManager
    run_async_test = async_worker_mod.run_async_test
    
except Exception as e:
    print(f"CRITICAL: Failed to load task1 modules from {TASK1_SRC}. {e}")
    sys.exit(1)

from .state import JobStore, JobStatus, task_queue

# Limits concurrent browser tabs to prevent system overload
# This mimics "Worker Node Capacity"
MAX_CONCURRENT_BROWSERS = 3
sem = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)

async def worker_loop():
    """Background consumer that pulls from Queue and executes Automation."""
    print("👷 Worker: Started background loop...")
    
    # Initialize Browser Manager (Singleton)
    browser_manager = AsyncBrowserManager()
    try:
        # Ensure browser is running
        await browser_manager.start(headless=False)
        print("👷 Worker: Browser Interface Ready.")
    except Exception as e:
        print(f"👷 Worker FATAL: Failed to start browser: {e}")
        return

    job_store = JobStore()

    while True:
        task_id = await task_queue.get()
        print(f"👷 Worker: Processing Task {task_id}")
        
        job = job_store.get_job(task_id)
        if not job:
            print(f"👷 Worker: Job {task_id} not found in store!")
            task_queue.task_done()
            continue

        job.update(JobStatus.PROCESSING)

        async with sem:
            try:
                # Create a new isolated context for this task
                context = await browser_manager.browser.new_context()
                
                # Execute the Task 1 Logic
                # We pass iteration=1 as this is a single "customer request"
                result = await run_async_test(context, iteration=1)
                
                await context.close()

                if result.get("token"):
                    job.update(JobStatus.COMPLETED, result=result)
                    print(f"👷 Worker: Task {task_id} COMPLETED ✅")
                elif result.get("error"):
                    job.update(JobStatus.FAILED, error=result["error"])
                    print(f"👷 Worker: Task {task_id} FAILED ❌")
                else:
                    # Fallback if no token and no explicit error
                    job.update(JobStatus.FAILED, error="Unknown failure: No token returned")
                    print(f"👷 Worker: Task {task_id} FAILED (No Token)")

            except Exception as e:
                job.update(JobStatus.FAILED, error=str(e))
                print(f"👷 Worker: Task {task_id} CRASHED 💥: {e}")
            finally:
                task_queue.task_done()
