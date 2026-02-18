# API Contract: MCP Tools for Task Management

## Overview
This document defines the MCP tool contracts for task management operations.

## add_task Tool

### Description
Creates a new task for the authenticated user.

### Input Parameters
```json
{
  "title": "string",
  "description": "string (optional)",
  "due_date": "ISO 8601 datetime string (optional)",
  "priority": "enum: low|medium|high|urgent (optional, default: medium)"
}
```

### Output
```json
{
  "success": true,
  "task_id": "string",
  "message": "Task created successfully"
}
```

### Error Output
```json
{
  "success": false,
  "error": "string",
  "code": "VALIDATION_ERROR|AUTH_ERROR|INTERNAL_ERROR"
}
```

---

## list_tasks Tool

### Description
Retrieves tasks for the authenticated user with optional filtering.

### Input Parameters
```json
{
  "status": "enum: all|pending|in_progress|completed (optional, default: all)",
  "limit": "integer (optional, default: 10)",
  "offset": "integer (optional, default: 0)",
  "sort_by": "enum: created_at|due_date|priority (optional, default: created_at)",
  "order": "enum: asc|desc (optional, default: desc)"
}
```

### Output
```json
{
  "success": true,
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "status": "enum: pending|in_progress|completed",
      "created_at": "ISO 8601 datetime string",
      "updated_at": "ISO 8601 datetime string",
      "due_date": "ISO 8601 datetime string (or null)",
      "priority": "enum: low|medium|high|urgent"
    }
  ],
  "total_count": "integer",
  "filtered_count": "integer"
}
```

### Error Output
```json
{
  "success": false,
  "error": "string",
  "code": "VALIDATION_ERROR|AUTH_ERROR|INTERNAL_ERROR"
}
```

---

## complete_task Tool

### Description
Marks a task as completed for the authenticated user.

### Input Parameters
```json
{
  "task_id": "string"
}
```

### Output
```json
{
  "success": true,
  "task_id": "string",
  "previous_status": "enum: pending|in_progress",
  "new_status": "completed",
  "message": "Task marked as completed"
}
```

### Error Output
```json
{
  "success": false,
  "error": "string",
  "code": "VALIDATION_ERROR|AUTH_ERROR|NOT_FOUND|INTERNAL_ERROR"
}
```

---

## update_task Tool

### Description
Updates properties of an existing task for the authenticated user.

### Input Parameters
```json
{
  "task_id": "string",
  "title": "string (optional)",
  "description": "string (optional)",
  "status": "enum: pending|in_progress|completed (optional)",
  "due_date": "ISO 8601 datetime string (optional)",
  "priority": "enum: low|medium|high|urgent (optional)"
}
```

### Output
```json
{
  "success": true,
  "task_id": "string",
  "updated_fields": ["string"],
  "message": "Task updated successfully"
}
```

### Error Output
```json
{
  "success": false,
  "error": "string",
  "code": "VALIDATION_ERROR|AUTH_ERROR|NOT_FOUND|INTERNAL_ERROR"
}
```

---

## delete_task Tool

### Description
Deletes a task for the authenticated user.

### Input Parameters
```json
{
  "task_id": "string"
}
```

### Output
```json
{
  "success": true,
  "task_id": "string",
  "message": "Task deleted successfully"
}
```

### Error Output
```json
{
  "success": false,
  "error": "string",
  "code": "VALIDATION_ERROR|AUTH_ERROR|NOT_FOUND|INTERNAL_ERROR"
}
```

---

## Authentication and Authorization

All MCP tools require:
1. Valid JWT token in request context
2. User ID verification to ensure user can only operate on their own tasks
3. Proper permission validation

## Error Handling Standards

### Common Error Codes
- `VALIDATION_ERROR`: Input parameters failed validation
- `AUTH_ERROR`: Authentication or authorization failed
- `NOT_FOUND`: Requested resource does not exist
- `INTERNAL_ERROR`: Unexpected server error occurred
- `CONFLICT_ERROR`: Operation conflicts with current state