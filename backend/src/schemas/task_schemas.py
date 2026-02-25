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
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    deleted: Optional[bool] = None

class TaskCompleteUpdate(BaseModel):
    """
    Schema for updating task completion status
    """
    completed: bool = True

class TaskResponse(BaseModel):
    """
    Schema for task response
    """
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    completed: bool
    deleted: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True

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