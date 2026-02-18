from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class TaskCreate(BaseModel):
    """
    Schema for creating a new task
    - title (required)
    - description (optional)
    - priority (optional, default: medium)
    """
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium")  # low, medium, high, urgent

class TaskUpdate(BaseModel):
    """
    Schema for updating a task
    - title (optional)
    - description (optional)
    - status (optional: pending, in_progress, completed)
    - priority (optional)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None  # pending, in_progress, completed
    priority: Optional[str] = None  # low, medium, high, urgent

class TaskCompleteUpdate(BaseModel):
    """
    Schema for updating task completion status
    """
    completed: bool = True  # Setting to True marks as completed

class TaskResponse(BaseModel):
    """
    Schema for task response (all fields except user_id for security)
    """
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: str  # pending, in_progress, completed
    priority: str  # low, medium, high, urgent
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

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