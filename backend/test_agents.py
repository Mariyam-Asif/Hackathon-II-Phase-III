#!/usr/bin/env python3
"""
Basic test for the AI Chat Agent functionality.
This script tests that the agents API is properly integrated into the main application.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
import importlib.util

# Dynamically import the app to avoid circular import issues
spec = importlib.util.spec_from_file_location("main", "./src/main.py")
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
app = main_module.app

def test_agents_endpoint_exists():
    """Test that the agents endpoint is accessible"""
    client = TestClient(app)

    # Test that the agents endpoint exists and returns a reasonable response
    # We expect this to fail with auth error (401 or 403) rather than 404
    response = client.post("/agents/chat", json={
        "user_message": "Hello",
        "user_id": "test-user-id"
    })

    # The endpoint should exist (not 404), but may require authentication
    assert response.status_code != 404, f"Agents endpoint not found. Got status: {response.status_code}"
    print(f"✓ Agents endpoint exists. Status: {response.status_code}")

    # Test the secured endpoint as well
    response = client.post("/agents/chat-secured", json={
        "user_message": "Hello",
        "user_id": "test-user-id"
    })

    assert response.status_code != 404, f"Secured agents endpoint not found. Got status: {response.status_code}"
    print(f"✓ Secured agents endpoint exists. Status: {response.status_code}")

def test_openapi_docs_includes_agents():
    """Test that the OpenAPI docs include the agents endpoints"""
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200

    # Check if agents endpoints are documented
    docs_response = client.get("/openapi.json")
    assert docs_response.status_code == 200

    openapi_spec = docs_response.json()

    # Look for agents endpoints in the spec
    paths = openapi_spec.get("paths", {})
    agent_paths = [path for path in paths.keys() if "agents" in path.lower()]

    assert len(agent_paths) > 0, f"No agents endpoints found in OpenAPI spec. Paths: {list(paths.keys())}"
    print(f"✓ OpenAPI spec includes agents endpoints: {agent_paths}")

if __name__ == "__main__":
    print("Testing AI Chat Agent Integration...")

    try:
        test_agents_endpoint_exists()
        test_openapi_docs_includes_agents()

        print("\n✅ All integration tests passed!")
        print("The AI Chat Agent is properly integrated into the application.")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)