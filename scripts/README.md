# Scripts

This directory contains utility scripts for development and maintenance.

## Contents

- `run_tests.py` - Comprehensive test runner script
- Development helper scripts
- Maintenance utilities

## Usage

Run scripts using Poetry to ensure proper environment:

```bash
# Run all tests
poetry run python scripts/run_tests.py

# Run specific test categories
poetry run python scripts/run_tests.py --type unit
poetry run python scripts/run_tests.py --type integration

# Run with verbose output
poetry run python scripts/run_tests.py --verbose
```
