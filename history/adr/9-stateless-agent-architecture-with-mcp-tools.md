# ADR-9: Stateless Agent Architecture with MCP Tools as Primary Mutation Layer

## Status
Accepted

## Date
2026-02-06

## Context
The system requires an AI-powered chatbot that interprets natural language user requests and performs task management operations. The architecture must ensure deterministic behavior, scalability, and clear audit trails while maintaining security and reliability. The constitution mandates stateless-by-design architecture and deterministic AI behavior through explicit tool usage.

## Decision
We will implement a stateless agent architecture where the AI agent operates deterministically through defined MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) rather than direct database manipulation. All task operations must be performed exclusively via MCP tools, with the agent operating statelessly per request and conversation history reconstructed from the database on every request.

## Alternatives Considered

### Alternative 1: Direct Database Access from Agent
- **Pros**: Simpler implementation, fewer layers of indirection
- **Cons**: Violates constitution principles, lacks audit trail, potential for inconsistent state management, bypasses business logic validation
- **Rejected** because it violates the constitutional requirement for deterministic AI behavior through explicit tool usage

### Alternative 2: Mixed Approach with Direct and Tool-Based Operations
- **Pros**: Could offer performance benefits for certain operations
- **Cons**: Creates inconsistency in the system, harder to maintain, violates principle of least surprise, potential security risks
- **Rejected** because it would create inconsistency and violate the deterministic behavior requirement

### Alternative 3: Server-Side Session Storage
- **Pros**: Could provide better performance for repeated interactions
- **Cons**: Violates constitutional prohibition on server-side session storage, reduces scalability, creates single points of failure
- **Rejected** because it violates the stateless-by-design architecture principle

## Consequences

### Positive
- Ensures deterministic behavior with clear audit trails for all AI-driven operations
- Maintains scalability through stateless operation
- Provides clear separation of concerns between AI agent and data management
- Enables consistent business logic enforcement through MCP tools
- Aligns with constitutional principles of stateless architecture

### Negative
- Potential performance overhead from reconstructing conversation history on each request
- Additional complexity in implementing MCP tools
- Possible increased latency for operations requiring multiple tool calls

## References
- Feature specification: specs/001-ai-chat-agent-mcp/spec.md
- Implementation plan: specs/001-ai-chat-agent-mcp/plan.md
- Research document: specs/001-ai-chat-agent-mcp/research.md
- Constitution: .specify/memory/constitution.md