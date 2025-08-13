# Project Status

Updated: 2025-08-12

## Overview
LLM-MusicTheory is a research-oriented toolkit to design, run, and test music-theory prompts across multiple LLM providers (OpenAI, Anthropic, Google, DeepSeek). It provides:
- Modular prompt composition from reusable templates and context guides
- Provider abstraction for swappable LLM backends
- CLI and Python APIs for repeatable single/batch experiments
- Hermetic, contract-first testing (no real API calls)

## Agent onboarding (read this first)
1. Setup
  - Use Python 3.11+; install deps with Poetry if available: `poetry install`. If not, use system Python to run tests (Makefile falls back to `python -m pytest`).
  - Copy `.env.example` to `.env`; keep placeholder keys for testing (tests use mocks).
2. Run tests quickly
  - `make test` for all tests, or `make test-fast` to skip slow.
  - Focused: `make test-models`, `make test-runner`, `make test-integration`, `make test-utils`.
3. Try the CLI (no costs unless you set real keys and run actual prompts)
  - Single: `poetry run run-single --model chatgpt --file Q1b --datatype mei --context --dataset fux-counterpoint`
  - Batch:  `poetry run run-batch --models chatgpt,claude --files Q1b --datatypes mei --dataset fux-counterpoint`
  - (Legacy aliases still accepted: --question/--questions)
4. Guardrails
  - Do not commit real API keys. Tests must remain hermetic (no network calls).
  - Respect contract tests; update contracts only when intended public behavior changes.

## Repository map (quick tour)
- `src/llm_music_theory/core`
  - `dispatcher.py`: `get_llm(name)` returns provider implementing `LLMInterface`.
  - `runner.py`: `PromptRunner` builds prompt and queries provider.
- `src/llm_music_theory/models`
  - `base.py`: `LLMInterface`, `PromptInput` contracts.
  - `{chatgpt,claude,gemini,deepseek}.py`: provider implementations.
- `src/llm_music_theory/prompts`
  - `prompt_builder.py`: assembles prompts from templates, guides, encoded data, and question text.
  - `prompts/base/*`, `prompts/questions/*`: prompt resources.
- `src/llm_music_theory/cli`
  - `run_single.py`, `run_batch.py`: command-line entrypoints.
- `src/llm_music_theory/utils`
  - `path_utils.py`, `logger.py`: file discovery, logging.
- `tests/`: contract + unit + integration tests with pytest markers.
- `Makefile`: test shortcuts; exports mock API keys; Poetry fallback.
- `pytest.ini`: config and markers.

## Contracts and testing
- Philosophy: contract-first (public behavior) + minimal unit tests for internals.
- Markers: `unit`, `integration`, `cli`, `contract`, `slow`.
- Hermetic setup: Makefile exports mock API keys; providers should be mocked/stubbed in tests—no network calls.
- Useful commands:
  - `make test` / `make test-fast`
  - `make test-models` / `make test-runner` / `make test-integration` / `make test-utils`
  - `make cov` for coverage
  - Direct: `poetry run pytest -m "not slow"`

## Development workflow (playbook)
1. Before coding: run `make test-fast` to see baseline green.
2. Implement changes with types/docs as needed.
3. Add tests:
  - Public behavior changes -> contract tests in `tests/` with `@pytest.mark.contract`.
  - Internal helpers -> unit tests alongside existing suites.
4. Validate: `make test` (or focused targets) and `make cov` if needed.
5. Commit with clear message; prefer small, focused commits.

## Current state
- Architecture
  - Prompt composition via `PromptBuilder`
  - Provider abstraction (`LLMInterface`) and dispatcher (`get_llm`)
  - Orchestrated execution via `PromptRunner`
  - CLI commands: `run-single`, `run-batch`
- Formats: MEI, MusicXML, ABC, Humdrum
- Config: `.env` for API keys; defaults in `config/settings.py`
- Testing
  - Pytest markers: unit, integration, cli, contract, slow
  - Contract-first tests, reduced overlap
  - Hermetic: mock keys; no real API calls
  - Makefile targets; Poetry fallback
- DX
  - Poetry packaging
  - README/docs/scripts updated
  - Removed `run_tests.py`; pytest/Make are canonical

## Recent changes
- Dataset migration: added unified `fux-counterpoint` layout with `--file/--files` flags
- Backwards compatibility: hidden aliases `--question/--questions`, `--list-questions`
- README + CLI docs updated for new dataset abstraction (`--dataset`, `--data-dir`)
- Removed `run_tests.py` (legacy pytest wrapper)
- Added `Makefile` with test targets and mock-API env defaults
- Fallback to `python -m pytest` when Poetry isn’t present
- Reduced duplicate tests; emphasized contract tests

## How to use (quick refs)
- Single prompt (CLI): `poetry run run-single --model chatgpt --file Q1b --datatype mei --context`
- Batch (CLI): `poetry run run-batch --models chatgpt,claude --files Q1b --datatypes mei,abc`
- Tests: `make test`, `make test-fast`, `make test-models`, `make cov`

## Known gaps / risks
- Need richer examples for new dataset (`fux-counterpoint`) beyond single stub
- Coverage badges can drift; removed to avoid misinformation
- Ensure legacy `RCM6` (formerly LLM-RCM) remains minimal but sufficient for test contracts
- Confirm CI uses `make test` or `poetry run pytest` with proper caches

## Next steps (prioritized)
1. Dataset Enhancements
  - Populate `fux-counterpoint` with additional encoded examples across all datatypes
  - Add sample `prompt.md` variations or multiple prompt sets
2. Testing
  - Add contract tests for new listing flags (`--list-files`, legacy alias)
  - Edge cases: invalid dataset name, missing base prompt, missing encoded file
3. Experiments
  - Optional: batch results aggregation/export (CSV/JSON)
  - Optional: experiment configs (YAML/JSON) + driver
4. Tooling
  - Optional: lint/type targets (ruff/mypy) in Makefile + CI
  - Optional: pre-commit hooks
5. Docs
  - “Quick Experiments” guide; dataset migration rationale section
6. CI/CD
  - Verify matrix (3.11, 3.12) and caching; run `make test`

## Verification
- Local smoke test: `make test-utils` passed (18/18)
- Tests are hermetic (mock API keys via Makefile)

If desired, run the full suite now and append a brief summary here.
