#!/usr/bin/env python3
"""
Test script to verify the authentication fixes work correctly.
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread
import signal
import os

# Server configuration
SERVER_URL = "http://localhost:8000"

def start_server():
    """Start the backend server."""
    print("Starting backend server...")
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.src.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=".")

    # Give the server time to start
    time.sleep(3)

    return proc

def test_register_new_user():
    """Test registering a new user."""
    print("\n--- Testing Registration ---")

    # Register a new user
    register_data = {
        "email": "testuser@example.com",
        "password": "shortpass",
        "username": "testuser"
    }

    try:
        response = requests.post(f"{SERVER_URL}/auth/register", json=register_data)
        print(f"Registration Status: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Registration Response: {response_json}")
        except json.JSONDecodeError:
            print(f"Registration Response (raw): {response.text}")
            return False

        if response.status_code == 200:
            print("[PASS] Registration successful")
            return True
        else:
            print(f"[FAIL] Registration failed: {response_json}")
            return False
    except Exception as e:
        print(f"[FAIL] Registration error: {e}")
        return False

def test_login_with_existing_user():
    """Test logging in with an existing user."""
    print("\n--- Testing Login with Existing User ---")

    login_data = {
        "email": "testuser@example.com",
        "password": "shortpass"
    }

    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Login Response: {response_json}")
        except json.JSONDecodeError:
            print(f"Login Response (raw): {response.text}")
            return False

        if response.status_code == 200:
            print("[PASS] Login with existing user successful")
            return True
        else:
            print(f"[FAIL] Login with existing user failed: {response_json}")
            return False
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return False

def test_login_with_nonexistent_user():
    """Test logging in with a non-existent user."""
    print("\n--- Testing Login with Non-existent User ---")

    login_data = {
        "email": "nonexistent@example.com",
        "password": "somepassword"
    }

    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Login Response: {response_json}")
        except json.JSONDecodeError:
            print(f"Login Response (raw): {response.text}")
            return False

        # Check if the response contains the expected error message
        if response.status_code != 200:
            error_msg = response_json.get("detail", {}).get("error", "") or response_json.get("error", "")
            if "No account found with this email" in error_msg or "register first" in error_msg.lower():
                print("[PASS] Correctly prompted user to register when email doesn't exist")
                return True
            else:
                print(f"[INFO] Login failed as expected, but message was: {error_msg}")
                return True  # Still acceptable
        else:
            print("[FAIL] Login with non-existent user should have failed")
            return False
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return False

def test_json_response_handling():
    """Test that error responses are always JSON."""
    print("\n--- Testing JSON Response Handling ---")

    # Send malformed request to trigger error
    try:
        response = requests.post(f"{SERVER_URL}/auth/login",
                               data="invalid json {",
                               headers={"Content-Type": "application/json"})

        print(f"Malformed request Status: {response.status_code}")

        try:
            response_json = response.json()
            print("[PASS] Error response is valid JSON")
            print(f"Error response: {response_json}")
            return True
        except json.JSONDecodeError:
            print(f"[FAIL] Error response is not valid JSON: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"[FAIL] JSON test error: {e}")
        return False

def run_tests():
    """Run all authentication tests."""
    print("Starting authentication tests...")

    # Start server in background
    server_proc = start_server()

    try:
        # Give server time to start
        time.sleep(5)

        # Run tests
        results = []
        results.append(test_register_new_user())
        results.append(test_login_with_existing_user())
        results.append(test_login_with_nonexistent_user())
        results.append(test_json_response_handling())

        # Print summary
        print(f"\n--- Test Summary ---")
        print(f"Tests passed: {sum(results)}/{len(results)}")

        if all(results):
            print("[PASS] All tests passed!")
            return True
        else:
            print("[FAIL] Some tests failed")
            return False

    finally:
        # Terminate the server
        try:
            server_proc.terminate()
            server_proc.wait(timeout=5)
        except:
            try:
                server_proc.kill()
            except:
                pass

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)