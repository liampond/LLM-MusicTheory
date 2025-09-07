# Development Guide

Guide for developers contributing to LLM-MusicTheory.

## Development Setup

### Environment Setup

1. **Clone and setup development environment**:
   ```bash
   git clone https://github.com/your-repo/LLM-MusicTheory.git
   cd LLM-MusicTheory
   
   # Install in development mode
   poetry install --with dev
   poetry shell
   
   # Install pre-commit hooks
   pre-commit install
   ```

2. **Configure development tools**:
   ```bash
   # Setup pytest configuration
   pytest --version
   
   # Setup linting
   ruff check src/
   black --check src/
   mypy src/
   ```

3. **Run tests to verify setup**:
   ```bash
   # Run all tests
   pytest
   
   # Run specific test categories
   pytest tests/test_models.py -v
   pytest tests/test_prompt_building.py -v
   ```

### Project Structure

```
LLM-MusicTheory/
├── src/llm_music_theory/          # Main package
│   ├── __init__.py
│   ├── cli/                       # Command-line interfaces
│   ├── config/                    # Configuration management
│   ├── core/                      # Core functionality
│   ├── models/                    # LLM model implementations
│   ├── prompts/                   # Prompt management
│   └── utils/                     # Utility functions
├── tests/                         # Test suite
├── docs/                          # Documentation
├── data/                          # Research data (read-only)
├── output/                        # Generated outputs
├── pyproject.toml                 # Project configuration
├── pytest.ini                    # Testing configuration
└── README.md                      # Project overview
```

## Code Style and Standards

### Python Code Style

We use several tools to maintain code quality:

**Black** for code formatting:
```bash
black src/ tests/
```

**Ruff** for linting:
```bash
ruff check src/ tests/
ruff check src/ tests/ --fix  # Auto-fix issues
```

**MyPy** for type checking:
```bash
mypy src/
```

**isort** for import sorting:
```bash
isort src/ tests/
```

### Type Hints

All new code should include type hints:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def analyze_question(
    question: str,
    model_name: str,
    encoded_type: Optional[str] = None,
    use_context: bool = True
) -> str:
    """Analyze a music theory question.
    
    Args:
        question: Question identifier (e.g., "Q1b")
        model_name: Name of the LLM model to use
        encoded_type: Music encoding format (musicxml, mei, abc, humdrum)
        use_context: Whether to include musical context
        
    Returns:
        Model's analysis response
        
    Raises:
        FileNotFoundError: If question or encoded files not found
        ValueError: If invalid parameters provided
    """
    # Implementation...
```

### Docstring Standards

Use Google-style docstrings:

```python
def process_response(response: str, format_type: str) -> Dict[str, Any]:
    """Process and analyze a model response.
    
    This function extracts structured information from free-form model
    responses, including musical analysis elements and metadata.
    
    Args:
        response: Raw response text from the model
        format_type: Music format used ("musicxml", "mei", etc.)
        
    Returns:
        Dictionary containing:
            - parsed_content: Structured analysis content
            - metadata: Response metadata (length, timing, etc.)
            - errors: Any parsing errors encountered
            
    Example:
        >>> response = "This piece is in C major with I-V-I progression"
        >>> result = process_response(response, "musicxml")
        >>> print(result["parsed_content"]["key"])
        "C major"
    """
    # Implementation...
```

## Testing Guidelines

### Test Structure

Tests are organized by functionality:

```
tests/
├── test_models.py              # Model implementation tests
├── test_prompt_building.py     # Prompt construction tests
├── test_runner.py              # Core runner functionality
├── test_path_utils.py          # Utility function tests
├── test_integration.py         # Integration tests
└── test_comprehensive.py       # End-to-end tests
```

### Writing Tests

**Unit Tests**:
```python
import pytest
from unittest.mock import Mock, patch
from llm_music_theory.prompts.prompt_builder import PromptBuilder

