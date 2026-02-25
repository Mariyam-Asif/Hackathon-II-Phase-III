
import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def check_task_table():
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
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        if 'task' in tables:
            columns = [col['name'] for col in inspector.get_columns('task')]
            print(f"Columns in 'task' table: {columns}")
        else:
            print("Table 'task' does not exist!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_task_table()
