import os
import sys

# Set the testing environment variable before importing any app modules
os.environ["TESTING"] = "true"

# Now run all tests
import subprocess

result = subprocess.run([
    sys.executable, "-m", "pytest",
    "tests/",
    "-v",
    "--tb=short"
], env=os.environ)

sys.exit(result.returncode)