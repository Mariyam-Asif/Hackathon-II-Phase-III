"""
Simple test script to verify JWT validation with Better Auth compatible tokens.
This script tests the basic functionality of our JWT utilities.
"""
import os
from datetime import timedelta
from backend.src.auth.jwt_utils import create_access_token, verify_better_auth_token
from backend.src.config.auth_config import auth_config

# Test token creation and validation
def test_jwt_functionality():
    print("Testing Better Auth JWT functionality...")

    # Sample user data
    sample_user_data = {
        "sub": "test-user-id-12345",
        "email": "test@example.com",
        "username": "testuser"
    }

    # Create a token
    print("\n1. Creating JWT token...")
    token = create_access_token(sample_user_data)
    print(f"   Token created: {token[:30]}...")

    # Verify the token
    print("\n2. Verifying JWT token...")
    token_data = verify_better_auth_token(token)

    if token_data:
        print(f"   Token valid: {token_data.valid}")
        print(f"   User ID: {token_data.user_id}")
        print(f"   Expires at: {token_data.exp}")
        print("   ✓ Token verification successful!")
    else:
        print("   ✗ Token verification failed!")
        return False

    # Test with invalid token
    print("\n3. Testing invalid token...")
    invalid_token_data = verify_better_auth_token("invalid.token.string")
    if invalid_token_data is None:
        print("   ✓ Invalid token correctly rejected")
    else:
        print("   ✗ Invalid token incorrectly accepted")
        return False

    print("\n✓ All JWT validation tests passed!")
    return True

if __name__ == "__main__":
    # Set up environment for testing
    os.environ.setdefault("BETTER_AUTH_SECRET", auth_config.BETTER_AUTH_SECRET)

    # Run tests
    test_jwt_functionality()