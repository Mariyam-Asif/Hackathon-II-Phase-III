#!/usr/bin/env python3
"""
Simple test to see what attributes are available
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlmodel import Session
from backend.src.models.user_model import User

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def simple_test():
    """Simple test to see what attributes are available"""
    print("Simple test...")

    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)

    with Session(engine) as session:
        # Query any existing users to see their attributes
        users = session.exec(select(User)).limit(1).all()

        if users:
            user = users[0]
            print(f"User found: {user}")
            print(f"User type: {type(user)}")
            print(f"User dir: {[attr for attr in dir(user) if not attr.startswith('_')]}")

            # Try to access the attributes
            try:
                print(f"Email: {getattr(user, 'email', 'NO EMAIL ATTR')}")
                print(f"Username: {getattr(user, 'username', 'NO USERNAME ATTR')}")
                print(f"ID: {getattr(user, 'id', 'NO ID ATTR')}")
            except Exception as e:
                print(f"Error accessing attributes: {e}")
        else:
            print("No users found in database")

if __name__ == "__main__":
    simple_test()