import psycopg2
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

def verify_users_in_database():
    """Verify that users are stored in the Neon database"""
    print("Verifying users in Neon database...")

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL not found in environment!")
        return False

    print(f"Connecting to database: {database_url.replace('@', '***@').split('?')[0]}")  # Hide credentials

    try:
        # Connect to the database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Query the users table
        cursor.execute("SELECT COUNT(*) FROM \"user\";")
        user_count = cursor.fetchone()[0]

        print(f"\nTotal users in database: {user_count}")

        if user_count > 0:
            # Get user details
            cursor.execute("""
                SELECT id, email, username, created_at
                FROM \"user\"
                ORDER BY created_at DESC;
            """)

            users = cursor.fetchall()

            print(f"\nUser details:")
            for user in users:
                user_id, email, username, created_at = user
                print(f"  - ID: {user_id}")
                print(f"    Email: {email}")
                print(f"    Username: {username}")
                print(f"    Created: {created_at}")
                print()

        # Close the connection
        cursor.close()
        conn.close()

        print(f"[SUCCESS] Found {user_count} users in the database!")
        return True

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Verifying users in Neon PostgreSQL database...\n")
    success = verify_users_in_database()

    if success:
        print("\n[SUCCESS] Successfully verified users in Neon database!")
    else:
        print("\n[ERROR] Failed to verify users in Neon database.")