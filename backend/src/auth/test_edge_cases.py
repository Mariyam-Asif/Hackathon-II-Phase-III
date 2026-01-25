"""
Test script for edge cases in Better Auth integration.
Tests expired tokens, malformed tokens, invalid signatures, etc.
"""
from backend.src.auth.jwt_utils import (
    verify_better_auth_token,
    is_valid_jwt_format,
    create_access_token,
    decode_token_payload
)
from datetime import timedelta
import jwt as pyjwt
from backend.src.config.auth_config import auth_config


def test_expired_tokens():
    print("Testing expired tokens...")

    # Create a token that expired 1 second ago
    expired_token = create_access_token(
        {"sub": "test-user-id"},
        expires_delta=timedelta(seconds=-1)
    )

    # Verify that expired token is rejected
    result = verify_better_auth_token(expired_token)
    if result is None:
        print("   ✓ Expired token correctly rejected")
    else:
        print("   ✗ Expired token incorrectly accepted")
        return False

    return True


def test_malformed_tokens():
    print("Testing malformed tokens...")

    malformed_tokens = [
        "not.at.all.a.valid.jwt",  # Not JWT format
        "header.payload",          # Missing signature part
        "header.with.too.many.parts.here.now",  # Too many parts
        "",                        # Empty string
        "12345",                   # Not JWT at all
        ".payload.signature",      # Missing header
        "header..signature",       # Missing payload
        "header.payload.",         # Missing signature
        "header..",                # Missing payload and signature
        "..",                      # All parts missing
    ]

    for i, token in enumerate(malformed_tokens, 1):
        # Test format validation
        is_format_valid = is_valid_jwt_format(token)
        if is_format_valid:
            print(f"   {i}. ✗ Malformed token '{token[:20]}...' incorrectly passed format check")
            return False
        else:
            print(f"   {i}. ✓ Malformed token '{token[:20]}...' correctly failed format check")

        # Test verification (should return None)
        verification_result = verify_better_auth_token(token)
        if verification_result is None:
            print(f"   {i}. ✓ Malformed token '{token[:20]}...' correctly rejected by verification")
        else:
            print(f"   {i}. ✗ Malformed token '{token[:20]}...' incorrectly passed verification")
            return False

    return True


def test_invalid_signatures():
    print("Testing tokens with invalid signatures...")

    # Create a valid token
    valid_token = create_access_token({"sub": "test-user-id"})

    # Extract the header and payload
    parts = valid_token.split('.')
    header_payload = f"{parts[0]}.{parts[1]}"

    # Create tokens with invalid signatures
    invalid_signature_tokens = [
        f"{header_payload}.invalid_signature_here",
        f"{header_payload}.",  # Empty signature
        f"{header_payload}.aW52YWxpZA==",  # Invalid base64 signature
        f"{header_payload}.not_base64",    # Not base64 at all
    ]

    for i, token in enumerate(invalid_signature_tokens, 1):
        # The format should still be valid (3 parts), but verification should fail
        is_format_valid = is_valid_jwt_format(token)
        if is_format_valid:
            print(f"   {i}. ✓ Token with invalid signature has valid JWT format")
        else:
            print(f"   {i}. ✗ Token with invalid signature failed format check")
            return False

        # Verification should fail due to invalid signature
        verification_result = verify_better_auth_token(token)
        if verification_result is None:
            print(f"   {i}. ✓ Token with invalid signature correctly rejected")
        else:
            print(f"   {i}. ✗ Token with invalid signature incorrectly accepted")
            return False

    return True


def test_tampered_payloads():
    print("Testing tokens with tampered payloads...")

    # Create a valid token
    valid_token = create_access_token({"sub": "original-user-id"})

    # Extract parts
    parts = valid_token.split('.')
    header, original_payload, signature = parts[0], parts[1], parts[2]

    # Create a token with tampered payload (but valid signature for original)
    # We'll create a new payload with different user ID
    tampered_payload_data = {"sub": "tampered-user-id", "exp": 9999999999}  # Far future
    import json
    import base64

    # Encode the tampered payload
    tampered_payload_json = json.dumps(tampered_payload_data)
    tampered_payload_b64 = base64.b64encode(tampered_payload_json.encode()).decode('utf-8')

    # Create token with original signature but tampered payload
    tampered_token = f"{header}.{tampered_payload_b64}.{signature}"

    # Format should be valid (3 valid JWT parts)
    is_format_valid = is_valid_jwt_format(tampered_token)
    if is_format_valid:
        print("   ✓ Tampered token has valid JWT format")
    else:
        print("   ✗ Tampered token failed format check")
        return False

    # Verification should fail due to signature mismatch
    verification_result = verify_better_auth_token(tampered_token)
    if verification_result is None:
        print("   ✓ Token with tampered payload correctly rejected (signature mismatch)")
    else:
        print("   ✗ Token with tampered payload incorrectly accepted")
        return False

    return True


def test_valid_tokens():
    print("Testing valid tokens...")

    # Create a valid token
    test_user_id = "valid-test-user-123"
    valid_token = create_access_token({"sub": test_user_id})

    # Format should be valid
    is_format_valid = is_valid_jwt_format(valid_token)
    if is_format_valid:
        print("   ✓ Valid token has valid JWT format")
    else:
        print("   ✗ Valid token failed format check")
        return False

    # Verification should succeed
    verification_result = verify_better_auth_token(valid_token)
    if verification_result is not None and verification_result.user_id == test_user_id:
        print("   ✓ Valid token correctly accepted")
        print(f"   ✓ User ID correctly extracted: {verification_result.user_id}")
    else:
        print("   ✗ Valid token incorrectly rejected")
        return False

    # Decode payload should work
    payload = decode_token_payload(valid_token)
    if payload and payload.get("sub") == test_user_id:
        print("   ✓ Token payload correctly decoded")
    else:
        print("   ✗ Token payload incorrectly decoded")
        return False

    return True


def run_all_edge_case_tests():
    print("Running edge case tests for Better Auth integration...\n")

    tests = [
        ("Valid tokens", test_valid_tokens),
        ("Expired tokens", test_expired_tokens),
        ("Malformed tokens", test_malformed_tokens),
        ("Invalid signatures", test_invalid_signatures),
        ("Tampered payloads", test_tampered_payloads),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"{test_name}:")
        try:
            result = test_func()
            if result:
                print(f"   ✓ {test_name} test passed\n")
            else:
                print(f"   ✗ {test_name} test failed\n")
                all_passed = False
        except Exception as e:
            print(f"   ✗ {test_name} test raised exception: {str(e)}\n")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = run_all_edge_case_tests()

    if success:
        print("🎉 All edge case tests passed!")
    else:
        print("❌ Some edge case tests failed!")