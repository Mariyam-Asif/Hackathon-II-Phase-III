import requests
import json

# Test the frontend integration with backend authentication
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_frontend_backend_integration():
    """Test that frontend can communicate with backend auth endpoints"""
    print("Testing frontend-backend authentication integration...")

    # Test 1: Check if auth endpoints are accessible
    print("\n1. Testing backend auth endpoints accessibility...")

    # Check register endpoint
    register_url = f"{BACKEND_URL}/auth/register"
    try:
        response = requests.options(register_url)  # Preflight request
        print(f"   Register endpoint OPTIONS: {response.status_code}")
    except:
        print("   Register endpoint: Unreachable")

    # Check login endpoint
    login_url = f"{BACKEND_URL}/auth/login"
    try:
        response = requests.options(login_url)  # Preflight request
        print(f"   Login endpoint OPTIONS: {response.status_code}")
    except:
        print("   Login endpoint: Unreachable")

    # Test 2: Test actual registration flow
    print("\n2. Testing registration flow...")
    user_data = {
        "email": "frontend_test@example.com",
        "username": "front_end_user",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(register_url, json=user_data, headers={'Content-Type': 'application/json'})
        print(f"   Registration response: {response.status_code}")
        if response.status_code == 200:
            reg_data = response.json()
            print(f"   Registration successful! User ID: {reg_data.get('user_id')[:8]}...")
            token = reg_data.get('access_token')
        else:
            print(f"   Registration failed: {response.text}")
            token = None
    except Exception as e:
        print(f"   Registration error: {e}")
        token = None

    # Test 3: Test login flow
    print("\n3. Testing login flow...")
    login_data = {
        "email": "frontend_test@example.com",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(login_url, json=login_data, headers={'Content-Type': 'application/json'})
        print(f"   Login response: {response.status_code}")
        if response.status_code == 200:
            login_data_response = response.json()
            print(f"   Login successful! User ID: {login_data_response.get('user_id')[:8]}...")
            print(f"   Token type: {login_data_response.get('token_type')}")
        else:
            print(f"   Login failed: {response.text}")
    except Exception as e:
        print(f"   Login error: {e}")

    # Test 4: Test token validation endpoint
    print("\n4. Testing token validation...")
    if token:
        validate_url = f"{BACKEND_URL}/auth/validate-token"
        try:
            response = requests.post(validate_url, json={"token": token}, headers={'Content-Type': 'application/json'})
            print(f"   Token validation response: {response.status_code}")
            if response.status_code == 200:
                validate_data = response.json()
                print(f"   Token valid: {validate_data.get('valid')}")
                if validate_data.get('valid'):
                    print(f"   User ID from token: {validate_data.get('user_id')[:8]}...")
            else:
                print(f"   Token validation failed: {response.text}")
        except Exception as e:
            print(f"   Token validation error: {e}")
    else:
        print("   Skipping token validation (no token available)")

    # Test 5: Check if frontend pages are accessible
    print("\n5. Testing frontend page accessibility...")
    try:
        # Check if main page loads
        response = requests.get(FRONTEND_URL)
        print(f"   Frontend home page: {response.status_code}")

        # Check if auth pages load
        response = requests.get(f"{FRONTEND_URL}/auth/login")
        print(f"   Frontend login page: {response.status_code}")

        response = requests.get(f"{FRONTEND_URL}/auth/register")
        print(f"   Frontend register page: {response.status_code}")
    except Exception as e:
        print(f"   Frontend access error: {e}")

    print("\nIntegration test completed!")

if __name__ == "__main__":
    test_frontend_backend_integration()