class TestPromptBuilder:
    """Test cases for PromptBuilder class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.builder = PromptBuilder()
    
    def test_get_question_text_valid_question(self):
        """Test loading valid question text."""
        question_text = self.builder.get_question_text("Q1b")
        
        assert isinstance(question_text, str)
        assert len(question_text) > 0
        assert "counterpoint" in question_text.lower()
    
    def test_get_question_text_invalid_question(self):
        """Test handling of invalid question."""
        with pytest.raises(FileNotFoundError):
            self.builder.get_question_text("INVALID_QUESTION")
    
    @patch('llm_music_theory.utils.path_utils.find_encoded_file')
    def test_get_encoded_content_mocked(self, mock_find_file):
        """Test encoded content loading with mocked file system."""
        # Setup mock
        mock_path = Mock()
        mock_path.read_text.return_value = "<?xml version='1.0'?>..."
        mock_find_file.return_value = mock_path
        
        # Test
        content = self.builder.get_encoded_content("Q1b", "musicxml")
        
        # Assertions
        assert content == "<?xml version='1.0'?>..."
        mock_find_file.assert_called_once_with("Q1b", "musicxml")
```

**Integration Tests**:
```python
import pytest
from llm_music_theory.core.runner import PromptRunner

class TestIntegration:
    """Integration tests requiring real files and setup."""
    
    def test_full_prompt_building_workflow(self):
        """Test complete prompt building workflow."""
        runner = PromptRunner()
        
        # This test requires actual question and encoded files
        prompt = runner._build_prompt("Q1b", "musicxml", True)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 1000  # Should be substantial
        assert "Q1b" in prompt
        assert "<?xml" in prompt  # Should contain MusicXML
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="API key required for integration test"
    )
    def test_actual_api_call(self):
        """Test with actual API call (requires API key)."""
        runner = PromptRunner()
        
        response = runner.run_analysis(
            question="Q1b",
            model_name="gemini-2.0-flash-exp",
            encoded_type="musicxml",
            use_context=True
        )
        
        assert isinstance(response, str)
        assert len(response) > 100
```

### Test Configuration

**pytest.ini**:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (may require API calls)
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**Running Tests**:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py -v

# Specific test method
pytest tests/test_models.py::TestPromptBuilder::test_get_question_text -v

# Skip slow tests
pytest -m "not slow"

# Only integration tests
pytest -m integration

# With coverage
pytest --cov=src/llm_music_theory --cov-report=html
```

## Adding New Features

### Adding a New Model

1. **Create model class**:
   ```python
   # src/llm_music_theory/models/new_model.py
   from .base import BaseModel
   import requests
   
   class NewModel(BaseModel):
       """Implementation for New Model API."""
       
       def __init__(self, model_name: str, **kwargs):
           super().__init__(model_name, **kwargs)
           self.api_key = os.getenv("NEW_MODEL_API_KEY")
           if not self.api_key:
               raise ValueError("NEW_MODEL_API_KEY environment variable required")
       
       def generate_response(self, prompt: str) -> str:
           """Generate response using New Model API."""
           try:
               response = requests.post(
                   "https://api.newmodel.com/v1/generate",
                   headers={
                       "Authorization": f"Bearer {self.api_key}",
                       "Content-Type": "application/json"
                   },
                   json={
                       "prompt": prompt,
                       "temperature": self.temperature,
                       "max_tokens": self.max_tokens
                   }
               )
               response.raise_for_status()
               
               return response.json()["generated_text"]
               
           except Exception as e:
               raise ModelError(f"New Model API error: {e}")
   ```

2. **Register in dispatcher**:
   ```python
   # src/llm_music_theory/core/dispatcher.py
   from ..models.new_model import NewModel
   
   MODEL_MAPPING = {
       # ... existing models
       "new-model-name": NewModel,
   }
   ```

3. **Add tests**:
   ```python
   # tests/test_new_model.py
   import pytest
   from unittest.mock import Mock, patch
   from llm_music_theory.models.new_model import NewModel
   
   class TestNewModel:
       def test_initialization(self):
           with patch.dict(os.environ, {"NEW_MODEL_API_KEY": "test-key"}):
               model = NewModel("new-model-name")
               assert model.model_name == "new-model-name"
               assert model.api_key == "test-key"
       
       def test_missing_api_key(self):
           with patch.dict(os.environ, {}, clear=True):
               with pytest.raises(ValueError, match="NEW_MODEL_API_KEY"):
                   NewModel("new-model-name")
   ```

4. **Update documentation**:
   - Add to supported models list
   - Update configuration guide
   - Add usage examples

### Adding a New Music Format

1. **Add encoded files**:
   ```bash
   mkdir -p src/llm_music_theory/encoded/new_format
   # Add your encoded files here
   ```

2. **Add base prompt**:
   ```bash
   # src/llm_music_theory/prompts/base/base_new_format.txt
   You are analyzing a musical score provided in NEW_FORMAT format.
   
   NEW_FORMAT is a music encoding standard that...
   [Detailed explanation of the format]
   
   When analyzing the music, consider:
   - How NEW_FORMAT represents musical elements
   - Specific features of this encoding
   - Best practices for interpretation
   
   Provide your analysis in a clear, structured format.
   ```

3. **Add question templates**:
   ```bash
   mkdir -p src/llm_music_theory/prompts/questions/context/new_format
   # Add question files for this format
   ```

4. **Update prompt builder**:
   ```python
   # src/llm_music_theory/prompts/prompt_builder.py
   def get_base_prompt(self, encoded_type: str) -> str:
       """Get base prompt for the specified encoding type."""
       base_prompts = {
           "musicxml": "base/base_musicxml.txt",
           "mei": "base/base_mei.txt", 
           "abc": "base/base_abc.txt",
           "humdrum": "base/base_humdrum.txt",
           "new_format": "base/base_new_format.txt",  # Add this
       }
       
       if encoded_type not in base_prompts:
           raise ValueError(f"Unsupported encoding type: {encoded_type}")
           
       return self._load_prompt(base_prompts[encoded_type])
   ```

5. **Update configuration**:
   ```python
   # src/llm_music_theory/config/settings.py
   SUPPORTED_FORMATS = [
       "musicxml",
       "mei", 
       "abc",
       "humdrum",
       "new_format"  # Add this
   ]
   ```

6. **Add tests**:
   ```python
   # tests/test_new_format.py
   def test_new_format_support():
       builder = PromptBuilder()
       
       # Test base prompt loading
       base_prompt = builder.get_base_prompt("new_format")
       assert "NEW_FORMAT" in base_prompt
       
       # Test encoded content loading
       content = builder.get_encoded_content("Q1b", "new_format")
       assert len(content) > 0
   ```

### Adding New Questions

1. **Create question files**:
   ```bash
   # No-context version
   echo "Your question text here..." > \
     src/llm_music_theory/prompts/questions/no_context/Q2a.txt
   
   # Context versions for each format
   for format in musicxml mei abc humdrum; do
     echo "Context-aware question for $format..." > \
       src/llm_music_theory/prompts/questions/context/$format/Q2a.txt
   done
   ```

2. **Add encoded content**:
   ```bash
   # Add musical content in all supported formats
   cp your_content.musicxml src/llm_music_theory/encoded/musicxml/Q2a.musicxml
   cp your_content.mei src/llm_music_theory/encoded/mei/Q2a.mei
   cp your_content.abc src/llm_music_theory/encoded/abc/Q2a.abc
   cp your_content.krn src/llm_music_theory/encoded/humdrum/Q2a.krn
   ```

3. **Test the new question**:
   ```bash
   python -m llm_music_theory.cli.run_single \
     --question Q2a \
     --model gemini-2.0-flash-exp \
     --encoded_type musicxml \
     --context
   ```

4. **Add validation tests**:
   ```python
   # tests/test_questions.py
   def test_q2a_question_loading():
       builder = PromptBuilder()
       
       # Test no-context loading
       question = builder.get_question_text("Q2a")
       assert len(question) > 0
       
       # Test context loading for each format
       for format_type in ["musicxml", "mei", "abc", "humdrum"]:
           question = builder.get_question_text("Q2a", format_type, True)
           assert len(question) > 0
           assert "Q2a" in question  # or appropriate content check
   ```

## Code Review Process

### Pull Request Guidelines

1. **Branch naming**: Use descriptive names
   - `feature/add-new-model`
   - `fix/prompt-encoding-issue`
   - `docs/update-api-reference`

2. **Commit messages**: Follow conventional commits
   ```
   feat: add support for new LLM model
   fix: resolve file extension issue in output
   docs: update installation guide
   test: add integration tests for prompt building
   refactor: simplify model dispatcher logic
   ```

3. **Pull request template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Integration tests verified
   
   ## Documentation
   - [ ] Code is well documented
   - [ ] README updated if needed
   - [ ] API documentation updated
   ```

### Code Review Checklist

**Functionality**:
- [ ] Code works as intended
- [ ] Edge cases handled appropriately
- [ ] Error handling is robust
- [ ] No obvious bugs or logic errors

**Code Quality**:
- [ ] Follows project coding standards
- [ ] Proper type hints included
- [ ] Good variable and function names
- [ ] Appropriate comments and docstrings

**Testing**:
- [ ] Adequate test coverage
- [ ] Tests are meaningful and comprehensive
- [ ] Integration tests included where appropriate
- [ ] Tests pass in CI/CD

**Documentation**:
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README updated if needed
- [ ] Breaking changes noted

## Performance Considerations

### API Rate Limiting

```python
import asyncio
from typing import List

class RateLimitedRunner:
    """Rate-limited analysis runner."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
    
    async def run_with_rate_limit(self, analysis_func, *args, **kwargs):
        """Run analysis with rate limiting."""
        import time
        
        current_time = time.time()
        
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(current_time)
        
        # Execute the analysis
        return analysis_func(*args, **kwargs)
