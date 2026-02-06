from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid
from ..models.task_model import Task
from ..models.user_model import User
from ..schemas.task_schemas import (
    TaskCreate, TaskUpdate, TaskCompleteUpdate, TaskResponse, TaskListResponse
)
from ..schemas.response_schemas import ErrorResponse
from ..database.session import get_session
from ..auth.auth_handler import get_current_user
from ..api.deps import verify_user_access
from ..api.auth_deps import verify_user_access as new_verify_user_access
from ..exceptions.auth_exceptions import UserMismatchException

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str,
    task_create: TaskCreate,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert user_id to UUID
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid user ID format").dict()
        )

    # Create task instance
    task = Task(
        title=task_create.title,
        description=task_create.description,
        user_id=user_uuid
    )

    # Add to database
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.get("/tasks", response_model=TaskListResponse)
def get_tasks(
    user_id: str,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    completed: bool = Query(None)
):
    """
    Retrieve all tasks for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert user_id to UUID
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid user ID format").dict()
        )

    # Build query with filters
    query = select(Task).where(Task.user_id == user_uuid, Task.deleted == False)

    if completed is not None:
        query = query.where(Task.completed == completed)

    # Count total before applying limit/offset
    total_query = select(Task).where(Task.user_id == user_uuid, Task.deleted == False)
    if completed is not None:
        total_query = total_query.where(Task.completed == completed)

    # Use scalar to get count from SQL COUNT(*) function
    total = db.scalar(select(func.count()).select_from(total_query.subquery()))

    # Apply pagination
    query = query.offset(offset).limit(limit)
    tasks = db.exec(query).all()

    # Convert to response format
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return TaskListResponse(
        tasks=task_responses,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user and is not deleted
    if task.user_id != user_uuid or task.deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to access this task").dict()
        )

    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Update a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user and is not deleted
    if task.user_id != user_uuid or task.deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to update this task").dict()
        )

    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def update_task_completion(
    user_id: str,
    task_id: str,
    task_complete_update: TaskCompleteUpdate,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Toggle or set the completion status of a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user and is not deleted
    if task.user_id != user_uuid or task.deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to update this task").dict()
        )

    # Update completion status
    if task_complete_update.completed is not None:
        task.completed = task_complete_update.completed
    else:
        # Toggle current status if not specified
        task.completed = not task.completed

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Mark a specific task as deleted (soft delete) for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user
    if task.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to delete this task").dict()
        )

    # Perform soft delete
    task.deleted = True
    db.add(task)
    db.commit()

    return