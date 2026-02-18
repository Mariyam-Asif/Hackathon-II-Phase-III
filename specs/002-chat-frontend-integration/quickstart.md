# Quick Start: AI-Powered Todo Chatbot

## Overview
This guide provides step-by-step instructions to set up and run the AI-Powered Todo Chatbot locally. The system consists of a frontend using OpenAI ChatKit, a backend API with FastAPI, an AI agent using OpenAI's API, an MCP server, and a Neon PostgreSQL database.

## Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn package manager
- Neon PostgreSQL account (or local PostgreSQL instance)
- OpenAI API key
- Better Auth compatible environment

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

## Configuration

### 1. Backend Environment Variables
Create a `.env` file in the `backend` directory:

```env
DATABASE_URL="postgresql://username:password@localhost:5432/todo_chatbot"
OPENAI_API_KEY="your-openai-api-key"
BETTER_AUTH_SECRET="your-better-auth-secret"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_DELTA=604800  # 7 days in seconds
MCP_SERVER_URL="http://localhost:8080"
```

### 2. Frontend Environment Variables
Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:8000"
```

## Database Setup

### 1. Initialize Database
```bash
cd backend
python -m src.database.init
```

### 2. Run Migrations
```bash
python -m src.database.migrate
```

## Running the System

### 1. Start the MCP Server
```bash
cd backend/src/mcp
python mcp_server.py
```

### 2. Start the Backend API
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```

## Testing the Integration

### 1. Verify Backend Health
Visit `http://localhost:8000/health` to confirm the backend is running.

### 2. Check API Endpoints
Test the chat endpoint with a simple request:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {your_jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me create a todo?"}'
```

### 3. Test Frontend
Navigate to `http://localhost:3000` in your browser and verify:
- Successful login with Better Auth
- Chat interface loads properly
- Messages can be sent and received

## Architecture Components

### MCP Server
The Model Context Protocol (MCP) server handles all todo operations through standardized tools:
- `create_todo` - Creates a new todo item
- `read_todos` - Retrieves user's todo list
- `update_todo` - Modifies an existing todo
- `delete_todo` - Removes a todo item
- `complete_todo` - Marks a todo as completed

### AI Agent
Configured with OpenAI's API to use function calling:
- Interacts with the system exclusively through MCP tools
- Maintains conversation context from database
- Provides natural language interface for todo management

### Frontend (ChatKit)
- Minimal chat interface focused on functionality
- Communicates with backend API
- Displays conversation history
- Handles user authentication

### Backend (FastAPI)
- Handles authentication via Better Auth
- Manages conversation state in database
- Orchestrates communication between frontend and AI agent
- Validates and processes API requests

## Development Workflow

### Making Changes to MCP Tools
1. Update the tool definitions in `backend/src/mcp/tools/`
2. Update the AI agent configuration if needed
3. Test the new functionality through the chat interface

### Modifying Data Models
1. Update the SQLModel definitions in `backend/src/models/`
2. Create and run new migration files
3. Update API contracts if necessary
4. Test with the frontend

### Adding New API Endpoints
1. Define the endpoint in `backend/src/api/`
2. Update API contracts documentation
3. Implement corresponding frontend functionality
4. Test the complete flow

## Troubleshooting

### Common Issues

**Issue**: Database connection errors
**Solution**: Verify `DATABASE_URL` is correct and database is running

**Issue**: Authentication failures
**Solution**: Check that JWT configuration matches between frontend and backend

**Issue**: AI agent not responding
**Solution**: Verify OpenAI API key and MCP server is running

**Issue**: Frontend can't connect to backend
**Solution**: Check CORS configuration and that both services are running on expected ports

### Logging
- Backend logs are output to console when running with `--reload`
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in environment
- MCP server logs are available in the server console

## Next Steps
1. Customize the AI agent's behavior by modifying the system prompt
2. Extend MCP tools with additional functionality
3. Enhance the frontend UI with additional features
4. Add monitoring and observability to production deployments