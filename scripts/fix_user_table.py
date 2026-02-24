import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def fix_user_table():
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
            # Drop the cached inspector if any
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            print(f"Current columns in 'user' table: {columns}")

            # Add 'name' column if it doesn't exist
            if 'name' not in columns:
                print("Adding 'name' column to 'user' table...")
                conn.execute(text('ALTER TABLE "user" ADD COLUMN "name" VARCHAR'))
                print("Column 'name' added successfully.")
                
                if 'username' in columns:
                    print("Migrating data from 'username' to 'name'...")
                    conn.execute(text('UPDATE "user" SET "name" = "username"'))
                    print("Data migrated.")
            else:
                print("Column 'name' already exists.")

            # Check for hashed_password vs password_hash
            if 'hashed_password' not in columns:
                if 'password_hash' in columns:
                    print("Renaming 'password_hash' to 'hashed_password'...")
                    conn.execute(text('ALTER TABLE "user" RENAME COLUMN "password_hash" TO "hashed_password"'))
                    print("Column renamed successfully.")
                else:
                    print("Adding 'hashed_password' column...")
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN "hashed_password" VARCHAR NOT NULL DEFAULT \'\''))
                    print("Column 'hashed_password' added successfully.")
            
            conn.commit()
            print("Changes committed.")
            
            # Final check
            new_inspector = inspect(engine)
            columns_final = [col['name'] for col in new_inspector.get_columns('user')]
            print(f"Final columns in 'user' table: {columns_final}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_user_table()
