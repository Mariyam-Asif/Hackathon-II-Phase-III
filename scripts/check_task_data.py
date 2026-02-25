
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def check_task_data():
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
            result = conn.execute(text('SELECT * FROM "task" LIMIT 5')).mappings().all()
            for row in result:
                print(row)
            
            if not result:
                print("No tasks found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_task_data()
