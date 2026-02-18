# Quickstart Guide: AI Chat Agent & MCP Tooling

## Overview
This guide provides the essential information to get started with the AI Chat Agent & MCP Tooling feature for task management.

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL-compatible database (Neon Serverless PostgreSQL recommended)
- OpenAI API key
- MCP SDK installed

## Setup

### 1. Environment Variables
Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database
BETTER_AUTH_SECRET=your_auth_secret
JWT_ALGORITHM=HS256
```

### 2. Database Setup
Initialize the database with the required tables:
```bash
cd backend
python -m src.database.init_db
```

### 3. Install Dependencies
Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

## Running the Application

### 1. Start the Backend
```bash
cd backend
uvicorn src.main:app --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

## Using the AI Chat Agent

### 1. Access the Chat Interface
Navigate to `http://localhost:3000/chat` to access the chat interface.

### 2. Supported Commands
The AI agent recognizes natural language for the following operations:

**Adding Tasks**:
- "Add a task to buy groceries"
- "Create a task called 'finish report'"
- "Remember to call John tomorrow"

**Listing Tasks**:
- "Show me my tasks"
- "What do I need to do?"
- "List all pending tasks"

**Completing Tasks**:
- "Mark 'buy groceries' as complete"
- "Finish the report task"
- "Complete task 1"

**Updating Tasks**:
- "Change the due date of 'buy groceries' to tomorrow"
- "Update the priority of 'finish report' to high"
- "Rename 'call John' to 'call John about project'"

**Deleting Tasks**:
- "Delete the 'buy groceries' task"
- "Remove task 1"
- "Cancel the meeting task"

## MCP Tools Architecture

The system uses the following MCP tools for task management:

### add_task
- Creates new tasks in the database
- Parameters: title, description, due_date, priority

### list_tasks
- Retrieves tasks from the database
- Parameters: status filter, limit, offset

### complete_task
- Updates task status to completed
- Parameters: task_id

### update_task
- Modifies existing task properties
- Parameters: task_id, title, description, status, due_date, priority

### delete_task
- Removes tasks from the database
- Parameters: task_id

## Troubleshooting

### Common Issues
1. **Agent not responding**: Check that OPENAI_API_KEY is set correctly
2. **Database connection errors**: Verify DATABASE_URL format and connectivity
3. **Authentication failures**: Ensure JWT tokens are properly configured

### Logging
Logs are available in the backend console and can be configured in the settings.