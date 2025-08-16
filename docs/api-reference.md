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

Main execution engine for a single prompt evaluation.

```python
PromptRunner(
    model: LLMInterface,
    file_id: str | None = None,      # preferred identifier (legacy alias question_number)
    datatype: str = "mei",
    context: bool = False,
    dataset: str = "fux-counterpoint",
    base_dirs: dict[str, Path] | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    save: bool = False,
    question_number: str | None = None,  # legacy
    exam_date: str | None = None,        # legacy
)
response = PromptRunner(model=llm, file_id="Q1b", datatype="mei", context=True).run()
```

When `save=True`, a matching `<filename>.input.json` bundle is persisted with the full compiled user prompt + component lengths.

### PromptBuilder

Constructs a `PromptInput` from raw components. Supports an optional `ordering` to control how sections are presented (used by new datasets to prioritize task description + guides before format instructions & source encoding).

Key parameters: `system_prompt`, `format_specific_user_prompt`, `encoded_data`, `guides`, `question_prompt`, `ordering`, `section_headers`, `temperature`.

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
    list_datatypes,
    list_questions,
    find_encoded_file,
    find_question_file,
    get_output_path,
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

Return legacy per‑question prompt stems (legacy datasets only). New single‑prompt datasets may return empty list.

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
#### `get_output_path(outputs_dir, model_name, file_id, datatype, context, dataset=None, ext=".txt", question_number=None)`

Build the canonical output path. Pattern:

```
outputs/<Model>/<dataset>__<file_id>_<datatype>_<context|nocontext>.txt
```
Dataset prefix omitted if `dataset` is None for backward compatibility.

Returns `Path`.

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
    "encoded": root / "data" / "RCM6" / "encoded",      # legacy dataset (formerly LLM-RCM)
    "prompts": root / "data" / "RCM6" / "prompts",
    "questions": root / "data" / "RCM6" / "prompts",
    "guides": root / "data" / "RCM6" / "guides",
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
models = ["chatgpt", "claude", "deepseek"]

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
