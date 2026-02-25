import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def check_schema_details():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    # Ensure sslmode is set correctly for Neon
    if "postgresql" in database_url and "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url += f"{separator}sslmode=require"

    print(f"Connecting to database...")
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            print("\n--- Task Table Schema ---")
            result = conn.execute(text("SELECT column_name, is_nullable, column_default, data_type FROM information_schema.columns WHERE table_name = 'task'")).mappings().all()
            for row in result:
                print(row)
            
            print("\n--- User Table Schema ---")
            result = conn.execute(text("SELECT column_name, is_nullable, column_default, data_type FROM information_schema.columns WHERE table_name = 'user'")).mappings().all()
            for row in result:
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema_details()
