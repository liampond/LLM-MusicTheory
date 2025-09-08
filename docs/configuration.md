# Configuration Guide

Learn how to configure LLM-MusicTheory for your specific}
```

### Output Configurationvironment Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Keys (at least one required)
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Output Configuration
OUTPUT_BASE_DIR=output
DEFAULT_MODEL=gemini-2.0-flash-exp
DEFAULT_ENCODED_TYPE=musicxml
```

### System Configuration

**Poetry Configuration**
```bash
# Use in-project virtual environments
poetry config virtualenvs.in-project true

# Configure PyPI settings
poetry config repositories.pypi-public https://pypi.org/simple/
```

**Python Path Configuration**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PYTHONPATH="${PYTHONPATH}:/path/to/LLM-MusicTheory/src"
```

## Model Configuration

### Default Model Settings

Models are configured in `src/llm_music_theory/models/`. Each model has specific settings:

#### Google Gemini
```python
# In models/gemini.py
DEFAULT_SETTINGS = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

#### OpenAI Models
```python
# In models/chatgpt.py
DEFAULT_SETTINGS = {
    "temperature": 0.1,
    "max_tokens": 4096,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}
```

#### Anthropic Claude
```python
# In models/claude.py
DEFAULT_SETTINGS = {
    "temperature": 0.1,
    "max_tokens": 4096,
    "top_p": 1.0,
}
```

### Custom Model Configuration

You can override default settings by modifying the model files or by creating custom configurations:

```python
# Example: Custom Gemini configuration
from llm_music_theory.models.gemini import GeminiModel

custom_model = GeminiModel(
    model_name="gemini-2.0-flash-exp",
    temperature=0.0,  # More deterministic
    max_output_tokens=2048,  # Shorter responses
)
```

## Prompt Configuration

### Base Prompts

Base prompts are stored in `src/llm_music_theory/prompts/base/`:

- `base_musicxml.txt`: For MusicXML format context
- `base_mei.txt`: For MEI format context
- `base_abc.txt`: For ABC notation context
- `base_humdrum.txt`: For Humdrum format context

### Customizing Base Prompts

To customize prompts for your use case:

1. **Copy existing prompt**:
   ```bash
   cp src/llm_music_theory/prompts/base/base_musicxml.txt \
      src/llm_music_theory/prompts/base/base_musicxml_custom.txt
   ```

2. **Modify the prompt** to include your specific instructions

3. **Update prompt builder** to use your custom prompt:
   ```python
   # In prompts/prompt_builder.py
   def get_base_prompt(self, encoded_type: str) -> str:
       if encoded_type == "musicxml":
           return self._load_prompt("base/base_musicxml_custom.txt")
       # ... other formats
   ```

### Question-Specific Prompts

Questions are stored in `src/llm_music_theory/prompts/questions/`:

**No Context Questions**: `no_context/Q1b.txt`
```text
Analyze the following counterpoint exercise...
```

**Context Questions**: `context/{format}/Q1b.txt`
```text
Given the musical score in {format} format below, analyze...

{encoded_content}

Question: ...
```

## Output Configuration

### Output Directory Structure

Configure output organization:

```python
# In config/settings.py
OUTPUT_STRUCTURE = {
    "base_dir": "output",
    "context_subdir": "context",
    "no_context_subdir": "no_context",
    "model_subdirs": True,  # Create subdirectories per model
    "timestamp_dirs": False,  # Add timestamp to directory names
}
```

### File Naming Conventions

Customize output file naming:

```python
# In config/settings.py
FILE_NAMING = {
    "include_timestamp": False,
    "include_model_name": False,
    "include_format": True,  # Include input format in filename
    "extension_strategy": "match_input",  # or "always_txt"
}
```

## Advanced Configuration

### Custom Model Implementation

To add a new model provider:

1. **Create model class**:
   ```python
   # In models/custom_model.py
   from .base import BaseModel
   
   class CustomModel(BaseModel):
       def __init__(self, model_name: str, **kwargs):
           super().__init__(model_name, **kwargs)
           # Initialize your model client
   
       async def generate_response(self, prompt: str) -> str:
           # Implement your model's response generation
           pass
   ```

2. **Register in dispatcher**:
   ```python
   # In core/dispatcher.py
   from ..models.custom_model import CustomModel
   
   MODEL_MAPPING = {
       # ... existing models
       "custom-model-name": CustomModel,
   }
   ```

### Custom Question Types

To add new question categories:

1. **Create question directory structure**:
   ```bash
   mkdir -p src/llm_music_theory/prompts/questions/context/your_category
   mkdir -p src/llm_music_theory/prompts/questions/no_context/your_category
   ```

2. **Add question files**:
   ```bash
   # Context version for each format
   echo "Your question text..." > \
     src/llm_music_theory/prompts/questions/context/musicxml/your_question.txt
   
   # No-context version
   echo "Your question text..." > \
     src/llm_music_theory/prompts/questions/no_context/your_question.txt
   ```

3. **Update question loader** if needed for special handling

### Performance Tuning

#### Memory Usage
```python
# In config/settings.py
MEMORY_SETTINGS = {
    "max_prompt_length": 50000,  # Characters
    "chunk_large_files": True,
    "cache_prompts": False,  # For repeated questions
}
```

#### Concurrency
```python
# In config/settings.py
CONCURRENCY_SETTINGS = {
    "max_concurrent_requests": 5,
    "request_timeout": 60,  # Seconds
    "retry_attempts": 3,
    "retry_delay": 1.0,  # Seconds
}
```

#### Rate Limiting
```python
# In config/settings.py
RATE_LIMIT_SETTINGS = {
    "requests_per_minute": {
        "openai": 3000,
        "anthropic": 1000,
        "google": 1500,
    },
    "tokens_per_minute": {
        "openai": 150000,
        "anthropic": 100000,
        "google": 32000,
    }
}
```

## Configuration Validation

### Validating Your Setup

Run configuration validation:

```bash
# Test configuration
python -c "
from llm_music_theory.config.settings import validate_config
validate_config()
print('Configuration valid!')
"

# Test API keys
python -c "
from llm_music_theory.core.dispatcher import ModelDispatcher
dispatcher = ModelDispatcher()
for model in ['gemini-2.0-flash-exp', 'gpt-4o']:
    try:
        dispatcher.get_model(model)
        print(f'✓ {model} configured correctly')
    except Exception as e:
        print(f'✗ {model} error: {e}')
"
```

### Configuration Best Practices

1. **Security**:
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate API keys regularly

2. **Performance**:
   - Start with smaller models for testing
   - Use appropriate temperature settings (0.1 for analytical tasks)
   - Monitor API usage and costs

3. **Maintainability**:
   - Document custom configurations
   - Version control configuration files (without secrets)
   - Test configurations after changes

4. **Reproducibility**:
   - Use consistent random seeds when available
   - Document model versions and settings
   - Keep configuration separate from code

## Next Steps

- [Adding Questions](adding-questions.md) - Learn to add your own questions
- [Adding Questions](adding-questions.md) - Learn to add your own questions
- [Examples](examples.md) - Efficient multi-question analysis
- [API Reference](api-reference.md) - Programming interface details
