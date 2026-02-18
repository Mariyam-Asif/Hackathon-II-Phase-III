# ADR-10: Agentic Technology Stack for AI-Powered Task Management

## Status
Accepted

## Date
2026-02-06

## Context
The system requires implementing an AI-powered chatbot that integrates with MCP tools for task management. The technology stack must support the stateless, deterministic architecture while enabling effective AI agent functionality. The stack needs to support the constitutional requirements of using FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, and Neon Serverless PostgreSQL.

## Decision
We will use the following technology stack:
- **Backend Framework**: FastAPI for API layer
- **AI Framework**: OpenAI Agents SDK for AI agent functionality
- **MCP Server**: Official MCP SDK for tool communication
- **ORM**: SQLModel for database interactions
- **Database**: Neon Serverless PostgreSQL for data persistence
- **Frontend**: ChatKit for user interface
- **Languages**: Python 3.11 and TypeScript/JavaScript

## Alternatives Considered

### Alternative 1: Different Backend Framework (e.g., Django, Flask)
- **Pros**: Familiarity with existing codebases, extensive ecosystem
- **Cons**: Less suitable for API-first approach, slower performance than FastAPI, less native async support
- **Rejected** because FastAPI offers superior performance, automatic API documentation, and excellent async support needed for AI agent integration

### Alternative 2: Different AI Framework (e.g., LangChain, CrewAI)
- **Pros**: Potentially more features out of the box, different abstractions
- **Cons**: May not integrate as seamlessly with MCP SDK, potential licensing issues, less control over deterministic behavior
- **Rejected** because OpenAI Agents SDK provides the most direct path to MCP integration and deterministic behavior

### Alternative 3: Different Database (e.g., MongoDB, SQLite)
- **Pros**: Different performance characteristics, potentially simpler setup
- **Cons**: Would not align with SQLModel ORM, potential schema flexibility issues, might not meet constitutional requirements
- **Rejected** because Neon Serverless PostgreSQL provides the required SQL capabilities, serverless scaling, and aligns with constitutional requirements

### Alternative 4: Different ORM (e.g., SQLAlchemy, Tortoise ORM)
- **Pros**: Familiarity with existing code, different feature sets
- **Cons**: Less integration with Pydantic models used by FastAPI, potentially more complex type handling
- **Rejected** because SQLModel provides excellent integration with Pydantic and FastAPI, reducing boilerplate code

## Consequences

### Positive
- FastAPI provides excellent performance and automatic API documentation
- OpenAI Agents SDK ensures seamless MCP integration and deterministic behavior
- SQLModel provides strong type safety with Pydantic integration
- Neon Serverless PostgreSQL offers scalable cloud-native database solution
- Modern, well-supported technology stack with active communities

### Negative
- Learning curve for team members unfamiliar with newer technologies
- Potential vendor lock-in with specific cloud services
- Some technologies may have fewer experienced developers available

## References
- Feature specification: specs/001-ai-chat-agent-mcp/spec.md
- Implementation plan: specs/001-ai-chat-agent-mcp/plan.md
- Research document: specs/001-ai-chat-agent-mcp/research.md
- Constitution: .specify/memory/constitution.md