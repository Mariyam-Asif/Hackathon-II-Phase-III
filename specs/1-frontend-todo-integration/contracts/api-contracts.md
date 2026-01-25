# API Contracts: Frontend UI and API Integration

## Authentication Endpoints (Managed by Better Auth)

### POST /api/auth/register
**Description**: Register a new user account
**Request**:
- Body: `{ email: string, password: string, name?: string }`
**Response**:
- 200: `{ user: { id, email, name }, token: string }`
- 400: `{ error: string }`
- 409: `{ error: "User already exists" }`

### POST /api/auth/login
**Description**: Authenticate a user and return session token
**Request**:
- Body: `{ email: string, password: string }`
**Response**:
- 200: `{ user: { id, email, name }, token: string }`
- 400: `{ error: string }`
- 401: `{ error: "Invalid credentials" }`

### POST /api/auth/logout
**Description**: Logout the current user and invalidate session
**Request**:
- Headers: `{ Authorization: "Bearer ${token}" }`
**Response**:
- 200: `{ message: "Successfully logged out" }`
- 401: `{ error: "Unauthorized" }`

## Task Management Endpoints (Managed by FastAPI Backend)

### GET /api/{user_id}/tasks
**Description**: Retrieve all tasks for the authenticated user
**Path Parameters**:
- `user_id`: string - The ID of the authenticated user
**Headers**:
- `{ Authorization: "Bearer ${token}" }`
**Response**:
- 200: `{ tasks: Task[] }`
- 401: `{ error: "Unauthorized" }`
- 403: `{ error: "Forbidden: Cannot access other user's tasks" }`
- 500: `{ error: "Internal server error" }`

### POST /api/{user_id}/tasks
**Description**: Create a new task for the authenticated user
**Path Parameters**:
- `user_id`: string - The ID of the authenticated user
**Headers**:
- `{ Authorization: "Bearer ${token}" }`
**Request Body**:
- `{ title: string, description?: string }`
**Response**:
- 201: `{ task: Task }`
- 400: `{ error: string }`
- 401: `{ error: "Unauthorized" }`
- 403: `{ error: "Forbidden: Cannot access other user's tasks" }`
- 500: `{ error: "Internal server error" }`

### PUT /api/{user_id}/tasks/{task_id}
**Description**: Update an existing task for the authenticated user
**Path Parameters**:
- `user_id`: string - The ID of the authenticated user
- `task_id`: string - The ID of the task to update
**Headers**:
- `{ Authorization: "Bearer ${token}" }`
**Request Body**:
- `{ title?: string, description?: string, completed?: boolean }`
**Response**:
- 200: `{ task: Task }`
- 400: `{ error: string }`
- 401: `{ error: "Unauthorized" }`
- 403: `{ error: "Forbidden: Cannot access other user's tasks" }`
- 404: `{ error: "Task not found" }`
- 500: `{ error: "Internal server error" }`

### DELETE /api/{user_id}/tasks/{task_id}
**Description**: Delete a task for the authenticated user
**Path Parameters**:
- `user_id`: string - The ID of the authenticated user
- `task_id`: string - The ID of the task to delete
**Headers**:
- `{ Authorization: "Bearer ${token}" }`
**Response**:
- 200: `{ message: "Task deleted successfully" }`
- 401: `{ error: "Unauthorized" }`
- 403: `{ error: "Forbidden: Cannot access other user's tasks" }`
- 404: `{ error: "Task not found" }`
- 500: `{ error: "Internal server error" }`

### PATCH /api/{user_id}/tasks/{task_id}/complete
**Description**: Toggle the completion status of a task for the authenticated user
**Path Parameters**:
- `user_id`: string - The ID of the authenticated user
- `task_id`: string - The ID of the task to update
**Headers**:
- `{ Authorization: "Bearer ${token}" }`
**Request Body**:
- `{ completed: boolean }`
**Response**:
- 200: `{ task: Task }`
- 400: `{ error: string }`
- 401: `{ error: "Unauthorized" }`
- 403: `{ error: "Forbidden: Cannot access other user's tasks" }`
- 404: `{ error: "Task not found" }`
- 500: `{ error: "Internal server error" }`

## Frontend API Client Interface

### Authentication Service Interface
```typescript
interface AuthService {
  register(email: string, password: string, name?: string): Promise<{ user: User, token: string }>;
  login(email: string, password: string): Promise<{ user: User, token: string }>;
  logout(): Promise<{ message: string }>;
  getCurrentUser(): Promise<User | null>;
}
```

### Task Service Interface
```typescript
interface TaskService {
  getAllTasks(userId: string): Promise<Task[]>;
  createTask(userId: string, taskData: { title: string, description?: string }): Promise<Task>;
  updateTask(userId: string, taskId: string, taskData: Partial<Task>): Promise<Task>;
  deleteTask(userId: string, taskId: string): Promise<{ message: string }>;
  toggleTaskComplete(userId: string, taskId: string, completed: boolean): Promise<Task>;
}
```

## Error Response Format
All error responses follow this standard format:
```typescript
{
  error: string;
}
```

## Success Response Format
Most success responses follow these patterns:
```typescript
{
  // Single resource
  [resourceName]: Resource;
}

{
  // Multiple resources
  [resourceNamePlural]: Resource[];
}

{
  // Message responses
  message: string;
}
```