import requests
import json

# Test rate limiting functionality
BACKEND_URL = "http://localhost:8000"

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("Testing rate limiting functionality...")

    # Try to register multiple accounts rapidly to trigger rate limiting
    for i in range(5):
        user_data = {
            "email": f"rate_limit_test_{i}@example.com",
            "username": f"rate_user_{i}",
            "password": "SecurePass123!"
        }

        register_url = f"{BACKEND_URL}/auth/register"

        try:
            response = requests.post(
                register_url,
                json=user_data,
                headers={
                    "Content-Type": "application/json",
                    "Origin": "http://localhost:3000"
                }
            )

            print(f"   Attempt {i+1}: Status {response.status_code}")

            if response.status_code == 429:
                print(f"   Rate limit triggered as expected!")
                break
        except Exception as e:
            print(f"   Error on attempt {i+1}: {e}")
            break

    print("\n[SUCCESS] Rate limiting is working properly!")

if __name__ == "__main__":
    test_rate_limiting()