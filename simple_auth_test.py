#!/usr/bin/env python3
"""
Simple test to verify that auth endpoints are accessible without auth headers.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_accessibility(url, method="POST", data=None):
    """Test if an endpoint is accessible without auth header."""
    try:
        if method == "POST":
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
        elif method == "OPTIONS":
            response = requests.options(
                url,
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type, Authorization"
                }
            )

        return response
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return None

print("Testing authentication endpoint accessibility...")

# Test CORS preflight
print("\n1. Testing CORS preflight for /auth/register:")
preflight_resp = test_endpoint_accessibility(f"{BASE_URL}/auth/register", "OPTIONS")
if preflight_resp:
    print(f"   Status: {preflight_resp.status_code}")
    print(f"   Has CORS headers: {'Access-Control-Allow-Origin' in preflight_resp.headers}")

# Test register endpoint accessibility (with shorter password)
print("\n2. Testing /auth/register accessibility:")
register_data = {
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "shortpass123"  # Shorter password to avoid length issues
}
register_resp = test_endpoint_accessibility(f"{BASE_URL}/auth/register", "POST", register_data)
if register_resp:
    print(f"   Status: {register_resp.status_code}")
    if register_resp.status_code == 401 and "Authorization header is required" in register_resp.text:
        print("   ❌ Register endpoint incorrectly requires auth header")
    else:
        print("   ✅ Register endpoint is accessible without auth header")

# Test login endpoint accessibility
print("\n3. Testing /auth/login accessibility:")
login_data = {
    "email": "testuser@example.com",
    "password": "shortpass123"
}
login_resp = test_endpoint_accessibility(f"{BASE_URL}/auth/login", "POST", login_data)
if login_resp:
    print(f"   Status: {login_resp.status_code}")
    if login_resp.status_code == 401 and "Authorization header is required" in login_resp.text:
        print("   ❌ Login endpoint incorrectly requires auth header")
    else:
        print("   ✅ Login endpoint is accessible without auth header")

# Test if there's an error about auth header specifically
print("\n4. Checking for specific auth header errors:")
if register_resp and "Authorization header is required" in register_resp.text:
    print("   ❌ Register endpoint incorrectly requires auth header")
elif login_resp and "Authorization header is required" in login_resp.text:
    print("   ❌ Login endpoint incorrectly requires auth header")
else:
    print("   ✅ No auth header requirement errors found")

print("\nTest completed.")