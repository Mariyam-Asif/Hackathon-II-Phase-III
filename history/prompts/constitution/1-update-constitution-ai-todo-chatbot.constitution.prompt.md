---
id: 1
title: update-constitution-ai-todo-chatbot
stage: constitution
date_iso: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: ai-todo-chatbot
branch: main
user: mariy
command: /sp.constitution
labels: ["constitution", "governance", "standards"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - .specify/memory/constitution.md
tests_yaml: |
  - constitution update validation
outcome: |
  Constitution updated to reflect AI-Powered Full-Stack Todo Chatbot project with stateless architecture, deterministic AI behavior, and MCP tool standards
evaluation: |
  Successfully updated constitution to align with Phase III requirements and new project direction
---

# Prompt History Record: Constitution Update

## Original Prompt

```
/sp.constitution

Project: AI-Powered Full-Stack Todo Chatbot (Phase III)

Core principles:
- Stateless-by-design architecture (no server-side session memory)
- Deterministic AI behavior through explicit tool usage
- Clear separation of concerns (UI, API, Agent, MCP, Database)
- Persistence as the single source of truth
- Agentic workflow compliance (spec → plan → tasks → implement)

Key standards:
- All task operations must be performed exclusively via MCP tools
- AI agent must never modify state outside MCP tools
- MCP tools must be stateless and persist data only via database
- Conversation context must be reconstructed from database on every request
- Agent responses must confirm all user-facing actions
- Errors must be handled gracefully and explained to the user
- No hidden state, in-memory caching, or implicit assumptions

Constraints:
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK only
- Frontend: OpenAI ChatKit
- ORM: SQLModel
- Database: Neon Serverless
```

## Response Summary

Updated the project constitution to reflect the AI-Powered Full-Stack Todo Chatbot requirements, incorporating new core principles around stateless architecture, deterministic AI behavior, and MCP tool usage standards. The constitution now emphasizes state management policies, tool usage standards, and error handling guidelines specific to the AI-powered application architecture.

## Changes Made

- Updated core principles to reflect stateless architecture and deterministic AI behavior
- Added specific standards for MCP tool usage
- Included technology stack constraints (FastAPI, OpenAI Agents SDK, ChatKit, SQLModel, Neon)
- Defined state management, tool usage, and error handling policies
- Maintained versioning and governance structure