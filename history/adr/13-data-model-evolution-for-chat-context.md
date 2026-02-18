# ADR-13: Data Model Evolution for Chat Context Management

## Status
Accepted

## Date
2026-02-09

## Context
The system requires extending the existing task management data model to support chat conversation context while maintaining compatibility with the stateless agent architecture. The chat system needs to store conversation history, message threads, and maintain context across multiple interactions. The constitution mandates that the database serves as the single source of truth, with all state stored persistently.

## Decision
We will extend the data model to include Conversation and Message entities alongside the existing Todo entity. The Conversation entity will track conversation threads with timestamps and titles, while the Message entity will store individual messages with sender type, content, status, and threading information. We will maintain the existing Todo entity structure but ensure it integrates with the new conversation context through user associations.

## Alternatives Considered

### Alternative 1: Store Conversation Context in Message Content Only
- **Pros**: Simpler schema, fewer tables to manage, potentially faster queries
- **Cons**: Loss of conversation-level metadata, difficulty in organizing messages, poor support for conversation navigation
- **Rejected** because it would limit the ability to manage multiple conversations and track conversation-level information

### Alternative 2: Separate Database for Chat vs Tasks
- **Pros**: Clear separation of concerns, potentially better performance for each domain
- **Cons**: Increased complexity in maintaining consistency, cross-database joins difficult, violates single source of truth principle
- **Rejected** because it would violate the constitutional requirement for database as single source of truth

### Alternative 3: Embed Messages in Todo Items
- **Pros**: Might seem to simplify relationship between tasks and chat
- **Cons**: Would create overly complex data structure, poor performance for chat-specific queries, violates separation of concerns
- **Rejected** because it would tightly couple chat functionality with task management inappropriately

## Consequences

### Positive
- Enables rich conversation history with proper threading and metadata
- Maintains clear separation between chat and task data while allowing integration
- Supports the constitutional requirement for database as single source of truth
- Enables conversation-level operations like archiving, searching, and sharing
- Preserves existing Todo entity structure for backward compatibility

### Negative
- Increases database schema complexity with additional tables and relationships
- May require more complex queries to join conversation and task data
- Additional maintenance overhead for conversation lifecycle management
- Potential for orphaned conversation data if users are deleted

## References
- Feature specification: specs/002-chat-frontend-integration/spec.md
- Implementation plan: specs/002-chat-frontend-integration/plan.md
- Data model: specs/002-chat-frontend-integration/data-model.md
- Constitution: .specify/memory/constitution.md