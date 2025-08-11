# 🔧 Scripts

Development and automation scripts for the LLM-MusicTheory project.

## 📁 Available Scripts

### Development Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **[`setup_dev.sh`](#setup-development)** | Set up development environment | `./scripts/setup_dev.sh` |
| **[`run_tests.sh`](#test-automation)** | Run comprehensive test suite | `./scripts/run_tests.sh` |
| **[`format_code.sh`](#code-formatting)** | Format code with black/isort | `./scripts/format_code.sh` |
| **[`check_quality.sh`](#quality-checks)** | Run quality checks | `./scripts/check_quality.sh` |

### Data Management

| Script | Purpose | Usage |
|--------|---------|-------|
| **[`validate_data.py`](#data-validation)** | Validate data integrity | `poetry run python scripts/validate_data.py` |
| **[`backup_data.sh`](#data-backup)** | Backup data directory | `./scripts/backup_data.sh` |
| **[`clean_outputs.py`](#output-cleanup)** | Clean old output files | `poetry run python scripts/clean_outputs.py` |

### Automation

| Script | Purpose | Usage |
|--------|---------|-------|
| **[`batch_experiment.py`](#batch-experiments)** | Run predefined experiments | `poetry run python scripts/batch_experiment.py` |
| **[`generate_docs.sh`](#documentation)** | Generate documentation | `./scripts/generate_docs.sh` |
| **[`release_prep.sh`](#release-preparation)** | Prepare for release | `./scripts/release_prep.sh` |

## 🚀 Quick Commands

```bash
# Set up development environment
./scripts/setup_dev.sh

# Run all tests
./scripts/run_tests.sh

# Format all code
./scripts/format_code.sh

# Validate data integrity
poetry run python scripts/validate_data.py

# Clean old outputs
poetry run python scripts/clean_outputs.py --days 30
```

## 📝 Script Details

### Setup Development

**`setup_dev.sh`** - Complete development environment setup:

```bash
#!/bin/bash
# Install Poetry if not present
# Set up virtual environment
# Install dependencies
# Set up pre-commit hooks
# Validate installation
```

**Usage:**
```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

### Test Automation

**`run_tests.sh`** - Comprehensive testing with reporting:

```bash
#!/bin/bash
# Run unit tests
# Generate coverage report  
# Run integration tests
# Check for test failures
# Generate summary report
```

**Options:**
```bash
./scripts/run_tests.sh --fast        # Skip slow tests
./scripts/run_tests.sh --coverage    # Generate coverage report
./scripts/run_tests.sh --models      # Test only model implementations
```

### Code Formatting

**`format_code.sh`** - Automated code formatting:

```bash
#!/bin/bash
# Run black formatter
# Sort imports with isort
# Check for formatting issues
# Report changes made
```

### Data Validation

**`validate_data.py`** - Verify data integrity:

```python
# Check file existence
# Validate file formats
# Verify data completeness
# Report missing files
# Check encoding integrity
```

**Usage:**
```bash
poetry run python scripts/validate_data.py
poetry run python scripts/validate_data.py --fix    # Attempt to fix issues
poetry run python scripts/validate_data.py --verbose # Detailed output
```

### Output Cleanup

**`clean_outputs.py`** - Manage output files:

```python
# Remove old output files
# Archive important results
# Free up disk space
# Generate cleanup report
```

**Usage:**
```bash
# Clean files older than 30 days
poetry run python scripts/clean_outputs.py --days 30

# Dry run (show what would be deleted)
poetry run python scripts/clean_outputs.py --dry-run

# Clean specific model outputs
poetry run python scripts/clean_outputs.py --model chatgpt
```

### Batch Experiments

**`batch_experiment.py`** - Run predefined experiment sets:

```python
# Execute experiment configurations
# Collect results systematically  
# Generate comparison reports
# Export data for analysis
```

**Usage:**
```bash
# Run default experiment set
poetry run python scripts/batch_experiment.py

# Run specific experiment
poetry run python scripts/batch_experiment.py --config experiments/config1.json

# Resume interrupted experiment
poetry run python scripts/batch_experiment.py --resume
```

## 🔧 Creating Custom Scripts

### Script Template

```python
#!/usr/bin/env python3
"""
Custom script template for LLM-MusicTheory project.
"""
import argparse
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from llm_music_theory.utils.logger import setup_logger

def main():
    """Main script functionality."""
    parser = argparse.ArgumentParser(description="Your script description")
    parser.add_argument("--option", help="Script option")
    args = parser.parse_args()
    
    logger = setup_logger(__name__)
    logger.info("Starting script execution")
    
    # Your script logic here
    
    logger.info("Script completed successfully")

if __name__ == "__main__":
    main()
```

### Best Practices

1. **Logging**: Use the project's logging configuration
2. **Error Handling**: Implement proper exception handling
3. **Documentation**: Include clear docstrings and help text
4. **Path Management**: Use Path objects for file operations
5. **Configuration**: Accept command-line arguments for flexibility

### Making Scripts Executable

```bash
# Make script executable
chmod +x scripts/your_script.sh

# Add shebang line to Python scripts
#!/usr/bin/env python3

# Use Poetry for Python script execution
poetry run python scripts/your_script.py
```

## 🚨 Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Solution: Make script executable
chmod +x scripts/script_name.sh
```

**Command Not Found**
```bash
# Solution: Run from project root
cd /path/to/LLM-MusicTheory
./scripts/script_name.sh
```

**Python Import Errors**
```bash
# Solution: Use Poetry environment
poetry run python scripts/script_name.py
```

### Debug Mode

Enable verbose output for any script:
```bash
export VERBOSE=1
./scripts/script_name.sh
```

---

For more information, see the main [README.md](../README.md) or [docs/](../docs/) directory.

## 🔧 Script Details

### Testing (Makefile/pytest)

Use Make targets or Poetry + pytest. The Makefile sets mock API keys by default so tests never hit real APIs.

Examples:
```bash
make test                 # All tests
make test-fast            # Skip slow tests
make test-models          # Only model tests
make cov                  # Coverage report

# Or directly
poetry run pytest -m "not slow"
poetry run pytest tests/test_models.py
```

### setup_dev.py

Development environment configuration:

```python
"""
Development environment setup script.
Configures local environment for optimal development workflow.
"""

# Features:
- Poetry environment validation
- Pre-commit hook installation
- IDE configuration suggestions
- Dependency compatibility checks
- Environment variable setup
```

### format_code.py

Code formatting automation:

```python
"""
Automated code formatting using Black and isort.
Ensures consistent code style across the project.
"""

# Features:
- Black code formatting
- Import sorting with isort
- Line length enforcement (88 characters)
- Docstring formatting
- Configuration file respect
```

### validate_data.py

Data integrity validation:

```python
"""
Validates project data files for integrity and structure.
Ensures all required data is present and properly formatted.
"""

# Features:
- Music file format validation
- Prompt template verification
- Question data consistency checks
- File naming convention enforcement
- Missing file detection
```

## 🎯 Script Categories

### 1. Testing & Quality Assurance
| Script | Purpose | Usage |
|--------|---------|--------|
| Makefile | Primary test runner | `make test` / `make test-fast` / `make cov` |
| `lint_code.py` | Code quality checks | `poetry run python scripts/lint_code.py` |
| `format_code.py` | Code formatting | `poetry run python scripts/format_code.py` |

### 2. Development Workflow  
| Script | Purpose | Usage |
|--------|---------|--------|
| `setup_dev.py` | Environment setup | `poetry run python scripts/setup_dev.py` |
| `check_deps.py` | Dependency management | `poetry run python scripts/check_deps.py` |
| `generate_docs.py` | Documentation | `poetry run python scripts/generate_docs.py` |

### 3. Data Management
| Script | Purpose | Usage |
|--------|---------|--------|
| `validate_data.py` | Data validation | `poetry run python scripts/validate_data.py` |
| `backup_data.py` | Data backup | `poetry run python scripts/backup_data.py` |
| `migrate_data.py` | Data migration | `poetry run python scripts/migrate_data.py` |

### 4. Release & Deployment
| Script | Purpose | Usage |
|--------|---------|--------|
| `prepare_release.py` | Release preparation | `poetry run python scripts/prepare_release.py` |
| `build_package.py` | Package building | `poetry run python scripts/build_package.py` |
| `deploy.py` | Deployment automation | `poetry run python scripts/deploy.py` |

## 🛠️ Creating New Scripts

### Script Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage:
    poetry run python scripts/your_script.py [options]

Requirements:
    - List any special requirements
    - Dependencies needed
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_music_theory.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main script function."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel("DEBUG")
    
    # Your script logic here
    logger.info("Script completed successfully")
```

### Best Practices for Scripts

5. **Documentation**: Clear docstrings and usage examples
6. **Testing**: Scripts should be testable where possible
# pyproject.toml
[tool.poetry.scripts]
format-code = "scripts.format_code:main"
validate-data = "scripts.validate_data:main"
setup-dev = "scripts.setup_dev:main"
```

## 🔍 Troubleshooting Scripts

### Common Issues

#### Permission Errors
```bash

```bash
# Ensure you're in the project root
cd /path/to/LLM-MusicTheory

# Use Poetry environment
poetry shell
python scripts/script_name.py
```

#### Missing Dependencies
```bash
# Install all dependencies
poetry install

# Install with development dependencies
poetry install --with dev
```

### Getting Help

For script-specific help:
```bash
python scripts/script_name.py --help
```

For general issues:
- Check the [Troubleshooting Guide](../docs/troubleshooting.md)
- Open an issue with the `scripts` label
- Contact the development team

## 📊 Script Metrics

### Test Runner Performance
- **Full test suite**: ~0.5 seconds
- **Individual categories**: ~0.1-0.2 seconds  
- **Coverage generation**: +0.2 seconds
- **Parallel execution**: 2-3x speedup

### Code Quality Tools
- **Black formatting**: ~0.1 seconds
- **isort imports**: ~0.1 seconds
- **Linting (flake8)**: ~0.3 seconds
- **Type checking (mypy)**: ~0.5 seconds

## 🤝 Contributing Scripts

To contribute a new script:

1. **Create** the script following the template
2. **Test** it thoroughly in different environments
3. **Document** usage and requirements
4. **Add** it to this README
5. **Submit** a pull request

### Script Review Checklist

- [ ] Follows naming conventions
- [ ] Includes proper error handling
- [ ] Has comprehensive help text
- [ ] Uses project logging standards
- [ ] Includes usage examples
- [ ] Works in CI/CD environment

---

*For script-related issues, please [open an issue](https://github.com/liampond/LLM-MusicTheory/issues) with the `scripts` label.*
