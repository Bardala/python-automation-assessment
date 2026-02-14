from fastapi import APIRouter, HTTPException, BackgroundTasks
from .models import TaskInput, TaskResponse
from core.state import JobStore, JobStatus, task_queue

router = APIRouter()
job_store = JobStore()

@router.post("/recaptcha/in", response_model=TaskResponse, status_code=202)
async def submit_task(task_input: TaskInput, background_tasks: BackgroundTasks):
    """
    Submits a new scraping task to the queue.
    Returns immediately with a Task ID (Async Processing).
    """
    # 1. Create Job Entry
    task_id = job_store.create_job()
    
    # 2. Push to Queue (In the future: RabbitMQ)
    await task_queue.put(task_id)
    
    return TaskResponse(
        task_id=task_id,
        status=JobStatus.QUEUED
    )

@router.get("/recaptcha/res/{task_id}", response_model=TaskResponse)
async def get_task_result(task_id: str):
    """
    Retrieves the status and result of a submitted task.
    """
    job = job_store.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return TaskResponse(
        task_id=job.task_id,
        status=job.status,
        result=job.result,
        error=job.error
    )
