#!/usr/bin/env python3
"""
Test runner script for LLM-MusicTheory project.
Runs comprehensive tests without making API calls.
"""
import sys
import subprocess
from pathlib import Path


def run_tests(test_type="all", verbose=True):
    """Run tests with specified configuration."""
    
    # Change to project root
    project_root = Path(__file__).parent
    
    # Base command
    cmd = ["poetry", "run", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    # Add specific test types
    if test_type == "models":
        cmd.append("tests/test_models.py")
    elif test_type == "prompt":
        cmd.append("tests/test_prompt_building.py")
    elif test_type == "runner":
        cmd.append("tests/test_runner.py")
    elif test_type == "integration":
        cmd.append("tests/test_integration.py")
    elif test_type == "comprehensive":
        cmd.append("tests/test_comprehensive.py")
    elif test_type == "utils":
        cmd.append("tests/test_path_utils.py")
    elif test_type == "fast":
        cmd.extend(["tests/", "-m", "not slow"])
    else:
        cmd.append("tests/")
    
    # Set environment variables to mock API keys
    env = {
        "OPENAI_API_KEY": "test-key-not-real",
        "ANTHROPIC_API_KEY": "test-key-not-real", 
        "GOOGLE_API_KEY": "test-key-not-real",
        "DEEPSEEK_API_KEY": "test-key-not-real"
    }
    
    print(f"Running: {' '.join(cmd)}")
    print("Environment: Mock API keys set (no actual API calls will be made)")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=project_root, env=env, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    print("LLM-MusicTheory Test Runner")
    print("=" * 40)
    print("This runs comprehensive tests that validate prompt generation")
    print("without making actual API calls to avoid costs.")
    print()
    
    available_types = [
        "all - Run all tests",
        "models - Test model interfaces", 
        "prompt - Test prompt building",
        "runner - Test prompt runner",
        "integration - Test CLI integration",
        "comprehensive - Test with real data",
        "utils - Test utility functions",
        "fast - Run quick tests only"
    ]
    
    if test_type == "help":
        print("Available test types:")
        for t in available_types:
            print(f"  {t}")
        return
    
    print(f"Running test type: {test_type}")
    print()
    
    success = run_tests(test_type)
    
    if success:
        print("\n✅ All tests passed!")
        print("The prompt generation system is working correctly.")
        print("Safe to proceed with real API calls if needed.")
    else:
        print("\n❌ Some tests failed!")
        print("Please review the output above and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
