import os
import sys

# Set the testing environment variable before importing any app modules
os.environ["TESTING"] = "true"

# Now run the tests
import subprocess

result = subprocess.run([
    sys.executable, "-m", "pytest",
    "tests/integration/test_task_endpoints.py",
    "-v"
], env=os.environ)

sys.exit(result.returncode)