# Migration Guide: From Legacy Auth to Better Auth System

This document provides guidance for migrating from the legacy authentication system to the Better Auth integration.

## Overview

This guide covers the migration process from the previous authentication implementation to the new Better Auth-based system with JWT token validation.

## Key Changes

### 1. Authentication Method
- **Before**: Custom authentication system with basic token handling
- **After**: Standard JWT tokens issued by Better Auth with proper validation

### 2. Token Format and Validation
- **Before**: Simple tokens with basic validation
- **After**: Proper JWT tokens with header.payload.signature format, validated using secret key

### 3. User Access Control
- **Before**: Basic user ID comparison
- **After**: Enhanced user validation with proper token-user ID matching and error handling

## Migration Steps

### Step 1: Update Backend Dependencies

1. Update requirements.txt to include Better Auth dependencies
2. Update environment variables to include Better Auth configuration:
   ```bash
   BETTER_AUTH_SECRET="your-secret-key-for-jwt-validation"
   JWT_ALGORITHM="HS256"
   JWT_EXPIRATION_DELTA=604800  # 7 days in seconds
   ```

### Step 2: Update Authentication Handler

1. Replace legacy auth_handler.py with new implementation that uses Better Auth standards
2. Update token creation and validation functions to use JWT format
3. Ensure proper error handling for invalid tokens

### Step 3: Update API Routes

1. Ensure all protected endpoints require JWT tokens in Authorization header
2. Update dependency injection to use new authentication functions
3. Update error responses to follow standard format

### Step 4: Update User Service

1. Update user creation and authentication methods to work with JWT system
2. Ensure password hashing remains consistent
3. Update user retrieval methods to work with new authentication flow

### Step 5: Update Middlewares

1. Add authentication middleware for global token validation
2. Add rate limiting middleware for authentication endpoints
3. Update security headers for enhanced protection

## Breaking Changes

### 1. API Authentication Headers
- **Before**: Various authentication methods
- **After**: All authenticated endpoints require `Authorization: Bearer <token>`

### 2. Error Responses
- **Before**: Basic error messages
- **After**: Standardized error format with error code and timestamp

### 3. Token Expiration
- **Before**: Possibly no token expiration
- **After**: All tokens have configurable expiration (default 7 days)

## Code Migration Examples

### 1. Client-Side API Calls
```javascript
// Before
fetch('/api/tasks', {
  headers: {
    'Authorization': `Token ${legacyToken}`
  }
});

// After
fetch('/api/userId/tasks', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  }
});
```

### 2. Token Validation
```python
# Before
def validate_token(token):
    # Simple validation
    return token in valid_tokens

# After
def validate_token(token):
    from backend.src.auth.jwt_utils import verify_better_auth_token
    return verify_better_auth_token(token)
```

## Data Migration

### User Data
- User accounts remain unchanged
- Password hashes remain compatible
- No data transformation required

### Token Data
- Legacy tokens will become invalid after migration
- Users will need to re-authenticate after deployment

## Testing the Migration

### 1. Pre-Migration Testing
- Verify backup of existing authentication data
- Test new authentication system in isolated environment
- Validate token creation and validation

### 2. Migration Testing
- Test user registration with new system
- Test user login and token acquisition
- Test API access with JWT tokens
- Verify user isolation and access controls

### 3. Post-Migration Testing
- Verify all protected endpoints require valid JWT tokens
- Test error handling for invalid/missing tokens
- Validate rate limiting functionality
- Confirm security headers are applied

## Rollback Plan

If issues arise during migration:

1. Revert to previous version of auth_handler.py
2. Restore previous requirements.txt
3. Remove new middleware configurations
4. Revert environment variable changes

## Deployment Checklist

- [ ] Update environment variables with Better Auth secrets
- [ ] Deploy new authentication handlers
- [ ] Update API routes with new authentication dependencies
- [ ] Deploy middleware updates
- [ ] Test authentication flow end-to-end
- [ ] Verify error handling
- [ ] Monitor authentication metrics
- [ ] Update documentation for frontend teams

## Troubleshooting Common Issues

### 1. Invalid Token Errors
- Verify `BETTER_AUTH_SECRET` is correctly set
- Check that tokens are being sent with `Bearer ` prefix
- Validate token format (header.payload.signature)

### 2. User Access Issues
- Confirm user ID in token matches URL parameter
- Verify user exists in database
- Check UUID formatting

### 3. Rate Limiting Issues
- Verify rate limiter configuration
- Check IP address detection in headers
- Adjust limits as needed for legitimate traffic

## Support Resources

- Authentication API documentation
- Error code reference
- Security best practices guide
- Frontend integration documentation