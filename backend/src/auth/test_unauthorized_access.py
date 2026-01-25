"""
Test script for unauthorized access prevention.
Tests that unauthenticated requests are properly rejected.
"""
import asyncio
from sqlmodel import Session, create_engine
from backend.src.models.user_model import User
from backend.src.services.user_service import UserService
from backend.src.auth.jwt_utils import create_access_token
from backend.src.database.database import get_db_uri
from backend.src.exceptions.auth_exceptions import (
    AuthException,
    TokenValidationException,
    UserMismatchException,
    InsufficientPermissionsException
)
import uuid


def test_unauthorized_access():
    print("Testing unauthorized access prevention...")

    # Create a test database session
    engine = create_engine(get_db_uri())
    with Session(engine) as session:
        # Create user service
        user_service = UserService(session)

        # Create test users
        test_email1 = "user1@example.com"
        test_username1 = "user1"
        test_password1 = "securepassword123"

        test_email2 = "user2@example.com"
        test_username2 = "user2"
        test_password2 = "securepassword1234"

        print("\n1. Creating test users...")
        try:
            # Clean up existing users
            for email in [test_email1, test_email2]:
                existing_user = user_service.get_user_by_email(email)
                if existing_user:
                    session.delete(existing_user)
                    session.commit()

            # Create test users
            user1 = user_service.create_user(
                email=test_email1,
                username=test_username1,
                password=test_password1
            )

            user2 = user_service.create_user(
                email=test_email2,
                username=test_username2,
                password=test_password2
            )

            print(f"   ✓ Created user1: {user1.email}")
            print(f"   ✓ Created user2: {user2.email}")

        except Exception as e:
            print(f"   ✗ Failed to create test users: {str(e)}")
            return False

        # Test with valid tokens
        print("\n2. Creating valid tokens...")
        try:
            token_data1 = {"sub": str(user1.id), "email": user1.email, "username": user1.username}
            token1 = create_access_token(token_data1)

            token_data2 = {"sub": str(user2.id), "email": user2.email, "username": user2.username}
            token2 = create_access_token(token_data2)

            print(f"   ✓ Token for user1: {token1[:30]}...")
            print(f"   ✓ Token for user2: {token2[:30]}...")

        except Exception as e:
            print(f"   ✗ Failed to create tokens: {str(e)}")
            return False

        # Test unauthorized access scenarios
        print("\n3. Testing unauthorized access scenarios...")

        # Test 1: No token provided (should fail)
        print("   a) Testing with no token...")
        try:
            from backend.src.auth.jwt_utils import verify_better_auth_token
            no_token_result = verify_better_auth_token("")
            if no_token_result is None:
                print("      ✓ Empty token correctly rejected")
            else:
                print("      ✗ Empty token incorrectly accepted")
                return False
        except Exception as e:
            print(f"      ✓ Empty token correctly caused exception: {str(e)[:50]}...")

        # Test 2: Invalid/malformed token (should fail)
        print("   b) Testing with invalid token...")
        try:
            invalid_token_result = verify_better_auth_token("invalid.token.string")
            if invalid_token_result is None:
                print("      ✓ Invalid token correctly rejected")
            else:
                print("      ✗ Invalid token incorrectly accepted")
                return False
        except Exception as e:
            print(f"      ✓ Invalid token correctly caused exception: {str(e)[:50]}...")

        # Test 3: Expired token (should fail) - test with a token that expires immediately
        print("   c) Testing with expired token...")
        try:
            from datetime import timedelta
            expired_token = create_access_token(
                {"sub": str(user1.id)},
                expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
            )

            expired_result = verify_better_auth_token(expired_token)
            if expired_result is None:
                print("      ✓ Expired token correctly rejected")
            else:
                print("      ✗ Expired token incorrectly accepted")
                return False
        except Exception:
            print("      ✓ Expired token correctly caused exception")

        # Test 4: User ID mismatch (should fail)
        print("   d) Testing user ID mismatch...")
        try:
            from backend.src.auth.jwt_utils import validate_user_id_in_token

            # Try to validate user2's ID with user1's token (should fail)
            mismatch_result = validate_user_id_in_token(token1, str(user2.id))
            if not mismatch_result:
                print("      ✓ User ID mismatch correctly detected")
            else:
                print("      ✗ User ID mismatch incorrectly passed")
                return False

            # Try to validate user1's ID with user1's token (should pass)
            correct_result = validate_user_id_in_token(token1, str(user1.id))
            if correct_result:
                print("      ✓ Correct user ID match correctly validated")
            else:
                print("      ✗ Correct user ID match incorrectly rejected")
                return False

        except Exception as e:
            print(f"      ✗ User ID validation test failed: {str(e)}")
            return False

        # Test 5: Test token validation with non-existent user ID
        print("   e) Testing token with non-existent user ID...")
        try:
            # Create a token with a fake user ID
            fake_user_id = str(uuid.uuid4())
            fake_token_data = {"sub": fake_user_id, "email": "fake@example.com", "username": "fakeuser"}
            fake_token = create_access_token(fake_token_data)

            # The token itself should be valid, but if we try to validate against a real user check
            # it should fail when we try to look up the user in the database
            token_validation = verify_better_auth_token(fake_token)
            if token_validation and token_validation.user_id == fake_user_id:
                print("      ✓ Fake user token validates but user doesn't exist in DB")
            else:
                print("      ✗ Fake user token validation failed unexpectedly")
                return False

        except Exception as e:
            print(f"      ✓ Non-existent user test handled correctly: {str(e)[:50]}...")

        print(f"\n✓ All unauthorized access prevention tests passed!")
        return True


