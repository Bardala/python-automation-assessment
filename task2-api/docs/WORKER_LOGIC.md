# Worker & Automation Logic

The `worker.py` module is the engine of the service. It bridging the gap between HTTP requests and Playwright browser instances.

## Concurrency Management

To prevent system exhaustion, execution is throttled using an `asyncio.Semaphore`.

- **`MAX_CONCURRENT_BROWSERS = 3`**: Limits the number of active browser pages being processed simultaneously. 
- Higher concurrency can be achieved by increasing this limit, depending on host CPU/RAM.

## Browser Lifecycle

- **Shared Browser Instance**: The `AsyncBrowserManager` (from Task 1) maintains a single persistent browser engine to save on startup overhead.
- **Isolated Contexts**: For every task, a new `BrowserContext` is created:
  ```python
  context = await browser_manager.browser.new_context()
  ```
  This ensures there is no cookie or state leakage between separate customer requests.
- **Automatic Cleanup**: Contexts are explicitly closed after completion or failure.

## Integration with Task 1

The system dynamically loads stealth automation logic from the adjacent `task1-recaptcha-stealth` directory. This allows the API to benefit from the latest stealth improvements without code duplication.

**Key Imported Functions:**
- `AsyncBrowserManager`: Handles Chrome CDP connection and stealth flags.
- `run_async_test`: Executes the actual page navigation and token retrieval.

## Robustness

- **Graceful Shutdown**: The `lifespan` handler in `main.py` ensures that the worker is canceled and resources are cleaned up when the server stops.
- **Error Capture**: Exceptions within the worker loop are caught and piped back to the `JobStore`, ensuring the API remains stable even if a specific automation task crashes.
