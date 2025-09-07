# API Reference

Complete reference for the LLM-MusicTheory programming interface.

## Core Classes

### ModelDispatcher

Central dispatcher for managing different LLM models.

```python
from llm_music_theory.core.dispatcher import ModelDispatcher

dispatcher = ModelDispatcher()
model = dispatcher.get_model("gemini-2.0-flash-exp")
```

#### Methods

**`get_model(model_name: str) -> BaseModel`**
- Returns an instance of the specified model
- Raises `ValueError` if model not found or not configured
- Available models: See [Supported Models](#supported-models)

**`list_available_models() -> List[str]`**
- Returns list of all configured model names
- Only includes models with valid API keys

#### Example Usage

```python
dispatcher = ModelDispatcher()

# Get specific model
gemini = dispatcher.get_model("gemini-2.0-flash-exp")

# List all available models
models = dispatcher.list_available_models()
print(f"Available models: {models}")
```

### PromptRunner

Executes music theory analysis tasks with specified models.

```python
from llm_music_theory.core.runner import PromptRunner

runner = PromptRunner()
```

#### Methods

**`run_analysis(question: str, model_name: str, encoded_type: Optional[str] = None, use_context: bool = True) -> str`**

Runs a complete music theory analysis.

**Parameters:**
- `question` (str): Question identifier (e.g., "Q1b")
- `model_name` (str): Model to use for analysis
- `encoded_type` (Optional[str]): Music format type ("musicxml", "mei", "abc", "humdrum")
- `use_context` (bool): Whether to include musical context

**Returns:**
- `str`: Model's response to the analysis question

**Raises:**
- `FileNotFoundError`: If question or encoded files not found
- `ValueError`: If invalid parameters provided
- `APIError`: If model API call fails

#### Example Usage

```python
runner = PromptRunner()

# Run analysis with context
response = runner.run_analysis(
    question="Q1b",
    model_name="gemini-2.0-flash-exp",
    encoded_type="musicxml",
    use_context=True
)

# Run analysis without context
response = runner.run_analysis(
    question="Q1b",
    model_name="gpt-4o",
    use_context=False
)
```

### PromptBuilder

Constructs prompts for music theory questions.

```python
from llm_music_theory.prompts.prompt_builder import PromptBuilder

builder = PromptBuilder()
```

#### Methods

**`build_prompt(question: str, encoded_type: Optional[str] = None, use_context: bool = True) -> str`**

Builds a complete prompt for analysis.

**Parameters:**
- `question` (str): Question identifier
- `encoded_type` (Optional[str]): Music format type
- `use_context` (bool): Whether to include musical context

**Returns:**
- `str`: Complete prompt ready for model input

**`get_question_text(question: str, encoded_type: Optional[str] = None, use_context: bool = True) -> str`**

Gets the question text without base prompt.

**`get_encoded_content(question: str, encoded_type: str) -> str`**

Loads and returns encoded musical content.

#### Example Usage

```python
builder = PromptBuilder()

# Build complete prompt with context
prompt = builder.build_prompt(
    question="Q1b",
    encoded_type="musicxml",
    use_context=True
)

# Get just the question text
question_text = builder.get_question_text("Q1b")

# Get encoded content
content = builder.get_encoded_content("Q1b", "musicxml")
```

## Model Classes

All model classes inherit from `BaseModel` and implement the same interface.

### BaseModel

Abstract base class for all LLM models.

```python
from llm_music_theory.models.base import BaseModel
```

#### Abstract Methods

**`generate_response(prompt: str) -> str`**
- Must be implemented by all model classes
- Takes a prompt string and returns model response
- Should handle API errors appropriately

#### Common Properties

- `model_name`: String identifier for the model
- `temperature`: Sampling temperature (0.0-1.0)
- `max_tokens`: Maximum response length

### GeminiModel

Google Gemini model implementation.

```python
from llm_music_theory.models.gemini import GeminiModel

model = GeminiModel(
    model_name="gemini-2.0-flash-exp",
    temperature=0.1,
    max_output_tokens=4096
)
```

#### Constructor Parameters

- `model_name` (str): Gemini model variant
- `temperature` (float): Sampling temperature (default: 0.1)
- `max_output_tokens` (int): Maximum response tokens (default: 8192)
- `top_p` (float): Nucleus sampling parameter (default: 0.95)
- `top_k` (int): Top-k sampling parameter (default: 40)

#### Available Models

- `gemini-2.0-flash-exp`: Latest experimental model
- `gemini-1.5-pro`: Production-ready model
- `gemini-1.5-flash`: Fast, efficient model

### ChatGPTModel

OpenAI GPT model implementation.

```python
from llm_music_theory.models.chatgpt import ChatGPTModel

model = ChatGPTModel(
    model_name="gpt-4o",
    temperature=0.1,
    max_tokens=4096
)
```

#### Constructor Parameters

- `model_name` (str): OpenAI model variant
- `temperature` (float): Sampling temperature (default: 0.1)
- `max_tokens` (int): Maximum response tokens (default: 4096)
- `top_p` (float): Nucleus sampling parameter (default: 1.0)
- `frequency_penalty` (float): Frequency penalty (default: 0.0)
- `presence_penalty` (float): Presence penalty (default: 0.0)

#### Available Models

- `gpt-4o`: GPT-4 Omni model
- `gpt-4o-mini`: Smaller, faster GPT-4 variant
- `o1-preview`: Reasoning-focused model
- `o1-mini`: Smaller reasoning model

### ClaudeModel

Anthropic Claude model implementation.

```python
from llm_music_theory.models.claude import ClaudeModel

model = ClaudeModel(
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=4096
)
```

#### Constructor Parameters

- `model_name` (str): Claude model variant
- `temperature` (float): Sampling temperature (default: 0.1)
- `max_tokens` (int): Maximum response tokens (default: 4096)
- `top_p` (float): Nucleus sampling parameter (default: 1.0)

#### Available Models

- `claude-3-5-sonnet-20241022`: Latest Sonnet model
- `claude-3-5-haiku-20241022`: Fast Haiku model

### DeepSeekModel

DeepSeek model implementation.

```python
from llm_music_theory.models.deepseek import DeepSeekModel

model = DeepSeekModel(
    model_name="deepseek-v3",
    temperature=0.1,
    max_tokens=4096
)
```

#### Constructor Parameters

- `model_name` (str): DeepSeek model variant
- `temperature` (float): Sampling temperature (default: 0.1)
- `max_tokens` (int): Maximum response tokens (default: 4096)
- `top_p` (float): Nucleus sampling parameter (default: 1.0)

#### Available Models

- `deepseek-v3`: Latest DeepSeek model

## Utility Functions

### Path Utilities

```python
from llm_music_theory.utils.path_utils import (
    find_encoded_file,
    get_project_root,
    ensure_output_directory
)
```

**`find_encoded_file(question: str, encoded_type: str) -> Path`**
- Locates encoded music files for questions
- Returns `Path` object to the file
- Raises `FileNotFoundError` if not found

**`get_project_root() -> Path`**
- Returns path to project root directory
- Useful for constructing relative paths

**`ensure_output_directory(output_path: Path) -> None`**
- Creates output directory if it doesn't exist
- Creates parent directories as needed

#### Example Usage

```python
from llm_music_theory.utils.path_utils import find_encoded_file

# Find encoded file
file_path = find_encoded_file("Q1b", "musicxml")
print(f"Found file: {file_path}")

# Get project root
root = get_project_root()
output_dir = root / "output" / "custom"
ensure_output_directory(output_dir)
```

### Logger Configuration

```python
from llm_music_theory.utils.logger import setup_logger

# Setup logger with custom configuration
logger = setup_logger(
    name="my_analysis",
    level="DEBUG",
    log_file="analysis.log"
)

logger.info("Starting analysis...")
```

**`setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger`**

Configures a logger with appropriate formatting.

**Parameters:**
- `name` (str): Logger name
- `level` (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- `log_file` (Optional[str]): Optional log file path

## Configuration

### Settings Module

```python
from llm_music_theory.config.settings import (
    OUTPUT_BASE_DIR,
    SUPPORTED_MODELS,
    SUPPORTED_FORMATS
)
```

#### Constants

- `OUTPUT_BASE_DIR`: Default output directory path
- `SUPPORTED_MODELS`: Dictionary of supported model configurations
- `SUPPORTED_FORMATS`: List of supported music encoding formats
- `DEFAULT_TEMPERATURE`: Default temperature for model sampling

#### Environment Variables

The system reads these environment variables:

- `GOOGLE_API_KEY`: Google Gemini API key
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `LOG_LEVEL`: Logging level (default: "INFO")
- `OUTPUT_BASE_DIR`: Custom output directory

## Error Handling

### Exception Classes

```python
from llm_music_theory.models.base import ModelError
```

**`ModelError`**: Base exception for model-related errors
**`APIError`**: API communication errors
**`ConfigurationError`**: Configuration and setup errors
**`ValidationError`**: Input validation errors

### Error Handling Best Practices

```python
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import ModelError

runner = PromptRunner()

try:
    response = runner.run_analysis(
        question="Q1b",
        model_name="gemini-2.0-flash-exp",
        encoded_type="musicxml"
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ModelError as e:
    print(f"Model error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom Model Implementation

```python
from llm_music_theory.models.base import BaseModel

class CustomModel(BaseModel):
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        # Initialize your model client
        self.client = YourModelClient()
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using your custom model."""
        try:
            response = self.client.generate(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.text
        except Exception as e:
            raise ModelError(f"Custom model error: {e}")

# Register your model
from llm_music_theory.core.dispatcher import ModelDispatcher
dispatcher = ModelDispatcher()
dispatcher.register_model("custom-model", CustomModel)
```

### Batch Processing

```python
from llm_music_theory.core.runner import PromptRunner
import asyncio

async def batch_analysis():
    """Run analysis on multiple questions."""
    runner = PromptRunner()
    
    questions = ["Q1b"]  # Add more questions
    models = ["gemini-2.0-flash-exp", "gpt-4o"]
    
    results = {}
    
    for question in questions:
        results[question] = {}
        for model in models:
            try:
                response = runner.run_analysis(
                    question=question,
                    model_name=model,
                    encoded_type="musicxml"
                )
                results[question][model] = response
            except Exception as e:
                results[question][model] = f"Error: {e}"
    
    return results

# Run batch analysis
results = asyncio.run(batch_analysis())
```

### Custom Output Handling

```python
from llm_music_theory.core.runner import PromptRunner
from pathlib import Path
import json

def save_analysis_with_metadata(
    question: str,
    model: str,
    response: str,
    metadata: dict
):
    """Save analysis with additional metadata."""
    
    output_dir = Path("output") / "custom_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save response
    response_file = output_dir / f"{question}_{model}_response.txt"
    with open(response_file, "w") as f:
        f.write(response)
    
    # Save metadata
    metadata_file = output_dir / f"{question}_{model}_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

# Usage
runner = PromptRunner()
response = runner.run_analysis("Q1b", "gemini-2.0-flash-exp")

metadata = {
    "timestamp": "2024-01-01T12:00:00",
    "model_version": "gemini-2.0-flash-exp",
    "context_type": "musicxml",
    "researcher": "Your Name"
}

save_analysis_with_metadata("Q1b", "gemini-2.0-flash-exp", response, metadata)
```

## Testing

### Unit Testing

```python
import pytest
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.prompts.prompt_builder import PromptBuilder

def test_prompt_builder():
    """Test prompt building functionality."""
    builder = PromptBuilder()
    
    # Test question loading
    question_text = builder.get_question_text("Q1b")
    assert len(question_text) > 0
    
    # Test prompt building
    prompt = builder.build_prompt("Q1b", "musicxml", True)
    assert "Q1b" in prompt
    assert len(prompt) > len(question_text)

def test_runner():
    """Test analysis runner."""
    runner = PromptRunner()
    
    # This would require actual API keys for full testing
    # Use mocking for unit tests
    pass
```

### Integration Testing

```python
def test_full_analysis_workflow():
    """Test complete analysis workflow."""
    from llm_music_theory.core.runner import PromptRunner
    
    runner = PromptRunner()
    
    # Test with actual API (requires valid keys)
    try:
        response = runner.run_analysis(
            question="Q1b",
            model_name="gemini-2.0-flash-exp",
            encoded_type="musicxml"
        )
        assert len(response) > 0
        print("Integration test passed!")
    except Exception as e:
        print(f"Integration test failed: {e}")
```

## Migration Guide

### From Version 1.x to 2.x

**API Changes:**
- `run_analysis()` now returns string instead of dict
- Output file extensions now match input format
- New required parameters for some methods

**Migration Steps:**
1. Update method calls to use new signatures
2. Update output file handling code
3. Test with new model versions

## Next Steps

- [Examples](examples.md) - Practical usage examples
- [Configuration](configuration.md) - Detailed usage information  
- [Development](development.md) - Contributing to the project
- [Research](research.md) - Academic research guidance
