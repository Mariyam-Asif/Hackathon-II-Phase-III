# ADR-6: Data Model and Storage Strategy

## Title
Data Model and Storage Strategy: UUID-based with Soft Delete and Strategic Indexing

## Status
Accepted

## Date
2026-01-09

## Context
We need to design a data model that supports multi-user functionality, ensures data integrity, provides good performance for common operations, and allows for proper data lifecycle management. The model must work effectively with PostgreSQL and support the required API operations efficiently.

## Decision
We will implement the following data model and storage strategy:
- **Primary Keys**: UUIDs for both users and tasks to ensure global uniqueness and security
- **Relationships**: Foreign key from Task.user_id to User.id to enforce referential integrity
- **Soft Delete**: Use a 'deleted' boolean field instead of hard deletion for data recovery capabilities
- **Indexing**: Strategic indexes on user_id and task status for query performance
- **Field Constraints**: Title length limited to 100 characters, description optional

## Rationale
UUIDs provide better security by making IDs harder to guess and support global uniqueness for distributed systems. Soft delete allows for potential data recovery and maintains audit trails. Strategic indexing ensures good performance for the most common queries (filtering by user and status).

## Consequences
**Positive:**
- Enhanced security through non-sequential IDs
- Data recovery capabilities through soft delete
- Good query performance through strategic indexing
- Consistent field constraints across the system

**Negative:**
- UUIDs are less human-readable than sequential IDs
- Soft delete requires additional logic to filter out deleted records
- Slightly larger storage requirements for UUIDs vs integers

## Alternatives Considered
- **Auto-incrementing integers**: More familiar but less secure and doesn't support distributed systems well
- **Hard delete**: Simpler implementation but no recovery capability
- **No indexing**: Lower storage requirements but poor performance for large datasets
- **Unlimited title length**: More flexible but potential performance and UX issues

## References
- plan.md: Data model requirements
- research.md: Decision on primary keys, foreign keys, and indexes
- data-model.md: Complete entity specifications