# ADR-11: Data Model and Task Storage Strategy

## Status
Accepted

## Date
2026-02-06

## Context
The system requires storing user tasks with rich metadata while maintaining data integrity, performance, and security. The data model must support the five core operations (add, list, complete, update, delete) through MCP tools while ensuring proper user isolation and audit capabilities. The constitution requires persistence as the single source of truth.

## Decision
We will implement a data model with two core entities:
- **Task Entity**: Contains id, user_id, title, description, status (pending/in_progress/completed), timestamps, due_date, and priority (low/medium/high/urgent)
- **User Entity**: Contains id, email, name, timestamps, and active status
With relationships: One User has many Tasks (foreign key: Task.user_id references User.id)

Storage strategy: Neon Serverless PostgreSQL with indexes on user_id for efficient queries, proper validation rules, and state transition constraints.

## Alternatives Considered

### Alternative 1: Single Combined Entity with Polymorphic Types
- **Pros**: Potentially simpler schema
- **Cons**: Would complicate queries, reduce type safety, make validation more complex
- **Rejected** because separate entities provide cleaner separation of concerns and better type safety

### Alternative 2: Document-Based Storage (e.g., MongoDB)
- **Pros**: Flexible schema, potential for easier evolution
- **Cons**: Would not align with SQLModel ORM, potential for inconsistent data, lack of built-in relational constraints
- **Rejected** because relational storage better supports the required constraints and user isolation requirements

### Alternative 3: Denormalized Storage with Embedded Relations
- **Pros**: Potentially faster reads for certain queries
- **Cons**: Would complicate updates, increase storage redundancy, violate normalization principles
- **Rejected** because normalized relations better support the required user isolation and data integrity

### Alternative 4: Soft Deletes Instead of Hard Deletes
- **Pros**: Preserves historical data, allows for undeletion
- **Cons**: Complicates queries, increases storage requirements, adds complexity to user data management
- **Rejected** because hard deletes align with user expectations for task management and simplify the data model

## Consequences

### Positive
- Clear separation between user and task entities enables proper isolation
- Proper indexing ensures efficient queries by user and status
- Validation rules enforce data integrity at the database level
- Status enum and transition constraints ensure consistent state management
- Foreign key relationships maintain referential integrity
- Aligns with constitutional requirement of persistence as single source of truth

### Negative
- Requires JOIN operations for user-task queries
- More complex schema than denormalized alternatives
- Fixed schema may require migrations for future changes
- Additional complexity in handling user isolation at the application level

## References
- Feature specification: specs/001-ai-chat-agent-mcp/spec.md
- Implementation plan: specs/001-ai-chat-agent-mcp/plan.md
- Data model document: specs/001-ai-chat-agent-mcp/data-model.md
- Research document: specs/001-ai-chat-agent-mcp/research.md
- Constitution: .specify/memory/constitution.md