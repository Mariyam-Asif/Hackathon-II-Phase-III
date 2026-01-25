#!/usr/bin/env python3
"""
Test script to verify Neon PostgreSQL connection and create tables
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel
from backend.src.database.database import engine

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def test_neon_connection():
    """Test the connection to Neon PostgreSQL and create tables if they don't exist"""
    print("Testing Neon PostgreSQL connection...")

    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment!")
        return False

    print(f"Using database URL: {database_url}")

    try:
        # Create a new engine for testing
        test_engine = create_engine(database_url)

        # Test the connection
        with test_engine.connect() as conn:
            print("+ Successfully connected to Neon PostgreSQL!")

            # Check existing tables
            inspector = inspect(test_engine)
            existing_tables = inspector.get_table_names()
            print(f"Existing tables: {existing_tables}")

            # Create tables if they don't exist
            print("\nCreating tables if they don't exist...")
            SQLModel.metadata.create_all(test_engine)

            # Check tables again after creation
            updated_tables = inspector.get_table_names()
            print(f"Tables after creation: {updated_tables}")

            # Check specific tables we need
            required_tables = ['user', 'task']
            missing_tables = []

            # Check if tables exist (considering possible pluralization or naming differences)
            table_exists = {}
            for req_table in required_tables:
                # Look for exact match first
                if req_table in updated_tables:
                    table_exists[req_table] = req_table
                else:
                    # Look for variations (users vs user, etc.)
                    found = False
                    for actual_table in updated_tables:
                        if req_table in actual_table or actual_table in req_table:
                            table_exists[req_table] = actual_table
                            found = True
                            break
                    if not found:
                        missing_tables.append(req_table)

            if missing_tables:
                print(f"ERROR: Missing required tables: {missing_tables}")
                print(f"Available tables: {updated_tables}")
                return False
            else:
                print("SUCCESS: All required tables exist:")
                for req_table, actual_table in table_exists.items():
                    columns = inspector.get_columns(actual_table)
                    print(f"  - {req_table} (as '{actual_table}'): {[col['name'] for col in columns]}")

                return True

    except Exception as e:
        print(f"ERROR: Error connecting to Neon: {e}")
        return False

if __name__ == "__main__":
    success = test_neon_connection()
    if success:
        print("\nSUCCESS: Neon PostgreSQL setup completed successfully!")
    else:
        print("\nERROR: Neon PostgreSQL setup failed!")