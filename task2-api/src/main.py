import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from api.routes import router
from core.worker import worker_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch Background Worker
    worker_task = asyncio.create_task(worker_loop())
    yield
    # Shutdown: Cancel worker (Mock graceful shutdown)
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        print("🛑 Worker Shutdown Gracefully")

app = FastAPI(
    title="Stealth Scraping API (Task 2)",
    description="A microservice-ready local API for reCAPTCHA solving.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
