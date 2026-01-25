"""
Utility for generating Better Auth secret keys for development/testing.
"""
import secrets
import string


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a random secret key for Better Auth.

    Args:
        length: Length of the secret key (default 32 characters)

    Returns:
        Randomly generated secret key
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    # Generate a secret key for development purposes
    secret_key = generate_secret_key()
    print(f"Generated Better Auth Secret Key: {secret_key}")
    print("\nTo use this in your .env file:")
    print(f'BETTER_AUTH_SECRET="{secret_key}"')