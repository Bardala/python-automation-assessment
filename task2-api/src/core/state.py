import asyncio
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = JobStatus.QUEUED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

    def update(self, status: JobStatus, result: Any = None, error: str = None):
        self.status = status
        self.updated_at = datetime.now()
        if result:
            self.result = result
        if error:
            self.error = error

class JobStore:
    """Singleton In-Memory Database Simulation."""
    _instance = None
    _jobs: Dict[str, Job] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobStore, cls).__new__(cls)
        return cls._instance

    def create_job(self) -> str:
        task_id = str(uuid.uuid4())
        job = Job(task_id)
        self._jobs[task_id] = job
        return task_id

    def get_job(self, task_id: str) -> Optional[Job]:
        return self._jobs.get(task_id)

    def get_all_jobs(self) -> Dict[str, Job]:
        return self._jobs

# Global singleton for the Queue (Simulating RabbitMQ)
# In a real app, this would be a connection pool to a broker.
task_queue: asyncio.Queue = asyncio.Queue()
