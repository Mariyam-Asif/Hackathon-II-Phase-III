---
name: backend-skill
description: Generate backend routes, handle requests and responses, and connect to databases for FastAPI applications.
---

# Backend Skill

## Instructions

1. **Route Generation**
   - Implement REST API endpoints for CRUD operations
   - Follow consistent naming and URL conventionsc
   - Organize routes modularly for maintainability

2. **Request/Response Handling**
   - Validate incoming requests using Pydantic models
   - Format responses consistently as JSON
   - Handle errors with proper HTTP status codes
   - Implement authentication and authorization checks where required

3. **Database Integration**
   - Connect endpoints to database models (SQLModel)
   - Perform create, read, update, delete operations securely
   - Ensure transactions maintain data integrity
   - Optimize queries for performance

## Best Practices
- Keep endpoint responsibilities clear and single-purpose
- Use descriptive names for routes and parameters
- Centralize repeated logic (e.g., auth, error handling)
- Validate all inputs and sanitize outputs
- Test endpoints with both valid and invalid data

## Example Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Task, get_db

router = APIRouter()

@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
