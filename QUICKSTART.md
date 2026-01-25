# Quickstart Guide - Todo App Backend

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Clone the Repository (Optional)
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist, install the required packages:
```bash
pip install fastapi uvicorn sqlmodel python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv psycopg2-binary alembic
```

### 4. Environment Configuration
Create a `.env` file in the project root directory with the following variables:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TESTING=false
LOG_LEVEL=INFO
```

### 5. Database Setup
Run database migrations:
```bash
alembic upgrade head
```

Or initialize the database tables:
```bash
python -c "from backend.src.database.database import create_db_and_tables; create_db_and_tables()"
```

### 6. Run the Application
```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Usage

### Authentication
Most endpoints require authentication. Include an Authorization header with a valid JWT token:
```
Authorization: Bearer <jwt-token>
```

### Available Endpoints

#### Task Management
- `POST /api/{user_id}/tasks` - Create a new task
  ```json
  {
    "title": "Task title (max 100 chars)",
    "description": "Optional description"
  }
  ```

- `GET /api/{user_id}/tasks` - Get all tasks for a user
  - Query params: `limit`, `offset`, `completed`

- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task

- `PUT /api/{user_id}/tasks/{task_id}` - Update a task
  ```json
  {
    "title": "Updated title",
    "description": "Updated description",
    "completed": false
  }
  ```

- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Update completion status
  ```json
  {
    "completed": true
  }
  ```

- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task (soft delete)

## Running Tests

### Unit Tests
```bash
python -m pytest tests/unit/
```

### All Tests (with test database)
```bash
TESTING=true python -m pytest tests/
```

## Configuration Options

- `LOG_LEVEL`: Set to DEBUG, INFO, WARNING, or ERROR (default: INFO)
- `TESTING`: Set to true to use in-memory SQLite database for tests (default: false)
- `DATABASE_URL`: PostgreSQL connection string for production

## Troubleshooting

### Common Issues
1. **Database Connection Error**: Verify your DATABASE_URL in the .env file
2. **Module Import Error**: Ensure all dependencies are installed with pip
3. **Port Already in Use**: Change the port in the uvicorn command

### For Development
- Use `--reload` flag to auto-reload on code changes
- Set LOG_LEVEL to DEBUG for more detailed logs