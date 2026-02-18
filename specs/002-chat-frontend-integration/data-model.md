# Data Model: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Date**: 2026-02-09
**Status**: Design

## Entity Definitions

### Conversation Entity
- **conversation_id**: UUID (Primary Key)
  - Unique identifier for each conversation
  - Auto-generated using UUID4
- **user_id**: UUID (Foreign Key)
  - Reference to the user who owns the conversation
  - Links to User entity
- **created_at**: DateTime (UTC)
  - Timestamp when conversation was initiated
  - Used for ordering and retention policies
- **updated_at**: DateTime (UTC)
  - Timestamp of last activity in conversation
  - Updated whenever a new message is added
- **title**: String (Optional)
  - Human-readable title derived from first message or user input
  - Max length: 200 characters

### Message Entity
- **message_id**: UUID (Primary Key)
  - Unique identifier for each message
  - Auto-generated using UUID4
- **conversation_id**: UUID (Foreign Key)
  - Reference to the conversation this message belongs to
  - Links to Conversation entity
- **sender_type**: Enum ['user', 'agent']
  - Indicates whether the message was sent by user or AI agent
  - Required field
- **content**: Text
  - The actual message content
  - No length restriction to accommodate detailed responses
- **timestamp**: DateTime (UTC)
  - When the message was created/sent
  - Used for chronological ordering
- **status**: Enum ['sent', 'pending', 'error'] (Default: 'sent')
  - Tracks the delivery/status of the message
  - Useful for handling failed transmissions
- **parent_message_id**: UUID (Optional, Foreign Key)
  - Reference to parent message for threaded conversations
  - Enables conversation branching/nesting

### User Entity
- **user_id**: UUID (Primary Key)
  - Unique identifier for each user
  - Auto-generated using UUID4
- **email**: String
  - User's email address for identification
  - Used as login identifier
  - Must be unique across all users
- **created_at**: DateTime (UTC)
  - When the user account was created
- **updated_at**: DateTime (UTC)
  - Last update to user account information

### Todo Entity
- **todo_id**: UUID (Primary Key)
  - Unique identifier for each todo item
  - Auto-generated using UUID4
- **user_id**: UUID (Foreign Key)
  - Reference to the user who owns the todo
  - Links to User entity
- **title**: String
  - Brief description of the todo item
  - Max length: 500 characters
- **description**: Text (Optional)
  - Detailed description of the todo
  - No length restriction
- **status**: Enum ['pending', 'in_progress', 'completed', 'cancelled'] (Default: 'pending')
  - Current state of the todo item
- **priority**: Enum ['low', 'medium', 'high', 'urgent'] (Default: 'medium')
  - Priority level of the todo item
- **due_date**: DateTime (Optional)
  - Deadline for the todo item
  - Null if no deadline
- **created_at**: DateTime (UTC)
  - When the todo was created
- **updated_at**: DateTime (UTC)
  - Last modification timestamp
- **completed_at**: DateTime (Optional)
  - When the todo was marked as completed

## Relationships

### Conversation ↔ Message
- One-to-Many relationship
- One conversation can have multiple messages
- Messages are deleted if conversation is deleted (CASCADE)

### User ↔ Conversation
- One-to-Many relationship
- One user can have multiple conversations
- Conversations are deleted if user is deleted (CASCADE)

### User ↔ Todo
- One-to-Many relationship
- One user can have multiple todos
- Todos are deleted if user is deleted (CASCADE)

### Message ↔ Todo
- Many-to-Many relationship (via implicit association)
- Messages may reference multiple todos
- Todos may be referenced in multiple messages

## Validation Rules

### Conversation Entity
- `user_id` must reference an existing User
- `title` must be 200 characters or fewer if provided
- `updated_at` must be equal to or later than `created_at`

### Message Entity
- `conversation_id` must reference an existing Conversation
- `sender_type` must be either 'user' or 'agent'
- `status` must be one of the defined enum values
- `parent_message_id` must reference an existing Message in the same conversation if provided

### User Entity
- `email` must follow standard email format
- `email` must be unique across all users
- `updated_at` must be equal to or later than `created_at`

### Todo Entity
- `user_id` must reference an existing User
- `title` must be 500 characters or fewer
- `status` must be one of the defined enum values
- `priority` must be one of the defined enum values
- `due_date` must be in the future if provided
- `completed_at` must be equal to or later than `created_at` if status is 'completed'

## Indexes

### Conversation Entity
- Index on `user_id` for efficient user conversation retrieval
- Index on `created_at` for chronological ordering

### Message Entity
- Index on `conversation_id` for efficient conversation message retrieval
- Composite index on `conversation_id` and `timestamp` for chronological message retrieval
- Index on `timestamp` for overall message ordering

### User Entity
- Unique index on `email` for efficient lookup and uniqueness enforcement

### Todo Entity
- Index on `user_id` for efficient user todo retrieval
- Index on `status` for filtering by status
- Index on `due_date` for deadline-based queries
- Index on `priority` for priority-based queries
- Index on `created_at` for chronological ordering