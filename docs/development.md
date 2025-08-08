# Development Guide

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Git for version control

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/liampond/LLM-MusicTheory.git
   cd LLM-MusicTheory
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Verify installation:**
   ```bash
   poetry run pytest
   ```

## Development Workflow

### Virtual Environment

Always use Poetry's virtual environment:

```bash
# Activate the environment
poetry shell

# Or run commands with poetry run
poetry run python -m llm_music_theory.cli.run_single --help
```

### Code Style

We follow Python best practices:

- **PEP 8** compliance
- **Type hints** for all public functions
- **Docstrings** for all modules, classes, and functions
- **Black** for code formatting (when available)
- **Import sorting** with standard library first

### Example Code Style

```python
from typing import Optional, List
from pathlib import Path

def find_encoded_file(
    question_number: str,
    datatype: str,
    encoded_dir: Path,
    required: bool = True
) -> Optional[Path]:
    """
    Locate the encoded music file for a given question and format.
    
    Parameters:
        question_number: e.g. "Q1a"
        datatype: one of ["mei","musicxml","abc","humdrum"]
        encoded_dir: base folder where encoded files live
        required: whether to raise exception if file missing

    Returns:
        Path to the file if found, or None if required=False and missing.
        
    Raises:
        ValueError: For unsupported datatype.
        FileNotFoundError: If required=True and file is missing.
    """
    # Implementation here...
```

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_models.py

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=src/llm_music_theory
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Mock Tests**: Test API interactions without real calls

### Writing Tests

#### Unit Test Example

```python
def test_find_project_root():
    """Test that find_project_root correctly locates the project root."""
    root = find_project_root()
    assert root.is_dir()
    assert (root / "pyproject.toml").exists()
```

#### Mock Test Example

```python
@patch('openai.OpenAI')
def test_chatgpt_query(mock_openai):
    """Test ChatGPT model with mocked API response."""
    # Setup mock
    mock_client = Mock()
    mock_openai.return_value = mock_client
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Test
    model = ChatGPT()
    result = model.query(test_input)
    
    assert result == "Test response"
```

### Test Data

- **Use fixtures**: For reusable test data
- **Temporary directories**: For file system tests
- **Mock API responses**: Never make real API calls in tests

## Architecture Guidelines

### Adding New Models

1. **Create model class** inheriting from `LLMInterface`:

```python
from llm_music_theory.models.base import LLMInterface, PromptInput

class NewModel(LLMInterface):
    def __init__(self):
        self.api_key = os.getenv("NEW_MODEL_API_KEY")
        if not self.api_key:
            raise ValueError("NEW_MODEL_API_KEY not found")
    
    def query(self, input: PromptInput) -> str:
        # Implement API call
        pass
```

2. **Add to dispatcher**:

```python
# In src/llm_music_theory/core/dispatcher.py
def get_llm(model_name: str) -> LLMInterface:
    models = {
        "ChatGPT": ChatGPT,
        "Claude": Claude,
        "Gemini": Gemini,
        "DeepSeek": DeepSeek,
        "NewModel": NewModel,  # Add here
    }
    # ...
```

3. **Add tests**:

```python
def test_new_model_query():
    """Test NewModel with mock API response."""
    # Test implementation
```

4. **Update documentation**:
   - Add to API reference
   - Update user guide
   - Add example usage

### Adding New Music Formats

1. **Add base prompt** in `data/LLM-RCM/prompts/base/base_newformat.txt`

2. **Update path utilities** to recognize the format:

```python
# In src/llm_music_theory/utils/path_utils.py
ext_map = {
    "mei": ".mei",
    "musicxml": ".musicxml", 
    "abc": ".abc",
    "humdrum": ".krn",
    "newformat": ".nf",  # Add here
}
```

3. **Add sample data** in `data/LLM-RCM/encoded/newformat/`

4. **Add tests** for the new format

5. **Update documentation**

## Project Structure

