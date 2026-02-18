# Implementation Plan: AI-Powered Todo Chatbot

**Feature**: AI-Powered Todo Chatbot
**Branch**: 002-chat-frontend-integration
**Created**: 2026-02-09
**Status**: Draft

## Technical Context

### Architecture Overview
- **Frontend**: OpenAI ChatKit for chat interface
- **Backend**: Python FastAPI API server
- **AI Agent**: OpenAI Agents SDK
- **MCP Server**: Official MCP SDK
- **Database**: Neon Serverless PostgreSQL with SQLModel
- **Authentication**: Better Auth with JWT tokens

### State Management Policy
- **Stateless architecture**: No server-side session memory between requests
- **Database as source of truth**: All state stored in Neon PostgreSQL
- **Request-scoped data**: Only temporary in-memory data per request

### Tool Usage Standards
- **MCP Tools**: Exclusive interface for AI to interact with system
- **Deterministic Operations**: All operations through explicit tool contracts
- **No Direct Access**: AI agent cannot modify state outside MCP tools

### Current Unknowns
- None (all previously identified unknowns have been researched and resolved)

## Constitution Check

### Compliance Verification
- ✓ Stateless-by-design architecture: Server maintains no session memory between requests
- ✓ Deterministic AI behavior: AI interacts only through defined MCP tools
- ✓ Clear separation of concerns: UI, API, Agent, MCP, and Database layers are distinct
- ✓ Persistence as single source of truth: All state stored in database
- ✓ Agentic workflow compliance: Following spec → plan → tasks → implement sequence

### Potential Violations
- [x] None identified

### Gate Status
- [x] All constitution principles verified as compliant
- [x] No unjustified violations identified

---

## Phase 0: Research & Discovery

### research.md

#### Decision: MCP Tool Architecture
**Rationale**: MCP (Model Context Protocol) server will serve as the standardized interface between the AI agent and the todo application, ensuring deterministic and secure interactions.

**Alternatives considered**:
- Direct API calls from AI agent (violates tool usage standards)
- Custom tool protocol (increases complexity and reduces standardization)

#### Decision: State Management Approach
**Rationale**: Stateless architecture with database as the single source of truth ensures scalability and reliability across distributed environments.

**Alternatives considered**:
- Server-side session storage (violates stateless principle)
- Client-side state with server synchronization (compromises data integrity)

#### Decision: Frontend Technology
**Rationale**: OpenAI ChatKit provides a proven, minimal chat interface that focuses on functionality rather than styling, aligning with the project's goals.

**Alternatives considered**:
- Custom-built chat interface (increases development time)
- Third-party chat libraries (potential compatibility issues)

#### Decision: AI Agent Configuration
**Rationale**: Using OpenAI Agents SDK with function calling allows for deterministic tool usage and clear input/output contracts.

**Alternatives considered**:
- Raw OpenAI API calls (less structured tool usage)
- Alternative AI frameworks (potential compatibility issues with MCP)

---

## Phase 1: Design & Contracts

### data-model.md

#### Conversation Entity
- **conversation_id**: UUID, primary key
- **user_id**: UUID, foreign key to user table
- **created_at**: DateTime, timestamp of creation
- **updated_at**: DateTime, timestamp of last activity
- **title**: String, conversation title (derived from first message)

#### Message Entity
- **message_id**: UUID, primary key
- **conversation_id**: UUID, foreign key to conversation
- **sender_type**: Enum ('user'|'agent'), type of sender
- **content**: Text, message content
- **timestamp**: DateTime, when message was sent
- **status**: Enum ('sent'|'pending'|'error'), delivery status
- **parent_message_id**: UUID, reference to parent message for threading

#### User Entity
- **user_id**: UUID, primary key
- **email**: String, user email address
- **created_at**: DateTime, account creation timestamp
- **updated_at**: DateTime, last update timestamp

### API Contracts

#### POST /api/{user_id}/chat
- **Description**: Process user message and return AI response
- **Request Body**:
  - `message`: String, user message content
  - `conversation_id`: UUID (optional), existing conversation ID
- **Response**:
  - `conversation_id`: UUID, conversation identifier
  - `response`: String, AI agent response
  - `tool_calls`: Array, any tools called by agent
- **Authentication**: JWT token required

#### GET /api/{user_id}/conversations
- **Description**: Retrieve user's conversation history
- **Response**: Array of conversation summaries
- **Authentication**: JWT token required

#### GET /api/{user_id}/conversations/{conversation_id}
- **Description**: Retrieve specific conversation history
- **Response**: Array of messages in chronological order
- **Authentication**: JWT token required

### quickstart.md

# Quick Start: AI-Powered Todo Chatbot

## Prerequisites
- Python 3.9+
- Node.js 18+
- Neon PostgreSQL account
- OpenAI API key
- Better Auth configuration

## Setup

### Backend
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export DATABASE_URL="your_neon_postgres_url"
   export OPENAI_API_KEY="your_openai_key"
   export BETTER_AUTH_SECRET="your_auth_secret"
   ```

3. Run database migrations:
   ```bash
   python -m backend.src.database.migrate
   ```

4. Start the backend:
   ```bash
   uvicorn backend.src.main:app --reload
   ```

### Frontend
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Configure environment variables:
   ```bash
   NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
   NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:8000"
   ```

3. Start the frontend:
   ```bash
   npm run dev
   ```

### MCP Server
1. Navigate to the MCP server directory
2. Install required dependencies
3. Start the MCP server:
   ```bash
   python mcp_server.py
   ```

## Usage
1. Visit the frontend application
2. Log in with your credentials
3. Start chatting with the AI agent to manage your todos
4. The AI will use MCP tools to interact with your todo list

---

## Phase 2: Implementation Preparation

### Agent Context Update

The agent context has been updated to include the following technologies and standards:

- MCP (Model Context Protocol) server implementation
- OpenAI Agents SDK configuration
- FastAPI backend patterns
- SQLModel database operations
- Better Auth integration
- ChatKit frontend integration
- Statelessness principles
- Deterministic tool usage patterns

---

## Phase 3: Execution Strategy

### Implementation Order
1. MCP Server with defined tools
2. AI Agent configuration and integration
3. Backend API endpoints
4. Database models and operations
5. Frontend ChatKit integration
6. Authentication integration
7. Testing and validation

### Risk Mitigation
- Implement MCP tools first to validate AI interaction patterns
- Use feature flags for gradual rollout
- Implement comprehensive error handling
- Monitor performance and usage patterns

### Success Metrics
- All UI → API → Agent → MCP → DB → UI loops function correctly
- Frontend is completely dependent on backend (no local state)
- Conversation recovery works after server restart
- Intent-to-tool mapping functions correctly through UI interactions