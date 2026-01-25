import os
import shutil

# Walk through the backend directory and remove all __pycache__ folders
for root, dirs, files in os.walk("backend"):
    for d in dirs:
        if d == "__pycache__":
            pycache_path = os.path.join(root, d)
            print(f"Removing {pycache_path}")
            shutil.rmtree(pycache_path)

print("Cache cleared successfully.")