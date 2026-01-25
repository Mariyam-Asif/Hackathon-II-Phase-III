# Contract: API Specification for Todo App Phase II

## API Endpoints

### POST /api/{user_id}/tasks
**Description**: Create a new task for the specified user

**Request Parameters**:
- user_id (path): UUID of the user creating the task

**Request Body**:
```json
{
  "title": "string (max 100 chars)",
  "description": "string (optional)"
}
```

**Response**:
- 201 Created: Task created successfully
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string or null",
  "completed": false,
  "deleted": false,
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to create tasks for this user_id
- 422 Unprocessable Entity: Validation error

### GET /api/{user_id}/tasks
**Description**: Retrieve all tasks for the specified user

**Request Parameters**:
- user_id (path): UUID of the user whose tasks to retrieve
- limit (query, optional): Number of tasks to return (default: 50, max: 100)
- offset (query, optional): Number of tasks to skip (default: 0)
- completed (query, optional): Filter by completion status (true/false)

**Response**:
- 200 OK: Tasks retrieved successfully
```json
{
  "tasks": [
    {
      "id": "UUID",
      "title": "string",
      "description": "string or null",
      "completed": "boolean",
      "deleted": "boolean",
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp"
    }
  ],
  "total": "integer",
  "limit": "integer",
  "offset": "integer"
}
```
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to access this user_id's tasks
- 422 Unprocessable Entity: Invalid query parameters

### GET /api/{user_id}/tasks/{id}
**Description**: Retrieve a specific task for the specified user

**Request Parameters**:
- user_id (path): UUID of the user
- id (path): UUID of the task to retrieve

**Response**:
- 200 OK: Task retrieved successfully
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string or null",
  "completed": "boolean",
  "deleted": "boolean",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to access this user_id's tasks
- 404 Not Found: Task not found
- 422 Unprocessable Entity: Invalid ID format

### PUT /api/{user_id}/tasks/{id}
**Description**: Update a specific task for the specified user

**Request Parameters**:
- user_id (path): UUID of the user
- id (path): UUID of the task to update

**Request Body**:
```json
{
  "title": "string (optional, max 100 chars)",
  "description": "string (optional)",
  "completed": "boolean (optional)"
}
```

**Response**:
- 200 OK: Task updated successfully
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string or null",
  "completed": "boolean",
  "deleted": "boolean",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to update this task
- 404 Not Found: Task not found
- 422 Unprocessable Entity: Validation error

### DELETE /api/{user_id}/tasks/{id}
**Description**: Mark a specific task as deleted (soft delete) for the specified user

**Request Parameters**:
- user_id (path): UUID of the user
- id (path): UUID of the task to delete

**Response**:
- 204 No Content: Task marked as deleted successfully
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to delete this task
- 404 Not Found: Task not found
- 422 Unprocessable Entity: Invalid ID format

### PATCH /api/{user_id}/tasks/{id}/complete
**Description**: Toggle or set the completion status of a specific task for the specified user

**Request Parameters**:
- user_id (path): UUID of the user
- id (path): UUID of the task to update completion status

**Request Body**:
```json
{
  "completed": "boolean (optional, if omitted, toggles current status)"
}
```

**Response**:
- 200 OK: Task completion status updated successfully
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string or null",
  "completed": "boolean",
  "deleted": "boolean",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: User doesn't have permission to update this task
- 404 Not Found: Task not found
- 422 Unprocessable Entity: Validation error

## Error Response Format
All error responses follow the standardized format:
```json
{
  "error": "descriptive error message",
  "code": "error_code",
  "details": {}
}
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
`Authorization: Bearer <jwt_token>`

## Validation
- All UUIDs must be valid RFC 4122 compliant identifiers
- Titles must be 1-100 characters
- User must be authenticated and authorized to access resources for the specified user_id