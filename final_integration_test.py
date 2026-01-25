#!/usr/bin/env python3
"""
Final Integration Test Script for Todo App Backend

This script performs comprehensive integration testing of all features
to ensure the application works as expected.
"""

import os
import sys
import subprocess
import time

def run_final_integration_tests():
    """Run comprehensive integration tests."""
    print("Starting Final Integration Testing...")
    print("=" * 50)

    # Set testing environment
    os.environ["TESTING"] = "true"

    # Run unit tests first
    print("\n1. Running Unit Tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/unit/", "-v"
    ], env=os.environ)

    if result.returncode != 0:
        print("❌ Unit tests failed!")
        return False
    else:
        print("✅ Unit tests passed!")

    # Run integration tests
    print("\n2. Running Integration Tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/integration/", "-v"
    ], env=os.environ)

    if result.returncode != 0:
        print("❌ Integration tests failed!")
        return False
    else:
        print("✅ Integration tests passed!")

    # Run contract tests
    print("\n3. Running Contract Tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/contract/", "-v"
    ], env=os.environ)

    if result.returncode != 0:
        print("❌ Contract tests failed!")
        return False
    else:
        print("✅ Contract tests passed!")

    # Run all tests together
    print("\n4. Running Full Test Suite...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/", "-v", "--tb=no"
    ], env=os.environ)

    if result.returncode != 0:
        print("❌ Full test suite failed!")
        return False
    else:
        print("✅ Full test suite passed!")

    # Calculate test statistics
    print("\n5. Calculating Test Coverage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "coverage", "run",
            "-m", "pytest", "tests/"
        ], env=os.environ)

        if result.returncode == 0:
            coverage_result = subprocess.run([
                sys.executable, "-m", "coverage", "report", "--show-missing"
            ], env=os.environ)

            print("✅ Coverage report generated!")
        else:
            print("⚠️  Coverage calculation skipped due to test failures")
    except Exception as e:
        print(f"⚠️  Could not run coverage: {e}")

    print("\n" + "=" * 50)
    print("🎉 Final Integration Testing Completed Successfully!")
    print("✅ All features are working as expected")
    print("✅ Tests are passing")
    print("✅ API endpoints are functional")
    print("✅ Database operations are working")
    print("✅ Authentication and authorization are functional")
    print("✅ Error handling is working")
    print("=" * 50)

    return True

if __name__ == "__main__":
    success = run_final_integration_tests()
    if not success:
        sys.exit(1)
    else:
        print("\n🚀 All Systems Ready for Production!")