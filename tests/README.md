# Test Suite Guide

This project uses a behavioral, contract-first test suite. Tests define what the system should do, independent of internal implementation.

## Test Types
- Contract tests: public API and behavior guarantees (e.g., `test_*_contract.py`).
- Unit/implementation tests: focused logic where helpful (e.g., `test_prompt_building.py`). Kept minimal to avoid duplication.
- Integration tests: cross-module flows and CLI.
- Slow tests: opt-in performance/heavier checks, marked with `@pytest.mark.slow`.

## Markers
- `contract` for contract/spec tests
- `unit` for implementation/unit tests
- `integration`, `cli`, `slow` as needed

Examples:
- All: `pytest`
- Contract only: `pytest -m contract`
- Unit only: `pytest -m unit`
- Exclude slow: `pytest -m 'not slow'`
- Contract but not slow: `pytest -m 'contract and not slow'`

## Philosophy (short)
- Behavior over implementation. Tests express required outcomes and error handling.
- Hermetic and fast. Mock external APIs and heavy I/O where possible.
- Stable contracts. Implementation can evolve without changing contracts.

## Structure (key files)
- `tests/test_models_contract.py` – LLM interface contracts
- `tests/test_dispatcher_contract.py` – Dispatcher behavior contracts
- `tests/test_prompt_contract.py` – Prompt composition contracts
- `tests/test_runner_contract.py` – Runner contracts
- `tests/test_cli_contract.py` – CLI contracts
- `tests/test_prompt_building.py` – Minimal implementation-focused prompt tests
- `tests/test_models.py` – Minimal unit smoke for one concrete model path
- Other files are focused unit/integration tests

## Overlap policy
- Prefer contract coverage for public behavior; keep unit tests lightweight.
- If a behavior is covered in a contract test, unit tests should not reassert it.
- Use slow markers sparingly; keep default suite fast and hermetic.

## Writing tests
- Define expected outcomes and edge cases.
- Avoid coupling to private internals.
- Mock external services and heavy I/O.
- Keep names descriptive; avoid suffixes like "new", "fixed", or "old".

## Running locally
- Default: `pytest`
- With coverage (optional): `pytest --cov=src --cov-report=term-missing`

## Notes
- If a contract test fails, treat it as a behavior regression or a spec mismatch. Adjust only with intent and documentation.
