# ADR-5: Backend Technology Stack

## Title
Backend Technology Stack: FastAPI with SQLModel and Neon PostgreSQL

## Status
Accepted

## Date
2026-01-09

## Context
We need to select a robust backend technology stack for the Todo application that supports multi-user functionality, provides good performance, and integrates well with the planned authentication system. The solution must support RESTful API development, have strong typing capabilities, and work well with PostgreSQL-compatible databases.

## Decision
We will use the following backend technology stack:
- **Framework**: FastAPI for its async capabilities, automatic API documentation, and Pydantic integration
- **ORM**: SQLModel for its combination of SQLAlchemy's power with Pydantic's validation
- **Database**: Neon Serverless PostgreSQL for its compatibility with PostgreSQL and serverless scaling
- **Testing**: pytest for comprehensive test coverage

## Rationale
FastAPI provides excellent performance through ASGI and automatic OpenAPI documentation. SQLModel combines the strengths of SQLAlchemy and Pydantic, allowing us to use the same models for database operations and request/response validation. Neon PostgreSQL offers PostgreSQL compatibility with serverless benefits, reducing operational overhead.

## Consequences
**Positive:**
- Fast development with automatic API documentation
- Strong typing and validation throughout the stack
- Good performance characteristics
- Easy integration with Pydantic-based validation

**Negative:**
- Learning curve for team members unfamiliar with FastAPI
- Potential complexity in deployment compared to simpler frameworks

## Alternatives Considered
- **Flask + SQLAlchemy**: More familiar but lacks automatic documentation and async support
- **Django**: More batteries-included but potentially overkill for this API-focused application
- **Node.js + Express**: Would require changing the Python focus of the project

## References
- plan.md: Technical Context section
- research.md: Decision on primary dependencies
- data-model.md: Database schema requirements