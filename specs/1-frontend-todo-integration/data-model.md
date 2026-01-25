# Data Model: Frontend UI and API Integration

## Frontend-Focused Data Models

### Task Entity
- **id**: string - Unique identifier for the task
- **title**: string - Required title of the task
- **description**: string (optional) - Optional detailed description of the task
- **completed**: boolean - Flag indicating if the task is completed, default false
- **userId**: string - Foreign key linking to the user who owns the task
- **createdAt**: Date - Timestamp when the task was created
- **updatedAt**: Date - Timestamp when the task was last updated

### User Entity (managed by Better Auth)
- **id**: string - Unique identifier for the user
- **email**: string - Required, unique email address
- **name**: string (optional) - Optional display name for the user

### Task State Model (frontend only)
- **loading**: boolean - Indicates if tasks are currently being loaded
- **error**: string (optional) - Error message if task operations fail
- **tasks**: Task[] - Array of tasks for the current user
- **selectedTask**: Task (optional) - Currently selected task for viewing/editing

### Authentication State Model (frontend only)
- **user**: User (optional) - Current authenticated user data
- **isLoading**: boolean - Whether authentication status is being checked
- **isAuthenticated**: boolean - Whether the user is currently authenticated
- **error**: string (optional) - Error message if authentication fails

## Validation Rules

### Task Validation
- Title must be provided and not empty
- Title length must be between 1 and 255 characters
- Description length must not exceed 1000 characters if provided
- Completed status must be a boolean value

### User Validation (handled by Better Auth)
- Email must be valid and unique
- Password must meet security requirements (handled by auth system)

## State Transitions

### Task State Transitions
- **Pending**: Task is being created or updated
- **Success**: Task operation completed successfully
- **Error**: Task operation failed
- **Idle**: No current task operations in progress

### Authentication State Transitions
- **Unauthenticated**: User not logged in
- **Authenticating**: User login/register in progress
- **Authenticated**: User successfully logged in
- **AuthError**: Authentication failed