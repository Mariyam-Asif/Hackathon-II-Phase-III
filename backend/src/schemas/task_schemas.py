from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class TaskCreate(BaseModel):
    """
    Schema for creating a new task
    - title (required, max 100 chars)
    - description (optional)
    """
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    """
    Schema for updating a task
    - title (optional, max 100 chars)
    - description (optional)
    - completed (optional)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskCompleteUpdate(BaseModel):
    """
    Schema for updating task completion status
    - completed (optional, if omitted, toggles current status)
    """
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    """
    Schema for task response (all fields except user_id for security)
    """
    id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """
    Schema for multiple tasks response with pagination
    """
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True