### Core Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Models and configurations are injected
- **Testability**: All components can be tested in isolation
- **Extensibility**: Easy to add new models and formats

### Directory Layout

```
src/llm_music_theory/           # Main package
├── cli/                        # Command-line interfaces
├── config/                     # Configuration management
├── core/                       # Business logic
├── models/                     # LLM implementations
├── prompts/                    # Prompt building
└── utils/                      # Utility functions

tests/                          # Test suite
├── test_models.py              # Model tests
├── test_runner.py              # Runner tests
├── test_path_utils.py          # Utility tests
└── ...

data/LLM-RCM/                   # Evaluation data
├── encoded/                    # Music files
├── prompts/                    # Prompt templates
├── questions/                  # Question specifications
└── guides/                     # Context information

docs/                           # Documentation
├── user-guide.md               # User instructions
├── api-reference.md            # API documentation
├── architecture.md             # System design
└── development.md              # This file
```

## Code Quality

### Static Analysis

We recommend using these tools (install separately):

```bash
# Type checking
mypy src/llm_music_theory/

# Linting
pylint src/llm_music_theory/

# Security analysis
bandit -r src/llm_music_theory/
```

### Documentation

- **Docstrings**: All public functions must have docstrings
- **Type hints**: Use for all function parameters and returns
- **Comments**: Explain complex logic, not obvious code
- **README updates**: Keep documentation current

### Error Handling

- **Specific exceptions**: Use appropriate exception types
- **Helpful messages**: Include context in error messages
- **Graceful degradation**: Continue when possible
- **Logging**: Log errors for debugging

## Performance Considerations

### Current Limitations

- **Sequential API calls**: No concurrency
- **Memory usage**: Loads all prompts into memory
- **File I/O**: Synchronous operations

### Optimization Opportunities

- **Async/await**: For concurrent API calls
- **Caching**: Response caching for repeated evaluations
- **Streaming**: For large file processing
- **Database**: Replace file-based storage

## Debugging

### Common Issues

1. **Import errors**: Use `poetry run` or activate virtual environment
2. **API key errors**: Check `.env` file configuration
3. **Path issues**: Verify data directory structure
4. **Test failures**: Check mock configurations

### Debug Commands

```bash
# Verbose test output
poetry run pytest -v -s

# Print environment info
poetry env info

# Check installed packages
poetry show

# Debug specific test
poetry run pytest tests/test_models.py::test_chatgpt_query -v -s
```

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing Workflow

### Before Making Changes

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Update dependencies**: `poetry install`
3. **Run tests**: `poetry run pytest`

### Development Process

1. **Write tests first**: Test-driven development
2. **Implement feature**: Follow coding standards
3. **Update documentation**: Keep docs current
4. **Test thoroughly**: All tests must pass

### Before Submitting

1. **Run full test suite**: `poetry run pytest`
2. **Check code style**: Follow established patterns
3. **Update documentation**: Include API docs and user guide
4. **Commit message**: Use clear, descriptive messages

```bash
# Good commit messages
git commit -m "Add support for MusicXML v4.0 format"
git commit -m "Fix temperature parameter validation in Claude model"
git commit -m "Improve error handling for missing API keys"
```

## Release Process

### Version Management

We use semantic versioning (SemVer):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if exists)
3. Run full test suite
4. Update documentation
5. Create git tag
6. Build and publish (if applicable)

## Environment Management

### Dependencies

- **Core dependencies**: Listed in `pyproject.toml` `[tool.poetry.dependencies]`
- **Development dependencies**: Listed in `[tool.poetry.group.dev.dependencies]`
- **Lock file**: `poetry.lock` ensures reproducible installs

### Adding Dependencies

```bash
# Add runtime dependency
poetry add requests

# Add development dependency
poetry add --group dev pytest-cov

# Update dependencies
poetry update
```

### Python Version

- **Minimum**: Python 3.11
- **Testing**: Test against supported versions
- **Compatibility**: Consider backward compatibility
