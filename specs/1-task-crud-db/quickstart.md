# Quickstart Guide: Todo App Phase II - Task CRUD & Database Integration

## Prerequisites
- Python 3.11+
- Neon PostgreSQL database account
- Better Auth configured for JWT handling
- pip and virtual environment support

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file with the following:
```env
DATABASE_URL=<your-neon-postgres-connection-string>
SECRET_KEY=<your-secret-key-for-jwt>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days in minutes
```

### 5. Run Database Migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Start the Application
```bash
uvicorn backend.src.main:app --reload --port 8000
```

## API Usage Examples

### Create a Task
```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "description": "This is a sample task"}'
```

### Get All Tasks for a User
```bash
curl -X GET http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Update a Task
```bash
curl -X PUT http://localhost:8000/api/{user_id}/tasks/{task_id} \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task Title", "completed": true}'
```

### Mark Task as Complete
```bash
curl -X PATCH http://localhost:8000/api/{user_id}/tasks/{task_id}/complete \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a Task (Soft Delete)
```bash
curl -X DELETE http://localhost:8000/api/{user_id}/tasks/{task_id} \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Integration Tests
```bash
pytest tests/integration/
```

### Run Contract Tests
```bash
pytest tests/contract/
```

## Development Workflow

1. **Database Changes**: Update models in `backend/src/models/`, then run `alembic revision --autogenerate -m "Description"` followed by `alembic upgrade head`
2. **API Changes**: Update schemas in `backend/src/schemas/` and routes in `backend/src/api/`
3. **Validation**: Ensure all changes maintain backward compatibility with existing contracts
4. **Testing**: Run all relevant test suites before committing changes