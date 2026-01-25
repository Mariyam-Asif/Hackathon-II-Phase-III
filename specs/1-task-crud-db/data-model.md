# Data Model: Todo App Phase II - Task CRUD & Database Integration

## Entity: Task

### Fields
- **id**: UUID (Primary Key, auto-generated)
  - Purpose: Unique identifier for each task
  - Constraints: Not null, unique, auto-generated
- **title**: VARCHAR(100)
  - Purpose: Task title/description
  - Constraints: Not null, max 100 characters
- **description**: TEXT (Optional)
  - Purpose: Detailed description of the task
  - Constraints: Nullable
- **completed**: BOOLEAN
  - Purpose: Track completion status
  - Constraints: Not null, default False
- **deleted**: BOOLEAN
  - Purpose: Track soft deletion status
  - Constraints: Not null, default False
- **user_id**: UUID (Foreign Key)
  - Purpose: Link task to owning user
  - Constraints: Not null, references User.id
- **created_at**: TIMESTAMP
  - Purpose: Track creation time
  - Constraints: Not null, auto-generated
- **updated_at**: TIMESTAMP
  - Purpose: Track last update time
  - Constraints: Not null, auto-generated

### Relationships
- **Belongs to**: User (via user_id foreign key)
- **Access Control**: Users can only access tasks where user_id matches their own ID

### Validation Rules
- Title must be between 1 and 100 characters
- User must be authenticated and authorized to access their own tasks only
- Soft delete means setting deleted=True rather than removing from database

### State Transitions
- Created → Active (initial state when task is created)
- Active → Completed (when PATCH /complete is called)
- Active/Completed → Deleted (when DELETE is called, sets deleted=True)
- Deleted → Active (if restoration functionality is added later)

## Entity: User

### Fields
- **id**: UUID (Primary Key, auto-generated)
  - Purpose: Unique identifier for each user
  - Constraints: Not null, unique, auto-generated
- **email**: VARCHAR(255)
  - Purpose: User's email address for identification
  - Constraints: Not null, unique
- **username**: VARCHAR(50)
  - Purpose: User's display name
  - Constraints: Not null, unique
- **created_at**: TIMESTAMP
  - Purpose: Track user creation time
  - Constraints: Not null, auto-generated
- **updated_at**: TIMESTAMP
  - Purpose: Track last user update time
  - Constraints: Not null, auto-generated

### Relationships
- **Has many**: Tasks (via tasks.user_id foreign key)
- **Access Control**: Users can only access their own tasks

### Validation Rules
- Email must be valid email format
- Username must be unique and between 3-50 characters