# API Reference

## Core Classes

### LLMInterface (Abstract Base Class)

Abstract interface for all LLM implementations.

```python
from llm_music_theory.models.base import LLMInterface, PromptInput

class LLMInterface(ABC):
    @abstractmethod
    def query(self, input: PromptInput) -> str:
        """Send prompt to LLM and return response."""
        pass
```

**Parameters:**
- `input` (PromptInput): Contains system prompt, user prompt, and parameters

**Returns:**
- `str`: The LLM's response as plain text

### PromptInput

Data class containing all parameters for an LLM request.

```python
@dataclass
class PromptInput:
    system_prompt: str            # System-level instructions
    user_prompt: str              # Main prompt content
    temperature: float = 0.0      # Sampling temperature (0.0-2.0)
    model_name: Optional[str] = None   # Override default model
    max_tokens: Optional[int] = None   # Response token limit
```

### PromptRunner

Main execution engine for running evaluations.

```python
from llm_music_theory.core.runner import PromptRunner

runner = PromptRunner(
    model=llm_instance,
    question_number="Q1b",
    datatype="mei",
    context=True,
    exam_date="",
    base_dirs=base_directories,
    temperature=0.7,
    max_tokens=500,
    save=True
)

response = runner.run()
```

**Parameters:**
- `model` (LLMInterface): LLM instance to use
- `question_number` (str): Question identifier (e.g., "Q1b")
- `datatype` (str): Music format ("mei", "musicxml", "abc", "humdrum")
- `context` (bool): Whether to include contextual guides
- `exam_date` (str): Exam date identifier (empty for default)
- `base_dirs` (dict): Directory paths for data locations
- `temperature` (float): Sampling temperature
- `max_tokens` (int, optional): Maximum response tokens
- `save` (bool): Whether to save response to file

**Returns:**
- `str`: The LLM's response

### PromptBuilder

Constructs prompts from components.

```python
from llm_music_theory.prompts.prompt_builder import PromptBuilder

builder = PromptBuilder()
prompt_input = builder.build_prompt_input(
    question_text="Analyze this musical excerpt...",
    base_format_prompt="You are a music theory expert...",
    encoded_content="<mei>...</mei>",
    guides_content="Remember to consider key signatures...",
    temperature=0.7,
    max_tokens=500
)
```

**Methods:**

#### `build_prompt_input()`

**Parameters:**
- `question_text` (str): The question to ask
- `base_format_prompt` (str): Format-specific instructions
- `encoded_content` (str): Musical data in specified format
- `guides_content` (str): Additional context and guides
- `temperature` (float): Sampling temperature
- `max_tokens` (int, optional): Maximum response tokens

**Returns:**
- `PromptInput`: Complete prompt ready for LLM

## Model Implementations

### ChatGPT

OpenAI GPT model implementation.

```python
from llm_music_theory.models.chatgpt import ChatGPT

model = ChatGPT()
response = model.query(prompt_input)
```

**Configuration:**
- Requires `OPENAI_API_KEY` environment variable
- Default model: `gpt-4`
- Supports temperature and max_tokens parameters

### Claude

Anthropic Claude model implementation.

```python
from llm_music_theory.models.claude import Claude

model = Claude()
response = model.query(prompt_input)
```

**Configuration:**
- Requires `ANTHROPIC_API_KEY` environment variable
- Default model: `claude-3-sonnet-20240229`
- Supports temperature and max_tokens parameters

### Gemini

Google Gemini model implementation.

```python
from llm_music_theory.models.gemini import Gemini

model = Gemini()
response = model.query(prompt_input)
```

**Configuration:**
- Requires `GOOGLE_API_KEY` environment variable
- Default model: `gemini-pro`
- Supports temperature parameter

### DeepSeek

DeepSeek model implementation.

```python
from llm_music_theory.models.deepseek import DeepSeek

model = DeepSeek()
response = model.query(prompt_input)
```

**Configuration:**
- Requires `DEEPSEEK_API_KEY` environment variable
- Uses OpenAI-compatible API
- Supports temperature and max_tokens parameters

## Utility Functions

### Path Utilities

```python
from llm_music_theory.utils.path_utils import (
    find_project_root,
    list_questions,
    list_datatypes,
    find_encoded_file,
    find_question_file
)
```

#### `find_project_root(start_path=None)`

Find the project root directory by looking for `pyproject.toml`.

**Parameters:**
- `start_path` (Path, optional): Starting directory for search

**Returns:**
- `Path`: Project root directory

