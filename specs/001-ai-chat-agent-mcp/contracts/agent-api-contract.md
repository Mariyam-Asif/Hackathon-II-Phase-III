# API Contract: AI Agent Integration

## Overview
This document defines the API contract for the AI Agent integration with the task management system.

## Base URL
`/api/v1/agents`

## Endpoints

### POST /chat
Process a natural language request through the AI agent and execute appropriate MCP tools.

#### Request
```json
{
  "user_id": "string",
  "message": "string",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```

**Parameters:**
- `user_id`: Unique identifier of the requesting user
- `message`: Natural language request from the user
- `conversation_history`: Previous conversation turns (optional)

#### Response
```json
{
  "response": "string",
  "tool_calls": [
    {
      "name": "add_task|list_tasks|complete_task|delete_task|update_task",
      "arguments": {}
    }
  ],
  "tool_results": [
    {
      "tool_name": "string",
      "result": {},
      "success": boolean
    }
  ],
  "final_response": "string"
}
```

**Response Fields:**
- `response`: Agent's initial response before tool execution
- `tool_calls`: List of MCP tools to be executed
- `tool_results`: Results from executed tools
- `final_response`: Final response after tool execution

#### Error Response
```json
{
  "error": "string",
  "code": "string",
  "details": {}
}
```

### GET /capabilities
Retrieve the agent's capabilities and supported MCP tools.

#### Response
```json
{
  "capabilities": [
    {
      "name": "add_task",
      "description": "Add a new task",
      "parameters": {
        "title": "string",
        "description": "string",
        "due_date": "string",
        "priority": "string"
      }
    },
    {
      "name": "list_tasks",
      "description": "List user's tasks",
      "parameters": {
        "status": "string",
        "limit": "integer",
        "offset": "integer"
      }
    },
    {
      "name": "complete_task",
      "description": "Mark a task as complete",
      "parameters": {
        "task_id": "string"
      }
    },
    {
      "name": "update_task",
      "description": "Update task properties",
      "parameters": {
        "task_id": "string",
        "title": "string",
        "description": "string",
        "status": "string",
        "due_date": "string",
        "priority": "string"
      }
    },
    {
      "name": "delete_task",
      "description": "Delete a task",
      "parameters": {
        "task_id": "string"
      }
    }
  ]
}
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Error Codes
- `AGENT_PROCESSING_ERROR`: Error occurred while processing agent request
- `TOOL_EXECUTION_ERROR`: Error occurred while executing MCP tool
- `INVALID_REQUEST`: Request parameters are invalid
- `UNAUTHORIZED`: User is not authenticated
- `RATE_LIMITED`: Request rate limit exceeded