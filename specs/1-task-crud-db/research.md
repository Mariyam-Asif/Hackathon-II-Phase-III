# Research: Todo App Phase II - Task CRUD & Database Integration

## Decision: Primary Keys, Foreign Keys, and Indexes
**Rationale**: Following SQLModel best practices with Neon PostgreSQL, we'll use UUID primary keys for both users and tasks to ensure global uniqueness. Foreign key from task.user_id to user.id will enforce referential integrity. Indexes on user_id and task status will support the required filtering performance.

**Alternatives considered**:
- Auto-incrementing integers (rejected for scalability concerns in distributed systems)
- String-based IDs (rejected for lack of uniqueness guarantees)

## Decision: Task Model Fields and Constraints
**Rationale**: Based on spec requirements, the Task model will include:
- id: UUID (primary key)
- title: str (max 100 chars, required)
- description: str (optional)
- completed: bool (default False)
- deleted: bool (default False, for soft delete)
- user_id: UUID (foreign key to User)
- created_at: datetime
- updated_at: datetime

**Alternatives considered**:
- Different field types (rejected to maintain consistency with Neon PostgreSQL capabilities)
- Additional computed fields (rejected as not required by spec)

## Decision: Response and Request Pydantic Models
**Rationale**: Create separate Pydantic models for different operations:
- TaskCreate: title, description (optional)
- TaskUpdate: title (optional), description (optional), completed (optional)
- TaskResponse: all fields except user_id (for security)
- ErrorResponse: follows spec { "error": "message", "code": "error_code", "details": {} }

**Alternatives considered**:
- Single model for all operations (rejected for lack of specificity)
- Different field naming conventions (rejected to maintain consistency)

## Decision: Pagination or Filtering Approach for GET Endpoints
**Rationale**: Implement basic pagination with offset/limit parameters for GET /api/{user_id}/tasks to handle large datasets efficiently. Add query parameters for filtering by completion status.

Parameters:
- limit: int (default 50, max 100)
- offset: int (default 0)
- completed: bool (optional, to filter by completion status)

**Alternatives considered**:
- Cursor-based pagination (rejected as unnecessarily complex for this phase)
- No pagination (rejected as it wouldn't handle large datasets properly)

## Decision: Error Handling Strategy
**Rationale**: Use FastAPI's exception handlers to return standardized error responses in the format specified by the spec: { "error": "message", "code": "error_code", "details": {} }. Implement proper HTTP status codes (400 for validation errors, 401 for auth issues, 403 for access denied, 404 for not found).

**Alternatives considered**:
- Different error response formats (rejected as it wouldn't meet spec requirements)
- Generic error responses (rejected as it wouldn't provide adequate debugging info)

## Decision: JWT-based Authentication with Better Auth Integration

**Rationale**: JWT (JSON Web Tokens) provide stateless authentication that scales well with the microservice architecture anticipated for future phases. Better Auth integration ensures secure token issuance and management while maintaining separation of concerns between authentication and business logic.

## Key Architecture Decisions

### 1. JWT vs Session Authentication
**Decision**: JWT Stateless Authentication
**Rationale**:
- Scales horizontally without shared session storage
- Aligns with REST principles (stateless operations)
- Supports the anticipated microservice architecture for future phases
- Better Auth naturally integrates with JWT tokens

### 2. JWT Validation Location
**Decision**: Dependency Injection Approach
**Rationale**:
- Provides fine-grained control over authentication per endpoint
- Enables custom validation logic for different user permissions
- Maintains clear separation between authentication and business logic
- Leverages FastAPI's built-in dependency injection system

### 3. User Identity Source
**Decision**: JWT Claims with URL Parameter Verification
**Rationale**:
- JWT claims provide authenticated user identity
- URL parameters (user_id) must match JWT identity for authorization
- Prevents users from accessing other users' resources
- Implements defense in depth for user isolation

### 4. Token Expiry Strategy
**Decision**: 7-Day Expiration with Refresh Capability
**Rationale**:
- Balances security (short-lived tokens) with usability
- Reduces exposure window if tokens are compromised
- Aligns with the security requirements in the spec

## API Protection Strategy

### Middleware vs Dependency Injection
- **Dependency Injection**: Used for endpoint-specific authentication requirements
- **Middleware**: Used for global authentication concerns (token format validation)

### Validation Rules
1. All requests must include valid JWT in Authorization header
2. JWT signature must be verified using shared secret
3. Token must not be expired
4. User ID in JWT must match user ID in URL path
5. User must exist in database

## Testing Strategy

### Authentication Tests
- Requests without JWT return 401 Unauthorized
- Invalid or expired JWT returns 401 Unauthorized
- JWT user_id mismatch with URL user_id returns 403 Forbidden
- Valid JWT with matching user_id grants access to user's own tasks only

## Technical Implementation

### Frontend Integration
- Better Auth manages JWT lifecycle
- Frontend attaches Authorization: Bearer {token} header to API requests
- Secure token storage and renewal handled by Better Auth

### Backend Integration
- FastAPI dependencies validate JWT tokens
- Shared secret for signature verification
- User identity extracted from token claims
- Authorization checks compare JWT identity with URL parameters

## Alternatives Considered

1. **Session-based Authentication**: Rejected due to scalability concerns and violation of statelessness requirement
2. **API Keys**: Rejected as they don't provide user identity or support the required authorization model
3. **OAuth2 Password Flow**: Rejected as Better Auth provides superior security and user experience