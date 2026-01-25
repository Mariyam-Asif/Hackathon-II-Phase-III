# Frontend Integration Guide: Better Auth with Backend API

This document explains how to integrate the frontend with the Better Auth authentication system and the backend API.

## Overview

The backend API is protected by JWT tokens issued by Better Auth. All authenticated endpoints require a valid JWT token in the Authorization header.

## Authentication Flow

### 1. User Registration

```javascript
// Example registration flow with Better Auth
const registerUser = async (email, username, password) => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      username,
      password
    })
  });

  if (response.ok) {
    const data = await response.json();
    // Store the token in local storage or secure cookie
    localStorage.setItem('auth_token', data.access_token);
    return data;
  } else {
    throw new Error('Registration failed');
  }
};
```

### 2. User Login

```javascript
// Example login flow with Better Auth
const loginUser = async (email, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password
    })
  });

  if (response.ok) {
    const data = await response.json();
    // Store the token in local storage or secure cookie
    localStorage.setItem('auth_token', data.access_token);
    return data;
  } else {
    throw new Error('Login failed');
  }
};
```

### 3. Making Authenticated API Calls

```javascript
// Example of making authenticated API calls
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('auth_token');

  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (response.status === 401) {
    // Token might be expired, redirect to login
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
    return;
  }

  return response;
};

// Example: Get user's tasks
const getUserTasks = async (userId) => {
  const response = await makeAuthenticatedRequest(`/api/${userId}/tasks`);
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('Failed to fetch tasks');
  }
};
```

## API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate user and get access token
- `POST /auth/validate-token` - Validate an access token
- `POST /auth/logout` - Logout user (client-side token removal)

### Task Endpoints

- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a specific task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Update task completion status
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task (soft delete)

## Error Handling

The API returns standardized error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2023-10-20T10:00:00Z",
  "path": "/api/example"
}
```

Common error codes:
- `MISSING_AUTH_HEADER`: No authorization header provided
- `INVALID_AUTH_SCHEME`: Authorization scheme must be Bearer
- `INVALID_TOKEN`: Invalid or expired token
- `USER_MISMATCH`: Access denied - token user ID does not match requested user ID
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded for authentication attempts

## Security Best Practices

1. Store JWT tokens securely (preferably in httpOnly cookies)
2. Implement token refresh logic for long-lived sessions
3. Handle token expiration gracefully
4. Validate user IDs match between token and URL parameters
5. Implement proper error handling and user feedback

## Environment Configuration

Make sure your frontend is configured to connect to the correct backend:

```javascript
// Example configuration
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-api.com'
  : 'http://localhost:8000';
```