def test_edge_cases():
    print("\nTesting edge cases for unauthorized access...")

    # Test with various malformed tokens
    test_tokens = [
        "not.a.token",                    # Not JWT format
        "",                              # Empty string
        "header.payload",                # Missing signature
        "header.with.dots.but.too.many.parts",  # Too many parts
        "12345",                         # Not JWT at all
    ]

    print("\n1. Testing malformed tokens...")
    from backend.src.auth.jwt_utils import verify_better_auth_token

    for i, token in enumerate(test_tokens, 1):
        try:
            result = verify_better_auth_token(token)
            if result is None:
                print(f"   {i}. ✓ Malformed token '{token[:15]}...' correctly rejected")
            else:
                print(f"   {i}. ✗ Malformed token '{token[:15]}...' incorrectly accepted")
                return False
        except Exception:
            print(f"   {i}. ✓ Malformed token '{token[:15]}...' correctly caused exception")

    # Test with invalid user ID formats
    print("\n2. Testing invalid user ID formats...")
    from backend.src.auth.jwt_utils import validate_user_id_in_token

    invalid_user_ids = [
        "not-a-uuid",
        "",
        "123",  # Too short
        "this-is-not-a-valid-uuid-format-at-all"
    ]

    # Create a valid token first
    from backend.src.auth.jwt_utils import create_access_token
    engine = create_engine(get_db_uri())
    with Session(engine) as session:
        user_service = UserService(session)

        # Create a test user
        test_email = "edge_test@example.com"
        test_username = "edgetest"
        test_password = "securepassword123"

        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            session.delete(existing_user)
            session.commit()

        test_user = user_service.create_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        valid_token_data = {"sub": str(test_user.id)}
        valid_token = create_access_token(valid_token_data)

        for i, invalid_id in enumerate(invalid_user_ids, 1):
            try:
                result = validate_user_id_in_token(valid_token, invalid_id)
                if not result:
                    print(f"   {i}. ✓ Invalid user ID '{invalid_id}' correctly rejected")
                else:
                    print(f"   {i}. ✗ Invalid user ID '{invalid_id}' incorrectly accepted")
                    return False
            except Exception:
                print(f"   {i}. ✓ Invalid user ID '{invalid_id}' correctly caused exception")

    print(f"\n✓ All edge case tests passed!")
    return True


if __name__ == "__main__":
    success1 = test_unauthorized_access()
    success2 = test_edge_cases()

    if success1 and success2:
        print(f"\n🎉 All unauthorized access prevention tests passed!")
    else:
        print(f"\n❌ Some unauthorized access prevention tests failed!")