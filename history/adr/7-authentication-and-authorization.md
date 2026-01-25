# ADR-7: Authentication and Authorization

## Title
Authentication and Authorization: JWT-based with User Isolation

## Status
Accepted

## Date
2026-01-09

## Context
We need to implement a secure authentication and authorization system that ensures users can only access their own data, provides secure token management, and integrates well with the API-first architecture. The solution must support the required user isolation while maintaining good user experience.

## Decision
We will implement the following authentication and authorization approach:
- **Authentication Method**: JWT (JSON Web Tokens) via Better Auth integration
- **Authorization Model**: User-based access control where users can only access resources linked to their user_id
- **Token Management**: 7-day expiration as determined in requirements clarification
- **Security Measures**: All endpoints require valid JWT tokens, sensitive fields excluded from responses
- **Integration**: JWT validation middleware to ensure proper authentication before request processing

## Rationale
JWT tokens provide stateless authentication that works well with RESTful APIs. The user isolation model ensures data security by design - each request is validated to ensure the user can only access their own resources. Better Auth provides a secure, well-tested solution for JWT handling.

## Consequences
**Positive:**
- Stateless authentication scales well
- Strong user data isolation
- Standard JWT implementation for interoperability
- Secure by design with user-based access control

**Negative:**
- JWT token management requires careful handling of expiration
- Cannot easily invalidate individual tokens before expiration
- Additional complexity in token refresh handling

## Alternatives Considered
- **Session-based authentication**: More familiar but requires server-side state management
- **API Keys**: Simpler but less secure and doesn't support user identity well
- **OAuth 2.0**: More complex than needed for this application
- **No authentication**: Would not meet security requirements

## References
- plan.md: Security and authentication requirements
- research.md: Error handling strategy mentioning JWT
- spec.md: Clarifications section on JWT token expiration
- contracts/api-contract.md: Authentication requirements for all endpoints