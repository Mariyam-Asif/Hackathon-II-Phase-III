# Quickstart Guide: Better Auth Integration for Todo Web Application

## Overview
This guide provides essential setup and usage instructions for the Better Auth integration with JWT-based authentication for the Todo App backend API.

## Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- Better Auth configured for frontend
- Environment variables configured with shared secrets
- Existing task management API running

## Setup

### 1. Environment Variables
Create a `.env` file in the backend root with the following:
```bash
# Authentication
BETTER_AUTH_SECRET="your-secret-key-for-jwt-validation"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_DELTA=604800  # 7 days in seconds

# Server Configuration
API_HOST="0.0.0.0"
API_PORT=8000
DEBUG=false
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
# or if using poetry
poetry install
```

## Better Auth Integration

### 1. Frontend Configuration
Configure Better Auth on the frontend with the following settings:
```javascript
// Example Better Auth configuration
const betterAuth = {
  secret: process.env.BETTER_AUTH_SECRET,
  // Additional configuration as needed
};
```

### 2. Token Handling
- Better Auth issues JWT tokens upon successful authentication
- Frontend stores tokens securely (preferably in httpOnly cookies)
- All API requests must include the token in the Authorization header

## API Usage

### Authentication Flow
1. User authenticates via Better Auth on frontend
2. Better Auth issues JWT token
3. Frontend attaches token to API requests: `Authorization: Bearer {token}`
4. Backend validates JWT and extracts user identity

### Base URL
```
http://localhost:8000/api/{user_id}/
```

### Available Endpoints

All existing task endpoints now require authentication:

#### Create Task
````
POST /api/{user_id}/tasks
Authorization: Bearer {valid-jwt-token}

{
  "title": "Task title (1-100 chars)",
  "description": "Optional description"
}
```
- **Success**: 201 Created with task object
- **Validation Error**: 422 Unprocessable Entity
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden (user_id mismatch)

#### Get All Tasks
````
GET /api/{user_id}/tasks?limit=50&offset=0&completed=false
Authorization: Bearer {valid-jwt-token}
```
- **Success**: 200 OK with paginated task list
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden (user_id mismatch)

#### Get Specific Task
````
GET /api/{user_id}/tasks/{task_id}
Authorization: Bearer {valid-jwt-token}
```
- **Success**: 200 OK with task object
- **Not Found**: 404 Not Found
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden

#### Update Task
````
PUT /api/{user_id}/tasks/{task_id}
Authorization: Bearer {valid-jwt-token}

{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```
- **Success**: 200 OK with updated task
- **Validation Error**: 422 Unprocessable Entity
- **Not Found**: 404 Not Found
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden

#### Mark Task Complete
````
PATCH /api/{user_id}/tasks/{task_id}/complete
Authorization: Bearer {valid-jwt-token}

{
  "completed": true
}
```
- **Success**: 200 OK with updated task
- **Not Found**: 404 Not Found
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden

#### Delete Task
````
DELETE /api/{user_id}/tasks/{task_id}
Authorization: Bearer {valid-jwt-token}
```
- **Success**: 204 No Content
- **Not Found**: 404 Not Found
- **Unauthorized**: 401 Unauthorized
- **Forbidden**: 403 Forbidden

## Authentication Requirements

Every API request must include:
1. Valid JWT token in Authorization header
2. User ID in URL must match JWT token's user ID
3. Token must not be expired

## Error Handling

All errors follow the format:
```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

Common HTTP status codes:
- `200`: Success (GET, PUT, PATCH)
- `201`: Created (POST)
- `204`: No Content (DELETE)
- `400`: Bad Request (malformed request)
- `401`: Unauthorized (invalid/expired JWT)
- `403`: Forbidden (user_id mismatch or insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation error)

## Testing

### Unit Tests
```bash
cd backend
python -m pytest tests/unit/
```

### Integration Tests
```bash
# With test database
TESTING=true python -m pytest tests/integration/
```

## Running the Server

```bash
cd backend
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend Integration

1. Configure Better Auth on frontend
2. Obtain JWT token after successful authentication
3. Attach token to all API requests: `Authorization: Bearer {token}`
4. Use logged-in user's ID in URL paths
5. Handle token expiration and renewal as needed