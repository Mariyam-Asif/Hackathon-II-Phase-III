# Data Model: AI Chat Agent & MCP Tooling

## Overview
This document defines the data models for the AI Chat Agent & MCP Tooling feature, focusing on the task management entities and their relationships.

## Core Entities

### Task
**Description**: Represents a user task that can be managed through the AI chat agent.

**Fields**:
- `id` (UUID/string): Unique identifier for the task
- `user_id` (UUID/string): Reference to the user who owns the task
- `title` (string): Brief description of the task
- `description` (string, optional): Detailed description of the task
- `status` (enum: "pending", "in_progress", "completed"): Current status of the task
- `created_at` (datetime): Timestamp when the task was created
- `updated_at` (datetime): Timestamp when the task was last updated
- `due_date` (datetime, optional): Deadline for the task completion
- `priority` (enum: "low", "medium", "high", "urgent"): Priority level of the task

**Validation Rules**:
- `title` is required and must be 1-255 characters
- `status` must be one of the defined enum values
- `user_id` must reference an existing user
- `due_date` must be in the future if provided
- `created_at` is set automatically on creation
- `updated_at` is updated automatically on any change

### User
**Description**: Represents a registered user of the system.

**Fields**:
- `id` (UUID/string): Unique identifier for the user
- `email` (string): Email address of the user (unique)
- `name` (string): Display name of the user
- `created_at` (datetime): Timestamp when the user was created
- `updated_at` (datetime): Timestamp when the user was last updated
- `is_active` (boolean): Whether the user account is active

**Validation Rules**:
- `email` is required and must be unique
- `name` is required and must be 1-100 characters
- `is_active` defaults to true

## Relationships
- One User has many Tasks (one-to-many relationship)
- Foreign key: Task.user_id references User.id

## State Transitions

### Task Status Transitions
- `pending` → `in_progress`: When user starts working on the task
- `in_progress` → `completed`: When user marks task as complete
- `completed` → `pending`: When user reopens a completed task
- `pending` → `completed`: Direct transition for quick completion

## Indexes
- Task: Index on user_id for efficient user-specific queries
- Task: Index on status for filtering by task status
- User: Index on email for authentication lookups

## Constraints
- All timestamps are stored in UTC
- Soft deletes are not used; records are permanently deleted
- Task titles must be unique per user to prevent confusion