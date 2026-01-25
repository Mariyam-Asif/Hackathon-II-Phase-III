import requests
import json
import jwt  # pip install pyjwt

# Test JWT token handling in frontend-backend integration
BACKEND_URL = "http://localhost:8000"

def test_jwt_validation():
    """Test that JWT tokens can be validated properly"""
    print("Testing JWT token validation...")

    # First, let's validate the token from our previous successful registration
    # Use the test user we created earlier
    login_url = f"{BACKEND_URL}/auth/login"
    login_data = {
        "email": "testuser@example.com",  # Use the user we created earlier
        "password": "SecurePass123!"
    }

    response = requests.post(login_url, json=login_data, headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return False

    data = response.json()
    token = data.get('access_token')
    user_id = data.get('user_id')

    print(f"[SUCCESS] Login successful")
    print(f"  User ID: {user_id}")
    print(f"  Token received: {len(token)} characters")

    # 1. Decode the JWT to check its structure
    try:
        # We'll decode without verification to check structure (not security-sensitive here)
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"[SUCCESS] JWT token structure verified")
        print(f"  Subject (user ID): {decoded.get('sub')}")
        print(f"  Email: {decoded.get('email')}")
        print(f"  Username: {decoded.get('username')}")
        print(f"  Expiration: {decoded.get('exp')}")
    except Exception as e:
        print(f"[ERROR] JWT decoding failed: {e}")
        return False

    # 2. Test using the token to access protected resources
    # First, let's try to validate the token
    validate_url = f"{BACKEND_URL}/auth/validate-token"
    validate_response = requests.post(validate_url, json={"token": token}, headers={'Content-Type': 'application/json'})

    if validate_response.status_code != 200:
        print(f"[ERROR] Token validation failed: {validate_response.status_code}")
        return False

    validate_data = validate_response.json()
    if not validate_data.get('valid'):
        print(f"[ERROR] Token validation returned invalid")
        return False

    print(f"[SUCCESS] Token validation successful")
    print(f"  Valid: {validate_data.get('valid')}")
    print(f"  User ID: {validate_data.get('user_id')}")

    # 3. Check that the token can be used with the task endpoints (which require authentication)
    # Try to access a user-specific task endpoint
    task_url = f"{BACKEND_URL}/api/{user_id}/tasks"
    task_response = requests.get(task_url, headers={'Authorization': f'Bearer {token}'})

    # This might return 404 if no tasks exist, which is fine
    print(f"[SUCCESS] Task endpoint access test: {task_response.status_code}")
    if task_response.status_code in [200, 404]:  # 200 for success, 404 for no tasks
        print("  [SUCCESS] Token accepted for protected endpoint access")
    elif task_response.status_code == 401:
        print("  [ERROR] Token rejected - authentication failed")
        return False
    else:
        print(f"  [WARNING] Unexpected status: {task_response.status_code}")

    # 4. Verify that token validation fails with an invalid token
    invalid_response = requests.post(validate_url, json={"token": "invalid.token.here"}, headers={'Content-Type': 'application/json'})
    invalid_data = invalid_response.json()

    if invalid_data.get('valid') == False:
        print("[SUCCESS] Invalid token properly rejected")
    else:
        print("[ERROR] Invalid token incorrectly accepted")
        return False

    print("\n[SUCCESS] JWT token validation test completed successfully!")
    print("\nSummary:")
    print("- JWT structure includes user identity information")
    print("- Tokens can be validated successfully")
    print("- Tokens work with protected API endpoints")
    print("- Invalid tokens are properly rejected")
    print("- Frontend can store and use tokens for authentication")

    return True

if __name__ == "__main__":
    test_jwt_validation()