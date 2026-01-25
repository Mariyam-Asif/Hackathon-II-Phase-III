---
name: auth-skill
description: Design and implement secure authentication flows including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Authentication Flows**
   - Implement secure sign-up and sign-in flows
   - Validate user input and handle authentication errors safely
   - Ensure consistent authentication behavior across frontend and backend

2. **Password Security**
   - Hash passwords using industry-standard algorithms (bcrypt or argon2)
   - Never store or transmit plaintext passwords
   - Use proper salting and secure configuration

3. **JWT Token Handling**
   - Issue JWT tokens upon successful authentication
   - Include essential user claims (id, email)
   - Enforce token expiration and signature verification
   - Send tokens via `Authorization: Bearer <token>` header

4. **Better Auth Integration**
   - Configure Better Auth on the frontend
   - Enable JWT plugin for token issuance
   - Share JWT signing secret with backend via environment variables
   - Align session lifecycle with backend token validation

5. **Backend Verification (FastAPI)**
   - Verify JWT signature and expiration on every request
   - Extract authenticated user identity from token
   - Enforce user-level data isolation
   - Return 401 Unauthorized for invalid or missing tokens

## Best Practices
- Treat authentication as a strict security boundary
- Never trust client-provided user identifiers
- Centralize authentication logic
- Rotate secrets when possible
- Log authentication failures without exposing sensitive data