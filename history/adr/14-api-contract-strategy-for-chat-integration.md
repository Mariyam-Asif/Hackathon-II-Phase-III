# ADR-14: API Contract Strategy for Chat Integration

## Status
Accepted

## Date
2026-02-09

## Context
The system requires defining API contracts that bridge the chat frontend with the AI agent backend while maintaining the stateless architecture and supporting MCP tool integration. The API must handle conversation management, message routing, and coordinate between the frontend, AI agent, and MCP tools. The constitution mandates clear separation of concerns and stateless-by-design architecture.

## Decision
We will implement a RESTful API with specific endpoints for chat functionality: POST /api/{user_id}/chat for processing user messages and returning AI responses with tool calls, GET /api/{user_id}/conversations for retrieving conversation history, and GET /api/{user_id}/conversations/{conversation_id} for specific conversation details. All endpoints will require JWT authentication, follow consistent error handling patterns, and maintain the stateless principle by reconstructing context from the database on each request.

## Alternatives Considered

### Alternative 1: WebSocket-based Real-time Communication
- **Pros**: More efficient for real-time chat, reduced request overhead, better for streaming responses
- **Cons**: More complex implementation, potential for server-side state storage, conflicts with stateless architecture, harder to scale
- **Rejected** because it would complicate the stateless architecture and add unnecessary complexity for the current requirements

### Alternative 2: GraphQL API
- **Pros**: More flexible querying, reduced over-fetching, single endpoint for multiple operations
- **Cons**: Steeper learning curve, additional complexity, potential performance issues with complex queries, less straightforward for event-driven chat
- **Rejected** because REST provides simpler, more predictable patterns for the chat use case

### Alternative 3: Direct AI Agent Communication
- **Pros**: Reduced API layer complexity, more direct communication
- **Cons**: Violates separation of concerns, bypasses authentication layer, potential security issues, conflicts with MCP tool architecture
- **Rejected** because it would violate the constitutional requirements for separation of concerns and deterministic AI behavior

## Consequences

### Positive
- Provides clear, predictable API contracts for frontend integration
- Maintains stateless architecture by requiring JWT authentication on each request
- Enables proper user isolation and data privacy through user_id scoping
- Supports the MCP tool integration pattern through well-defined response structures
- Enables consistent error handling and response formatting across the system

### Negative
- May result in more network requests compared to real-time protocols
- Could introduce slight latency compared to direct communication patterns
- Requires more complex error handling for network-related issues
- May require additional caching strategies for performance optimization

## References
- Feature specification: specs/002-chat-frontend-integration/spec.md
- Implementation plan: specs/002-chat-frontend-integration/plan.md
- API contracts: specs/002-chat-frontend-integration/contracts/api-contracts.yaml
- Constitution: .specify/memory/constitution.md