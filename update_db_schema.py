#!/usr/bin/env python3
"""
Script to recreate the database with the updated schema.
This addresses the issue where the password_hash column was missing from the user table.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.database.database import engine, create_db_and_tables
from backend.src.models.user_model import User
from sqlalchemy import inspect

def check_database_schema():
    """Check if the database schema includes the password_hash column."""
    inspector = inspect(engine)
    columns = inspector.get_columns('user')

    column_names = [col['name'] for col in columns]
    print(f"Current user table columns: {column_names}")

    if 'password_hash' in column_names:
        print("[PASS] password_hash column exists in the database")
        return True
    else:
        print("[FAIL] password_hash column is missing from the database")
        return False

def recreate_database():
    """Recreate the database tables with the updated schema."""
    print("Recreating database tables with updated schema...")

    # Drop all tables first
    from backend.src.models.user_model import User
    try:
        from backend.src.models.task_model import Task
        Task.__table__.drop(engine, checkfirst=True)
    except ImportError:
        print("Task model not found, continuing...")

    User.__table__.drop(engine, checkfirst=True)

    print("Dropped existing tables")

    # Create all tables with the new schema
    create_db_and_tables()
    print("Created tables with updated schema")

    # Verify the schema
    if check_database_schema():
        print("[PASS] Database successfully updated with new schema")
        return True
    else:
        print("[FAIL] Failed to update database schema")
        return False

if __name__ == "__main__":
    print("Checking database schema...")

    if not check_database_schema():
        print("\nThe database schema is outdated. Recreating with updated schema...")
        recreate_database()
    else:
        print("\nDatabase schema is already up to date.")