**Raises:**
- `FileNotFoundError`: If project root cannot be found

#### `list_questions(questions_dir)`

List all available question IDs.

**Parameters:**
- `questions_dir` (Path): Directory containing question files

**Returns:**
- `List[str]`: List of question IDs (e.g., ["Q1a", "Q1b", "Q2a"])

#### `list_datatypes(encoded_dir)`

List all available music data types.

**Parameters:**
- `encoded_dir` (Path): Directory containing encoded music files

**Returns:**
- `List[str]`: List of datatypes (e.g., ["mei", "musicxml", "abc", "humdrum"])

#### `find_encoded_file(question_number, datatype, encoded_dir, required=True)`

Locate encoded music file for a question and format.

**Parameters:**
- `question_number` (str): Question identifier
- `datatype` (str): Music format
- `encoded_dir` (Path): Directory containing encoded files
- `required` (bool): Whether to raise exception if not found

**Returns:**
- `Optional[Path]`: Path to the file, or None if not found and not required

**Raises:**
- `FileNotFoundError`: If required=True and file not found
- `ValueError`: If datatype is not supported

#### `find_question_file(question_number, context, questions_dir, required=True)`

Locate question prompt file.

**Parameters:**
- `question_number` (str): Question identifier
- `context` (bool): Whether to find contextual version
- `questions_dir` (Path): Directory containing question files
- `required` (bool): Whether to raise exception if not found

**Returns:**
- `Optional[Path]`: Path to the file, or None if not found and not required

### Model Dispatcher

```python
from llm_music_theory.core.dispatcher import get_llm, list_available_models

# Get model instance by name
model = get_llm("ChatGPT")

# List all available models
models = list_available_models()
```

#### `get_llm(model_name)`

Create LLM instance by name.

**Parameters:**
- `model_name` (str): Model identifier ("ChatGPT", "Claude", "Gemini", "DeepSeek")

**Returns:**
- `LLMInterface`: Model instance

**Raises:**
- `ValueError`: If model name is not recognized

#### `list_available_models()`

Get list of all available model names.

**Returns:**
- `List[str]`: List of model identifiers

## Configuration

### Settings

```python
from llm_music_theory.config.settings import API_KEYS

# Access API keys
openai_key = API_KEYS.get("openai")
anthropic_key = API_KEYS.get("anthropic")
```

### Environment Variables

The following environment variables are used:

- `OPENAI_API_KEY`: OpenAI API key for ChatGPT
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude
- `GOOGLE_API_KEY`: Google API key for Gemini
- `DEEPSEEK_API_KEY`: DeepSeek API key

## Error Handling

### Custom Exceptions

The package raises standard Python exceptions:

- `FileNotFoundError`: Missing required files
- `ValueError`: Invalid parameters or configurations
- `RuntimeError`: API communication errors

### Error Recovery

Most functions implement graceful error handling:
- Missing optional files are skipped
- API errors are logged and re-raised
- Invalid parameters trigger helpful error messages

## Usage Examples

### Basic Evaluation

```python
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.chatgpt import ChatGPT
from llm_music_theory.utils.path_utils import find_project_root

# Setup
model = ChatGPT()
root = find_project_root()
base_dirs = {
    "encoded": root / "data" / "LLM-RCM" / "encoded",
    "prompts": root / "data" / "LLM-RCM" / "prompts",
    "questions": root / "data" / "LLM-RCM" / "prompts",
    "guides": root / "data" / "LLM-RCM" / "guides",
    "outputs": root / "outputs"
}

# Run evaluation
runner = PromptRunner(
    model=model,
    question_number="Q1b",
    datatype="mei",
    context=True,
    exam_date="",
    base_dirs=base_dirs,
    temperature=0.7,
    save=True
)

response = runner.run()
print(f"Response: {response}")
```

### Batch Processing

```python
from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.utils.path_utils import list_questions, list_datatypes

# Get available data
questions = list_questions(base_dirs["questions"])
datatypes = list_datatypes(base_dirs["encoded"])
models = ["ChatGPT", "Claude", "DeepSeek"]

# Process all combinations
for model_name in models:
    model = get_llm(model_name)
    for question in questions:
        for datatype in datatypes:
            runner = PromptRunner(
                model=model,
                question_number=question,
                datatype=datatype,
                context=True,
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.0,
                save=True
            )
            try:
                response = runner.run()
                print(f"Completed {model_name}/{question}/{datatype}")
            except Exception as e:
                print(f"Failed {model_name}/{question}/{datatype}: {e}")
```
