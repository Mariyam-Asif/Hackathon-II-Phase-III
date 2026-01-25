#!/usr/bin/env python3
"""
Test script to reproduce the registration errors with specific passwords.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlmodel import Session
from backend.src.models.auth_models import UserRegistrationRequest
from backend.src.services.user_service import UserService
from backend.src.database.database import engine
from backend.src.api.auth_routes import register_user

def test_passwords():
    print("Testing specific passwords that cause errors...")

    # Use the existing engine from database module
    with Session(engine) as session:
        print("\n1. Testing password 'hello1993' (should cause 500 error)...")
        try:
            # Create registration request with problematic password
            registration_data = UserRegistrationRequest(
                email="test1@example.com",
                username="testuser1",
                password="hello1993"
            )

            # Try to create the user
            result = register_user(registration_data, session)
            print(f"   ✓ User created successfully: {result.email}")
        except Exception as e:
            print(f"   ✗ Error occurred: {str(e)}")
            print(f"   - Error type: {type(e).__name__}")

        print("\n2. Testing password '1234hello' (should cause 409 error)...")
        try:
            # Create registration request with another problematic password
            registration_data2 = UserRegistrationRequest(
                email="test2@example.com",
                username="testuser2",
                password="1234hello"
            )

            # Try to create the user
            result2 = register_user(registration_data2, session)
            print(f"   ✓ User created successfully: {result2.email}")
        except Exception as e:
            print(f"   ✗ Error occurred: {str(e)}")
            print(f"   - Error type: {type(e).__name__}")

        print("\n3. Testing duplicate email scenario...")
        try:
            # Try to create user with same email as first test
            registration_data3 = UserRegistrationRequest(
                email="test1@example.com",  # Same as first test
                username="testuser3",
                password="differentpassword"
            )

            # Try to create the user
            result3 = register_user(registration_data3, session)
            print(f"   ✓ User created successfully: {result3.email}")
        except Exception as e:
            print(f"   ✗ Error occurred: {str(e)}")
            print(f"   - Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_passwords()