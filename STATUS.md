# Project Status

Updated: 2025-08-11

## Overview
LLM-MusicTheory is a research-oriented toolkit to design, run, and test music theory prompts across multiple LLM providers (OpenAI, Anthropic, Google, DeepSeek). It provides modular prompt composition, provider abstraction, and repeatable experiments via CLI and Python APIs. Tests are hermetic and contract-first.

## Current State
- Architecture
  - Prompt composition via `PromptBuilder`
  - LLM provider abstraction (`LLMInterface`) and dispatcher (`get_llm`)
  - Orchestrated execution via `PromptRunner`
  - CLI commands: `run-single`, `run-batch`
- Formats supported: MEI, MusicXML, ABC, Humdrum
- Configuration: `.env` for API keys; defaults in `config/settings.py`
- Testing
  - Pytest markers: unit, integration, cli, contract, slow
  - Contract-first tests; reduced overlap with unit tests
  - Hermetic: mock API keys; no real API calls in tests
  - Makefile targets for common test flows; Poetry fallback to `python -m pytest`
- Developer Experience
  - Poetry for packaging and scripts
  - Updated README and docs/scripts.md
  - Removed legacy `run_tests.py`; canonical test entry is Makefile/pytest

## Recent Changes
- Removed root-level `run_tests.py` (thin wrapper around pytest)
- Added `Makefile` with test targets and mock-API env defaults
- Implemented fallback to `python -m pytest` when Poetry is not installed
- Updated documentation to use Make targets/pytest instead of the script
- Pruned duplicate/legacy tests; emphasized contract tests

## How to Use
- Single prompt (CLI):
  - `poetry run run-single --model chatgpt --question Q1b --datatype mei --context`
- Batch prompts (CLI):
  - `poetry run run-batch --models chatgpt,claude --questions Q1b --datatypes mei,abc`
- Tests:
  - `make test` (all), `make test-fast` (skip slow), `make test-models` (focused), `make cov` (coverage)
  - Or directly: `poetry run pytest -m "not slow"`

## Known Gaps / Risks
- Static test coverage badges and counts can drift; removed to avoid misinformation
- Some docs still reference example datasets under `data/LLM-RCM/`; ensure data presence for examples (not required for tests)
- CI status not validated here; ensure CI uses `make test` or `poetry run pytest`

## Next Steps
1. Testing improvements
   - Expand contract tests for CLI discovery flags and error cases
   - Add edge-case tests for missing files and invalid parameters
2. Experiment ergonomics
   - Optional: add result aggregation/export (CSV/JSON) for `run-batch`
   - Optional: add experiment configs (YAML/JSON) and a driver script
3. Tooling
   - Optional: add lint/type targets (ruff/mypy) to Makefile and CI
   - Optional: pre-commit hooks for formatting and linting
4. Docs
   - Add a minimal “Quick Experiments” guide
   - Ensure docs align with Make-based testing and Poetry fallback
5. CI/CD
   - Verify CI matrix (3.11, 3.12) runs `make test` and caches appropriately

## Verification
- Local smoke test executed: `make test-utils` passed (18/18)
- No real API calls during tests (mock API keys exported via Makefile)

If you want, I can run the full test suite now and include a short summary here.
