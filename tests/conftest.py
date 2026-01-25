import os
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

# Set testing mode before importing the app modules
os.environ["TESTING"] = "true"


@pytest.fixture(scope="module")
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client