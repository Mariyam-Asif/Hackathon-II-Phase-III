
import os
import sys
import uuid
from sqlmodel import Session, SQLModel, create_engine

# Add src to path
sys.path.insert(0, os.path.abspath("backend/src"))

# Import all models to resolve relationships
from models.user import User
from models.task import Task
from models.conversation import Conversation
from models.message import Message
from models.auth_models import UserRegistrationRequest, UserLoginRequest
from services.user_service import UserService

# Use SQLite for local verification of logic
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

def test_auth_logic():
    print("Testing auth logic...")
    with Session(engine) as session:
        user_service = UserService(session)
        
        # 1. Test registration
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        password = "testpassword123"
        name = "Test User"
        
        print(f"Registering {email}...")
        
        # We call the service directly
        user = user_service.create_user(email=email, username=name, password=password)
        print(f"User created: {user.email}, id: {user.id}, name: {user.name}")
        
        assert user.email == email
        assert user.name == name
        assert user.hashed_password != password
        
        # 2. Test login with correct details
        print("Testing login with correct details...")
        auth_user = user_service.authenticate_user(email, password)
        assert auth_user is not None
        assert auth_user.id == user.id
        print("Login successful!")
        
        # 3. Test login with wrong password
        print("Testing login with wrong password...")
        auth_user_wrong = user_service.authenticate_user(email, "wrongpassword")
        assert auth_user_wrong is None
        print("Wrong password correctly rejected!")
        
        # 4. Test Pydantic validation
        from models.auth_models import UserAuthResponse
        print("Testing UserAuthResponse with None name...")
        # This would have failed before the fix
        response = UserAuthResponse(
            user_id=str(user.id),
            email=user.email,
            name=None, 
            access_token="fake_token"
        )
        print(f"UserAuthResponse created successfully with None name: {response.name}")

if __name__ == "__main__":
    try:
        test_auth_logic()
        print("\nALL LOCAL LOGIC TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
