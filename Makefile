.PHONY: test test-fast test-models test-runner test-integration test-utils cov

# Default mock API keys to ensure tests never hit real APIs
export OPENAI_API_KEY ?= test-key-not-real
export ANTHROPIC_API_KEY ?= test-key-not-real
export GOOGLE_API_KEY ?= test-key-not-real
export DEEPSEEK_API_KEY ?= test-key-not-real

# Run all tests
test:
	poetry run pytest

# Fast tests (skip slow)
test-fast:
	poetry run pytest -m "not slow"

# Focused test categories
test-models:
	poetry run pytest tests/test_models.py

test-runner:
	poetry run pytest tests/test_runner.py

test-integration:
	poetry run pytest tests/test_integration.py

test-utils:
	poetry run pytest tests/test_path_utils.py

# Coverage report
cov:
	poetry run pytest --cov=src/llm_music_theory --cov-report=term-missing
