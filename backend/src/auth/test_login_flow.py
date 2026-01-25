"""
Test script for login flow with Better Auth integration.
Tests the complete user login process.
"""
import asyncio
from sqlmodel import Session, create_engine
from backend.src.models.user_model import User
from backend.src.models.auth_models import UserLoginRequest
from backend.src.services.user_service import UserService
from backend.src.auth.jwt_utils import verify_better_auth_token
from backend.src.auth.token_manager import TokenManager
from backend.src.config.auth_config import auth_config
from backend.src.database.database import get_db_uri


def test_login_flow():
    print("Testing Better Auth login flow...")

    # Create a test database session
    engine = create_engine(get_db_uri())
    with Session(engine) as session:
        # Create user service
        user_service = UserService(session)

        # Create a test user first
        test_email = "login_test@example.com"
        test_username = "logintestuser"
        test_password = "securepassword123"

        print("\n1. Creating test user...")
        try:
            # Check if user already exists
            existing_user = user_service.get_user_by_email(test_email)
            if existing_user:
                # Delete existing user for clean test
                session.delete(existing_user)
                session.commit()

            # Create the test user
            test_user = user_service.create_user(
                email=test_email,
                username=test_username,
                password=test_password
            )

            print(f"   ✓ Test user created: {test_user.email}")
        except Exception as e:
            print(f"   ✗ Failed to create test user: {str(e)}")
            return False

        print("\n2. Testing user login...")
        try:
            # Test login with correct credentials
            authenticated_user = user_service.authenticate_user(test_email, test_password)

            if authenticated_user:
                print(f"   ✓ User authenticated successfully")
                print(f"   - User ID: {authenticated_user.id}")
            else:
                print(f"   ✗ User authentication failed with correct credentials")
                return False

            # Test login with incorrect password
            wrong_auth = user_service.authenticate_user(test_email, "wrongpassword")
            if wrong_auth is None:
                print(f"   ✓ Wrong password correctly rejected")
            else:
                print(f"   ✗ Wrong password incorrectly accepted")
                return False

            # Test login with non-existent user
            nonexistent_auth = user_service.authenticate_user("nonexistent@example.com", test_password)
            if nonexistent_auth is None:
                print(f"   ✓ Non-existent user correctly rejected")
            else:
                print(f"   ✗ Non-existent user incorrectly accepted")
                return False

        except Exception as e:
            print(f"   ✗ Login test failed: {str(e)}")
            return False

        print("\n3. Testing JWT token generation...")
        try:
            from backend.src.auth.auth_handler import create_access_token

            # Create token for the test user
            token_data = {"sub": str(test_user.id), "email": test_user.email, "username": test_user.username}
            access_token = create_access_token(token_data)

            print(f"   ✓ Access token generated: {access_token[:30]}...")

            # Validate the token
            validated_token = verify_better_auth_token(access_token)
            if validated_token:
                print(f"   ✓ Token validated successfully")
                print(f"   - User ID in token: {validated_token.user_id}")
                assert str(test_user.id) == validated_token.user_id, "User ID should match"
                print(f"   ✓ User ID matches between user and token")
            else:
                print(f"   ✗ Token validation failed")
                return False

        except Exception as e:
            print(f"   ✗ JWT token test failed: {str(e)}")
            return False

        print("\n4. Testing token refresh functionality...")
        try:
            # Initialize token manager
            token_mgr = TokenManager()

            # Create a refresh token
            refresh_token = token_mgr.create_refresh_token(str(test_user.id))
            print(f"   ✓ Refresh token created: {refresh_token[:30]}...")

            # Validate the refresh token
            is_valid = token_mgr.validate_refresh_token(refresh_token)
            if is_valid:
                print(f"   ✓ Refresh token validation successful")
            else:
                print(f"   ✗ Refresh token validation failed")
                return False

            # Use refresh token to get new access token
            new_access_token = token_mgr.refresh_access_token(refresh_token)
            if new_access_token:
                print(f"   ✓ New access token obtained via refresh: {new_access_token[:30]}...")

                # Validate the new access token
                new_token_validated = verify_better_auth_token(new_access_token)
                if new_token_validated:
                    print(f"   ✓ New access token validated successfully")
                    assert str(test_user.id) == new_token_validated.user_id, "User ID should match"
                    print(f"   ✓ User ID matches in refreshed token")
                else:
                    print(f"   ✗ New access token validation failed")
                    return False
            else:
                print(f"   ✗ Failed to refresh access token")
                return False

        except Exception as e:
            print(f"   ✗ Token refresh test failed: {str(e)}")
            return False

        print(f"\n✓ All login flow tests passed!")
        return True


if __name__ == "__main__":
    test_login_flow()