
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def set_defaults():
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
            print("Setting defaults for task table...")
            conn.execute(text('ALTER TABLE "task" ALTER COLUMN "completed" SET DEFAULT false'))
            conn.execute(text('ALTER TABLE "task" ALTER COLUMN "deleted" SET DEFAULT false'))
            
            # Also set created_at and updated_at defaults if missing
            conn.execute(text('ALTER TABLE "task" ALTER COLUMN "created_at" SET DEFAULT CURRENT_TIMESTAMP'))
            conn.execute(text('ALTER TABLE "task" ALTER COLUMN "updated_at" SET DEFAULT CURRENT_TIMESTAMP'))
            
            conn.commit()
            print("Defaults set successfully.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    set_defaults()
