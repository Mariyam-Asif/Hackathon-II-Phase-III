import requests
import json

# Test the signup functionality from the frontend perspective
BACKEND_URL = "http://localhost:8000"

def test_signup_from_frontend():
    """Test signup functionality simulating frontend behavior"""
    print("Testing signup functionality simulating frontend behavior...")

    # Test user data
    user_data = {
        "email": "frontend_test_new@example.com",
        "username": "frontend_test_user",
        "password": "SecurePass123!"
    }

    # Simulate the frontend request with proper headers
    register_url = f"{BACKEND_URL}/auth/register"

    # First, let's try a preflight request (simulating what browsers do)
    print("1. Testing preflight OPTIONS request...")
    options_response = requests.options(
        register_url,
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    print(f"   OPTIONS request status: {options_response.status_code}")
    print(f"   Access-Control-Allow-Origin: {options_response.headers.get('access-control-allow-origin')}")
    print(f"   Access-Control-Allow-Methods: {options_response.headers.get('access-control-allow-methods')}")

    # Now try the actual registration
    print("\n2. Testing actual registration request...")
    try:
        response = requests.post(
            register_url,
            json=user_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )

        print(f"   Registration response: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Registration successful!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Username: {data.get('username')}")

            # Test login with the new user
            print("\n3. Testing login with new user...")
            login_url = f"{BACKEND_URL}/auth/login"
            login_data = {
                "email": "frontend_test_new@example.com",
                "password": "SecurePass123!"
            }

            login_response = requests.post(
                login_url,
                json=login_data,
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:3000"
                }
            )

            if login_response.status_code == 200:
                login_data_response = login_response.json()
                print(f"   Login successful!")
                print(f"   User ID: {login_data_response.get('user_id')}")
                print(f"   Token type: {login_data_response.get('token_type')}")

                # Test token validation
                print("\n4. Testing token validation...")
                token = login_data_response.get('access_token')
                validate_url = f"{BACKEND_URL}/auth/validate-token"

                validate_response = requests.post(
                    validate_url,
                    json={"token": token},
                    headers={
                        "Content-Type": "application/json",
                        "Origin": "http://localhost:3000"
                    }
                )

                if validate_response.status_code == 200:
                    validate_data = validate_response.json()
                    if validate_data.get('valid'):
                        print(f"   Token validation successful!")
                        print(f"   Token is valid: {validate_data.get('valid')}")
                        print(f"   User ID from token: {validate_data.get('user_id')}")

                        print("\n[SUCCESS] All authentication flows working correctly!")
                        print("The frontend signup/login process should work without CORS issues.")
                        return True
                    else:
                        print(f"   Token validation failed!")
                        return False
                else:
                    print(f"   Token validation response: {validate_response.status_code}")
                    return False
            else:
                print(f"   Login failed: {login_response.status_code}")
                return False
        else:
            print(f"   Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   Error during registration: {e}")
        return False

if __name__ == "__main__":
    success = test_signup_from_frontend()
    if success:
        print("\n[RESULT] Frontend authentication integration is working correctly!")
    else:
        print("\n[RESULT] There are issues with the frontend authentication integration.")