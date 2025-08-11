.PHONY: test test-fast test-models test-runner test-integration test-utils cov

# Detect pytest command: prefer Poetry, else fall back to system Python
HAS_POETRY := $(shell command -v poetry >/dev/null 2>&1 && echo yes || echo no)
ifeq ($(HAS_POETRY),yes)
	PYTEST_CMD := poetry run pytest
else
	PYTEST_CMD := python -m pytest
endif

# Default mock API keys to ensure tests never hit real APIs
export OPENAI_API_KEY ?= test-key-not-real
export ANTHROPIC_API_KEY ?= test-key-not-real
export GOOGLE_API_KEY ?= test-key-not-real
export DEEPSEEK_API_KEY ?= test-key-not-real

# Run all tests
test:
	$(PYTEST_CMD)

# Fast tests (skip slow)
test-fast:
	$(PYTEST_CMD) -m "not slow"

# Focused test categories
test-models:
	$(PYTEST_CMD) tests/test_models.py

test-runner:
	$(PYTEST_CMD) tests/test_runner.py

test-integration:
	$(PYTEST_CMD) tests/test_integration.py

test-utils:
	$(PYTEST_CMD) tests/test_path_utils.py

# Coverage report
cov:
	$(PYTEST_CMD) --cov=src/llm_music_theory --cov-report=term-missing
