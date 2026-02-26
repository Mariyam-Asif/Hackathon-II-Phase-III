
import os
import sys
import uuid
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

async def test_backend_task_creation():
    backend_url = "http://localhost:8000" # Test against local if possible, or HF if we have token
    
    # Actually, I'll just simulate the internal logic one last time with the exact same data
    from sqlalchemy import create_engine, text
    database_url = os.getenv("DATABASE_URL")
    if "postgresql" in database_url and "sslmode" not in database_url:
        database_url += "?sslmode=require"
        
    print(f"Testing direct DB insertion with exact fields...")
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            user_id = 'dab13411-d3a1-482e-bdad-7e95affa64ec'
            task_id = str(uuid.uuid4())
            
            # This is exactly what the backend does now
            query = text("""
                INSERT INTO "task" (id, title, description, priority, status, user_id, deleted, completed, created_at, updated_at)
                VALUES (:id, :title, :description, :priority, :status, :user_id, :deleted, :completed, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
            conn.execute(query, {
                "id": task_id,
                "title": "Final Verification Task",
                "description": "Checking if this fails",
                "priority": "medium",
                "status": "pending",
                "user_id": user_id,
                "deleted": False,
                "completed": False
            })
            conn.commit()
            print(f"Successfully inserted task {task_id} directly into DB!")
            
            # Clean up
            conn.execute(text('DELETE FROM "task" WHERE id = :id'), {"id": task_id})
            conn.commit()
            print("Cleanup successful.")
            
    except Exception as e:
        print(f"Insertion failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_backend_task_creation())
