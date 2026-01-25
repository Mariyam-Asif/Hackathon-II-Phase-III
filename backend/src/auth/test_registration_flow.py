"""
Test script for registration flow with Better Auth integration.
Tests the complete user registration process.
"""
import asyncio
from sqlmodel import Session, create_engine
from backend.src.models.user_model import User
from backend.src.models.auth_models import UserRegistrationRequest
from backend.src.services.user_service import UserService
from backend.src.auth.jwt_utils import verify_better_auth_token
from backend.src.config.auth_config import auth_config
from backend.src.database.database import get_db_uri


def test_registration_flow():
    print("Testing Better Auth registration flow...")

    # Create a test database session
    engine = create_engine(get_db_uri())
    with Session(engine) as session:
        # Create user service
        user_service = UserService(session)

        # Test user data
        test_email = "testuser@example.com"
        test_username = "testuser123"
        test_password = "securepassword123"

        # Create registration request
        registration_data = UserRegistrationRequest(
            email=test_email,
            username=test_username,
            password=test_password
        )

        print("\n1. Creating new user...")
        try:
            # Create the user
            new_user = user_service.create_user(
                email=registration_data.email,
                username=registration_data.username,
                password=registration_data.password
            )

            print(f"   ✓ User created successfully")
            print(f"   - User ID: {new_user.id}")
            print(f"   - Email: {new_user.email}")
            print(f"   - Username: {new_user.username}")

            # Verify user was created in DB
            retrieved_user = user_service.get_user_by_email(test_email)
            assert retrieved_user is not None, "User should exist in database"
            assert retrieved_user.email == test_email, "Email should match"
            assert retrieved_user.username == test_username, "Username should match"

            print(f"   ✓ User verified in database")

            # Test authentication with created user
            print("\n2. Testing user authentication...")
            authenticated_user = user_service.authenticate_user(test_email, test_password)

            if authenticated_user:
                print(f"   ✓ User authenticated successfully")
                print(f"   - Authenticated user ID: {authenticated_user.id}")

                # Verify that non-matching password fails
                wrong_auth = user_service.authenticate_user(test_email, "wrongpassword")
                assert wrong_auth is None, "Wrong password should not authenticate"
                print(f"   ✓ Wrong password correctly rejected")
            else:
                print(f"   ✗ User authentication failed")
                return False

            # Test JWT token creation
            print("\n3. Testing JWT token creation...")
            from backend.src.auth.auth_handler import create_access_token

            token_data = {"sub": str(new_user.id), "email": new_user.email, "username": new_user.username}
            access_token = create_access_token(token_data)

            print(f"   ✓ JWT token created: {access_token[:30]}...")

            # Test token validation
            print("\n4. Testing JWT token validation...")
            validated_token = verify_better_auth_token(access_token)

            if validated_token:
                print(f"   ✓ Token validated successfully")
                print(f"   - User ID in token: {validated_token.user_id}")
                assert str(new_user.id) == validated_token.user_id, "User ID should match"
                print(f"   ✓ User ID matches between user and token")
            else:
                print(f"   ✗ Token validation failed")
                return False

            print(f"\n✓ All registration flow tests passed!")
            return True

        except Exception as e:
            print(f"   ✗ Registration test failed: {str(e)}")
            return False


if __name__ == "__main__":
    test_registration_flow()