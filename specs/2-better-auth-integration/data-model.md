# Data Model: Better Auth Integration for Todo Web Application

## Entities

### User (Existing)
- **id**: UUID (Primary Key)
  - Type: uuid.UUID
  - Constraints: Required, Unique, Auto-generated
  - Rationale: Global uniqueness for distributed systems

- **email**: String
  - Type: str
  - Constraints: Required, Unique, Max 255 chars
  - Rationale: User identification and authentication

- **username**: String
  - Type: str
  - Constraints: Required, Unique, Max 50 chars
  - Rationale: Human-readable user identifier

- **created_at**: DateTime
  - Type: datetime
  - Constraints: Required, Auto-generated
  - Rationale: Track account creation time

- **updated_at**: DateTime
  - Type: datetime
  - Constraints: Required, Auto-generated
  - Rationale: Track last modification time

### JWT Token (Conceptual)
- **token**: String
  - Type: str
  - Constraints: Required, Encoded JWT
  - Rationale: Authentication token issued by Better Auth

- **expires_at**: DateTime
  - Type: datetime
  - Constraints: Required
  - Rationale: Token expiration time (7 days)

- **user_id**: UUID (Reference)
  - Type: uuid.UUID
  - Constraints: Required, References User.id
  - Rationale: Associate token with user identity

## Authentication Relationships

### User-Token Relationship
- **Type**: One-to-Many (conceptually)
- **Description**: Each user can have multiple active tokens (though typically one per session)
- **Rationale**: Support for multiple devices/sessions per user

## Validation Rules

### Authentication
1. **JWT Format**: Must be valid JWT format (header.payload.signature)
2. **Signature Validation**: Must be signed with the shared secret
3. **Expiration Check**: Token must not be expired
4. **User Existence**: User referenced in token must exist in database
5. **Identity Match**: User ID in JWT must match user ID in URL path

### User Entity (Additional)
1. **Email Format**: Must be valid email format
2. **Username Length**: Must be 1-50 characters
3. **Uniqueness**: Email and username must be unique across all users

## State Transitions

### Token Lifecycle
- **Initial State**: Token issued by Better Auth
- **Active State**: Valid token used for API requests
- **Expired State**: Token reaches expiration time (7 days)
- **Revoked State**: Token invalidated before expiration (future enhancement)

## Integration Points

### Better Auth Integration
- **Sign Up**: User registration handled by Better Auth
- **Sign In**: User authentication handled by Better Auth
- **Token Issue**: JWT tokens issued by Better Auth
- **Token Validation**: Backend validates JWT signature using shared secret

### API Integration
- **Header**: Authorization: Bearer {token}
- **Validation**: Per-request JWT validation
- **User Extraction**: User identity extracted from JWT claims
- **Authorization**: URL parameter vs JWT identity comparison