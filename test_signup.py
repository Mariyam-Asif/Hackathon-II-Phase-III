import requests
import json

# Test the signup functionality
BASE_URL = "http://localhost:8000"

def test_signup():
    """Test user registration endpoint"""
    signup_url = f"{BASE_URL}/auth/register"

    # Test user data
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }

    print("Testing signup endpoint...")
    print(f"Sending POST request to: {signup_url}")
    print(f"User data: {json.dumps(user_data, indent=2)}")

    try:
        response = requests.post(signup_url, json=user_data)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.content:
            try:
                response_json = response.json()
                print(f"Response Body: {json.dumps(response_json, indent=2)}")

                if response.status_code == 200:
                    print("\n[SUCCESS] Signup successful!")
                    print(f"User ID: {response_json.get('user_id')}")
                    print(f"Email: {response_json.get('email')}")
                    print(f"Username: {response_json.get('username')}")
                    print(f"Access Token: {'*' * 20} (hidden)")

                    return response_json
                else:
                    print(f"\n[ERROR] Signup failed with status {response.status_code}")
                    return None

            except ValueError:
                print(f"Response Body (non-JSON): {response.text}")
                return None
        else:
            print("Response Body: Empty")
            return None

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the server. Is it running?")
        return None
    except Exception as e:
        print(f"[ERROR] Error occurred: {e}")
        return None

def test_login():
    """Test user login endpoint"""
    login_url = f"{BASE_URL}/auth/login"

    # Login credentials
    login_data = {
        "email": "testuser@example.com",
        "password": "SecurePass123!"
    }

    print("\nTesting login endpoint...")
    print(f"Sending POST request to: {login_url}")
    print(f"Login data: {json.dumps(login_data, indent=2)}")

    try:
        response = requests.post(login_url, json=login_data)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.content:
            try:
                response_json = response.json()
                print(f"Response Body: {json.dumps(response_json, indent=2)}")

                if response.status_code == 200:
                    print("\n[SUCCESS] Login successful!")
                    print(f"User ID: {response_json.get('user_id')}")
                    print(f"Email: {response_json.get('email')}")
                    print(f"Username: {response_json.get('username')}")
                    print(f"Access Token: {'*' * 20} (hidden)")

                    return response_json
                else:
                    print(f"\n[ERROR] Login failed with status {response.status_code}")
                    return None

            except ValueError:
                print(f"Response Body (non-JSON): {response.text}")
                return None
        else:
            print("Response Body: Empty")
            return None

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the server. Is it running?")
        return None
    except Exception as e:
        print(f"[ERROR] Error occurred: {e}")
        return None

if __name__ == "__main__":
    print("Testing Signup and Login functionality...\n")

    # Test signup
    signup_result = test_signup()

    if signup_result:
        # Test login after successful signup
        login_result = test_login()

        if login_result:
            print("\n[PASS] Both signup and login tests passed!")
        else:
            print("\n[WARN] Signup worked, but login failed.")
    else:
        print("\n[FAIL] Signup test failed.")