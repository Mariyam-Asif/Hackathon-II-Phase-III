#!/usr/bin/env python3
"""
Debug script to check SQLModel metadata and registered models
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlmodel import SQLModel
from backend.src.models.user_model import User
from backend.src.models.task_model import Task

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def debug_sqlmodel_metadata():
    """Debug the SQLModel metadata to see what tables are registered"""
    print("Debugging SQLModel metadata...")

    # Print registered tables in SQLModel metadata
    print(f"SQLModel metadata tables: {list(SQLModel.metadata.tables.keys())}")

    # Print all registered classes
    for table_name, table_obj in SQLModel.metadata.tables.items():
        print(f"Table '{table_name}' has columns: {[col.name for col in table_obj.columns]}")

    # Import the models to ensure they're registered
    print(f"User model imported: {User.__name__}")
    print(f"Task model imported: {Task.__name__}")

    print(f"After imports, SQLModel metadata tables: {list(SQLModel.metadata.tables.keys())}")

if __name__ == "__main__":
    debug_sqlmodel_metadata()