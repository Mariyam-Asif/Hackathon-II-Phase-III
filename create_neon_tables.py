#!/usr/bin/env python3
"""
Script to properly create tables in Neon PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel
from backend.src.models.user_model import User
from backend.src.models.task_model import Task

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def create_tables_in_neon():
    """Create tables in Neon PostgreSQL database"""
    print("Creating tables in Neon PostgreSQL...")

    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment!")
        return False

    print(f"Using database URL: {database_url}")

    try:
        # Create engine
        engine = create_engine(database_url)

        # Ensure models are imported to register them with SQLModel
        print("Ensuring models are imported...")
        print(f"Registered tables: {list(SQLModel.metadata.tables.keys())}")

        # Create all tables
        print("Creating all tables...")
        SQLModel.metadata.create_all(engine)

        # Verify tables were created
        inspector = inspect(engine)
        tables_after_creation = inspector.get_table_names()
        print(f"Tables after creation: {tables_after_creation}")

        # Check for our required tables
        required_tables = ['user', 'task']
        found_tables = []

        for req_table in required_tables:
            if req_table in tables_after_creation:
                found_tables.append(req_table)
                columns = inspector.get_columns(req_table)
                print(f"  + Table '{req_table}' exists with columns: {[col['name'] for col in columns]}")
            else:
                print(f"  - Table '{req_table}' NOT found")

        if len(found_tables) == len(required_tables):
            print(f"\nSUCCESS: All required tables ({', '.join(found_tables)}) created successfully!")
            return True
        else:
            missing = [t for t in required_tables if t not in found_tables]
            print(f"\nERROR: Missing tables: {missing}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables_in_neon()
    if success:
        print("\nSUCCESS: Neon PostgreSQL tables created successfully!")
    else:
        print("\nERROR: Failed to create Neon PostgreSQL tables!")