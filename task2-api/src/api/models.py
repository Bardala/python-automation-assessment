from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from core.state import JobStatus

class TaskInput(BaseModel):
    url: HttpUrl
    # Optional parameters for future extensibility (e.g. proxy, headers)
    # matching the "System Design" requirement for flexibility
    params: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: JobStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
