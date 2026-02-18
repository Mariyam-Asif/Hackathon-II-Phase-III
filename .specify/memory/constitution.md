<!-- SYNC IMPACT REPORT
Version change: 1.1.0 → 1.2.0
Modified principles:
- Progressive Enhancement (Phase-Building) → Stateless-by-design architecture
- Simplicity First (Minimal Viable Solution) → Deterministic AI behavior through explicit tool usage
- Separation of Concerns (Decoupled Architecture) → Clear separation of concerns
- Production Mindset (Best Practices) → Persistence as the single source of truth
- Extensibility (Future-Proof Design) → Agentic workflow compliance

Added sections: State Management Policy, Tool Usage Standards, Error Handling Policy
Removed sections: Phase-Specific Standards (replaced with new standards)
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ✅ updated
Follow-up TODOs: None
-->

# AI-Powered Full-Stack Todo Chatbot Constitution

## Core Principles

### I. Stateless-by-design architecture
Systems must maintain no server-side session memory between requests. All state must be managed through persistence layers or passed explicitly through API calls. This ensures scalability, reliability, and predictable behavior across distributed environments. No in-memory session state, cached user data, or transient server-side storage should persist between requests.

### II. Deterministic AI behavior through explicit tool usage
AI agents must interact with the system exclusively through defined MCP tools. All operations must follow explicit, predictable patterns with clear input/output contracts. The AI should never attempt to directly modify system state outside of approved tool interfaces. This ensures reproducible behavior and clear audit trails for all AI-driven operations.

### III. Clear separation of concerns
Maintain strict boundaries between UI layer (OpenAI ChatKit), API layer (Python FastAPI), Agent layer (OpenAI Agents SDK), MCP server layer (Official MCP SDK), and Database layer (SQLModel/Neon). Each layer must have well-defined interfaces and responsibilities without cross-layer contamination. Business logic must remain isolated from presentation and infrastructure concerns.

### IV. Persistence as the single source of truth
All system state must be stored in the database (Neon Serverless PostgreSQL) and retrieved from there. No ephemeral state should be trusted as authoritative. All operations must be designed assuming that any in-memory data is transient and unreliable. Consistency and integrity must be maintained through database-level constraints and transactions.

### V. Agentic workflow compliance
All development follows the spec → plan → tasks → implement workflow. Requirements must be clearly specified before planning, plans must precede task breakdowns, and tasks must be executed systematically. This ensures structured development and prevents ad-hoc changes that could compromise system integrity or introduce inconsistencies.

## Key Standards

### MCP Tool Standards:
- All task operations must be performed exclusively via MCP tools
- AI agent must never modify state outside MCP tools
- MCP tools must be stateless and persist data only via database
- Conversation context must be reconstructed from database on every request
- Agent responses must confirm all user-facing actions
- Errors must be handled gracefully and explained to the user
- No hidden state, in-memory caching, or implicit assumptions

### Technology Stack:
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK only
- Frontend: OpenAI ChatKit
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL

### State Management Policy:
- Server-side sessions are prohibited
- All user state must be stored in database
- Authentication state must be JWT-based with no server-side session storage
- Request-scoped data only in memory
- Cache invalidation must be explicit and tied to database changes

### Tool Usage Standards:
- MCP tools must provide clear, deterministic interfaces
- All tool operations must be logged for audit purposes
- Tool parameters must be strongly typed and validated
- Error handling must be consistent across all tools
- Tool responses must include operation status and relevant metadata

### Error Handling Policy:
- All errors must be caught and handled gracefully
- User-facing errors must be informative but not expose internal details
- System errors must be logged with sufficient context for debugging
- Recovery procedures must be defined for common failure scenarios
- Error responses must maintain API contract consistency

## Constraints

### Technical Constraints:
- Backend must use Python FastAPI framework exclusively
- AI integration limited to OpenAI Agents SDK
- MCP server implementations must use Official MCP SDK only
- Frontend restricted to OpenAI ChatKit for UI components
- ORM layer must use SQLModel with Neon Serverless PostgreSQL
- All external service integrations must be through defined APIs

### Architectural Constraints:
- No direct database access from frontend
- All data flow must go through backend APIs
- AI operations must be stateless and deterministic
- MCP tools must not maintain internal state between calls
- Authentication must be token-based with JWT
- All sensitive data must be encrypted at rest and in transit

## Development Workflow

### Code Quality Standards:
- All code must follow type hints and strong typing principles
- Module boundaries must be clearly defined and documented
- Testing must cover all MCP tool interactions
- Error handling must be comprehensive across all layers
- Documentation required for all public interfaces
- Commit messages must follow conventional format

### Quality Gates:
- All MCP tools must pass integration testing
- Type checking must pass for all components
- Security scanning required before deployment
- Performance benchmarks must be established
- Architecture compliance verified before merge

## Governance

All development must align with the stateless architecture principles and MCP tool usage standards. Changes to core principles require explicit approval and documentation of impact on system determinism and state management. Code reviews must verify compliance with tool usage standards and architectural constraints. Architectural decisions affecting state management or tool interfaces must be documented with clear rationale and trade-offs.

**Version**: 1.2.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06