```

### Memory Management

```python
import gc
from typing import Generator

def batch_analysis_generator(
    questions: List[str],
    models: List[str], 
    batch_size: int = 10
) -> Generator[Dict, None, None]:
    """Memory-efficient batch analysis."""
    
    runner = PromptRunner()
    
    for i in range(0, len(questions), batch_size):
        batch_questions = questions[i:i + batch_size]
        
        batch_results = []
        for question in batch_questions:
            for model in models:
                try:
                    result = runner.run_analysis(question, model)
                    batch_results.append({
                        "question": question,
                        "model": model,
                        "result": result
                    })
                except Exception as e:
                    batch_results.append({
                        "question": question,
                        "model": model,
                        "error": str(e)
                    })
        
        yield batch_results
        
        # Clean up memory after each batch
        gc.collect()
```

## Debugging and Troubleshooting

### Logging Setup

```python
import logging
from llm_music_theory.utils.logger import setup_logger

# Development logging
logger = setup_logger(
    name="development",
    level="DEBUG",
    log_file="development.log"
)

# Usage in your code
logger.debug("Debugging prompt construction")
logger.info("Starting analysis for Q1b")
logger.warning("API rate limit approaching")
logger.error("Failed to load encoded file")
```

### Common Development Issues

**Import Errors**:
```bash
# Ensure you're in the poetry environment
poetry shell

