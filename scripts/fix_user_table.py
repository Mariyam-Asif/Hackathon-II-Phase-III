
import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def fix_database():
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
            # 1. Fix User Table
            inspector = inspect(engine)
            if 'user' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('user')]
                print(f"User columns: {columns}")
                
                if 'name' not in columns:
                    print("Adding 'name' to 'user'...")
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN "name" VARCHAR'))
                
                if 'hashed_password' not in columns:
                    if 'password_hash' in columns:
                        print("Renaming 'password_hash' to 'hashed_password'...")
                        conn.execute(text('ALTER TABLE "user" RENAME COLUMN "password_hash" TO "hashed_password"'))
                    else:
                        print("Adding 'hashed_password' to 'user'...")
                        conn.execute(text('ALTER TABLE "user" ADD COLUMN "hashed_password" VARCHAR NOT NULL DEFAULT \'\''))
            
            # 2. Fix Task Table
            if 'task' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('task')]
                print(f"Task columns: {columns}")
                
                if 'status' not in columns:
                    print("Adding 'status' to 'task'...")
                    conn.execute(text("ALTER TABLE \"task\" ADD COLUMN \"status\" VARCHAR NOT NULL DEFAULT 'pending'"))
                
                if 'priority' not in columns:
                    print("Adding 'priority' to 'task'...")
                    conn.execute(text("ALTER TABLE \"task\" ADD COLUMN \"priority\" VARCHAR NOT NULL DEFAULT 'medium'"))
                
                if 'completed_at' not in columns:
                    print("Adding 'completed_at' to 'task'...")
                    conn.execute(text("ALTER TABLE \"task\" ADD COLUMN \"completed_at\" TIMESTAMP"))
                
                # Migrate 'completed' boolean if it exists
                if 'completed' in columns:
                    print("Migrating 'completed' boolean to 'status'...")
                    conn.execute(text("UPDATE \"task\" SET \"status\" = 'completed' WHERE \"completed\" = true"))
                    conn.execute(text("UPDATE \"task\" SET \"status\" = 'pending' WHERE \"completed\" = false OR \"completed\" IS NULL"))

            conn.commit()
            print("Changes committed successfully.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database()
