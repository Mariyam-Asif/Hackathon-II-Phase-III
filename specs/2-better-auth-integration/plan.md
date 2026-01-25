# Better Auth Integration - Final Architecture Plan

## Authentication Flow

### Better Auth Integration
- Frontend: Next.js application with Better Auth client-side integration
- Better Auth handles user registration, login, and session management
- Better Auth issues JWT tokens upon successful authentication
- Frontend stores JWT tokens in secure storage (httpOnly cookies or secure localStorage)

### JWT Issuance and Storage
- Better Auth creates JWT tokens with user identity information
- JWT tokens contain user_id in the `sub` claim
- Frontend attaches JWT as `Authorization: Bearer <token>` header on protected requests
- Token refresh mechanism implemented for long-lived sessions

### FastAPI JWT Middleware
- Stateless JWT verification middleware in FastAPI application
- Middleware intercepts requests to protected endpoints
- Validates JWT signature, expiration, and user identity
- Extracts user_id from token claims for authorization checks

### Public vs Protected Routes
- Public routes: `/`, `/health`, `/docs`, `/redoc`, `/openapi.json`, `/auth/register`, `/auth/login`, `/auth/validate-token`
- Protected routes: All `/api/{user_id}/tasks/*` endpoints
- Middleware enforces authentication on protected routes

## JWT Design

### Required Payload Fields
- `sub`: User ID (UUID string) - identifies the authenticated user
- `exp`: Expiration timestamp - Unix timestamp for token expiration
- `iat`: Issued at timestamp - Unix timestamp when token was created
- `jti`: JWT ID (optional) - unique identifier for the token
- `aud`: Audience (optional) - intended recipients of the token
- `iss`: Issuer (optional) - entity that issued the token

### Expiration Rules
- Default token expiration: 7 days (604800 seconds)
- Configurable via `JWT_EXPIRATION_DELTA` environment variable
- Tokens automatically expire after the specified duration
- No server-side session storage - relies on JWT expiration

### Signature Algorithm
- Algorithm: HS256 (HMAC with SHA-256)
- Configurable via `JWT_ALGORITHM` environment variable
- Uses shared secret for signing and verification

### Shared Secret Usage
- `BETTER_AUTH_SECRET` environment variable stores the shared secret
- Secret used for both signing and verifying JWT tokens
- Must be kept secure and consistent between frontend and backend
- Default fallback secret for development environments

## Database (Neon PostgreSQL)

### Users Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Tasks Schema
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(100) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    deleted BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### User ↔ Task Relationship
- One-to-many relationship: One user can have many tasks
- Foreign key constraint ensures referential integrity
- `ON DELETE CASCADE` ensures tasks are removed when user is deleted
- `user_id` indexed for efficient queries

### Strict User-Scoped Query Rules
- All task queries must filter by authenticated user's ID
- Task creation: Only create tasks for authenticated user
- Task retrieval: Only return tasks belonging to authenticated user
- Task modification: Only allow updates to tasks owned by authenticated user
- Task deletion: Only allow deletion of tasks owned by authenticated user

## Security Guarantees

### Stateless Authentication
- No server-side session storage required
- JWT tokens contain all necessary authentication information
- Scalable authentication without shared session state
- Tokens are self-contained with user identity and expiration

### No Session Storage
- Authentication relies entirely on JWT validation
- No database lookups for token validation
- Faster authentication with reduced database load
- Stateless design enables horizontal scaling

### User Data Isolation
- Each user can only access their own data
- User ID verification between token claims and URL parameters
- Comprehensive authorization checks on all protected endpoints
- Prevents unauthorized cross-user data access

### Protection Against Common Attacks
- Rate limiting on authentication endpoints to prevent brute force
- Secure token storage and transmission
- Proper error handling without information leakage
- CORS policies to prevent cross-site request forgery

## Implementation Requirements

### Frontend Integration
- Next.js application with Better Auth client integration
- Secure token storage and management
- Automatic token attachment to API requests
- Proper error handling for authentication failures

### Backend Integration
- JWT validation middleware for protected endpoints
- User ID verification in all data access operations
- Comprehensive error handling and validation
- Proper logging and monitoring of authentication events

### Environment Configuration
Required environment variables:
```
BETTER_AUTH_SECRET="your-secret-key-for-jwt-validation"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_DELTA=604800  # 7 days in seconds
```

### Testing Strategy
- Unit tests for JWT validation functions
- Integration tests for authentication flow
- End-to-end tests for user data isolation
- Security tests for authorization bypass attempts