# Verify installation
poetry install

# Check Python path
python -c "import sys; print(sys.path)"
```

**Test Failures**:
```bash
# Run specific failing test with verbose output
pytest tests/test_models.py::TestPromptBuilder::test_failing_method -v -s

# Debug with pdb
pytest tests/test_models.py::TestPromptBuilder::test_failing_method --pdb

# Check test coverage
pytest --cov=src/llm_music_theory --cov-report=term-missing
```

**Type Checking Issues**:
```bash
# Run mypy with detailed output
mypy src/ --show-error-codes --show-error-context

# Ignore specific errors temporarily
# type: ignore[error-code]
```

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. **Pre-release**:
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Version bumped in pyproject.toml
   - [ ] API compatibility verified

2. **Release**:
   - [ ] Create release branch
   - [ ] Final testing
   - [ ] Tag release
   - [ ] Create GitHub release
   - [ ] Update documentation

3. **Post-release**:
   - [ ] Monitor for issues
   - [ ] Update development branch
   - [ ] Plan next release

## Contributing Guidelines

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Best Practices

- Start with small, focused changes
- Write tests for new functionality
- Follow existing code patterns
- Update documentation
- Be responsive to code review feedback

## Next Steps

- [API Reference](api-reference.md) - Complete programming interface
- [Examples](examples.md) - Practical usage examples
- [Configuration](configuration.md) - End-user documentation
- [Research Guide](research.md) - Academic research guidance
