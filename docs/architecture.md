# Architecture

## System Overview

The LLM-MusicTheory package is a modular evaluation framework for testing Large Language Models on music theory tasks. The architecture emphasizes small focused modules, backward compatibility for legacy datasets, and explicit prompt assembly ordering for new datasets.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │   Core Layer    │    │  Model Layer    │
│                 │    │                 │    │                 │
│ • run_single    │────│ • PromptRunner  │────│ • ChatGPT       │
│ • run_batch     │    │ • Dispatcher    │    │ • Claude        │
└─────────────────┘    └─────────────────┘    │ • Gemini        │
                                              │ • DeepSeek      │
                                              └─────────────────┘
          │                        │                    │
          │                        │                    │
          ▼                        ▼                    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Utils Layer    │    │ Prompts Layer   │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • path_utils    │    │ • PromptBuilder │    │ • Legacy Data   │
│ • logger        │    │ • Base Prompts  │    │ • Questions     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. CLI Layer (`src/llm_music_theory/cli/`)

**Purpose**: Command-line interface for user interaction

- **`run_single.py`**: Single question evaluation
- **`run_batch.py`**: Batch evaluation across multiple parameters

**Key Responsibilities**:
- Argument parsing and validation
- Environment setup
- User feedback and progress reporting

### 2. Core Layer (`src/llm_music_theory/core/`)

**Purpose**: Business logic and orchestration

- **`runner.py`**: Main execution engine (`PromptRunner` class) – now prefers `file_id` with legacy `question_number` alias
- **`dispatcher.py`**: Model selection and instantiation

**Key Responsibilities**:
- Prompt compilation and assembly
- Model interaction coordination
- Result handling and storage

### 3. Model Layer (`src/llm_music_theory/models/`)

**Purpose**: LLM-specific implementations

- **`base.py`**: Abstract interface (`LLMInterface`)
- **`chatgpt.py`**: OpenAI GPT implementation
- **`claude.py`**: Anthropic Claude implementation
- **`gemini.py`**: Google Gemini implementation
- **`deepseek.py`**: DeepSeek implementation

**Key Responsibilities**:
- API communication
- Response parsing and error handling
- Model-specific parameter handling

### 4. Prompts Layer (`src/llm_music_theory/prompts/`)

**Purpose**: Prompt construction and management

- **`prompt_builder.py`**: Deterministic prompt assembly (supports custom ordering for new datasets)
- **`base/`**: Format-specific base prompts

**Key Responsibilities**:
- Template processing
- Context injection
- Prompt validation

### 5. Utils Layer (`src/llm_music_theory/utils/`)

**Purpose**: Supporting utilities

- **`path_utils.py`**: File system operations
- **`logger.py`**: Logging configuration

**Key Responsibilities**:
- Data discovery and loading
- Error handling
- System utilities

### 6. Data Layer (`data/RCM6/` – legacy, formerly LLM-RCM)

**Purpose**: Static evaluation data

- **`encoded/`**: Music files in various formats
- **`prompts/`**: Base prompt templates
- **`questions/`**: Question specifications
- **`guides/`**: Context information

## Data Flow

### 1. Request Flow

```
CLI Input → Validation → Runner → PromptBuilder → Model → Response → Persistence
    ↓           ↓           ↓        ↓         ↓        ↓
Arguments   Parameters   Prompt   API Call  Result   File
```

### 2. Prompt Assembly Flow

```
Question/File Id + Format + Context Guides → PromptBuilder (ordered sections) → Final PromptInput
    ↓         ↓        ↓            ↓             ↓
 Q1b.txt + mei + guides → Template Processing → LLM Input
```

## Design Patterns

### 1. Strategy Pattern (Models)

Each LLM implements the `LLMInterface` abstract base class, allowing runtime model selection:

```python
# Abstract interface
class LLMInterface(ABC):
    @abstractmethod
    def query(self, input: PromptInput) -> str:
        pass

# Concrete implementations
class ChatGPT(LLMInterface): ...
class Claude(LLMInterface): ...
```

### 2. Builder Pattern (Prompts)

The `PromptBuilder` constructs complex prompts from multiple components:

```python
prompt_input = PromptBuilder(
    system_prompt=system_txt,
    format_specific_user_prompt=base_format_txt,
    encoded_data=mei_source,
    guides=[guide1, guide2],
    question_prompt=task_text,
    ordering=["question_prompt","guides","format_prompt","encoded_data"],  # new dataset order
    temperature=0.7,
).build()
```

### 3. Factory Pattern (Dispatcher)

The dispatcher creates model instances based on string identifiers:

```python
model = get_llm("chatgpt")  # Case-insensitive / alias tolerant
```

## Configuration Management

### Environment Variables

- **API Keys**: Stored in `.env` file
- **Model Settings**: Configurable per model
- **Path Configuration**: Automatic project root detection

### Settings Hierarchy

1. CLI arguments (highest)
2. Environment variables / settings module
3. Defaults baked into constructors (lowest)

## Error Handling Strategy

### 1. Graceful Degradation

-- Missing optional files: skip gracefully
-- Missing required files: raise early & clearly
-- API failures: surfaced by model layer (retry logic may be added later)

### 2. Error Categories

- **Configuration Errors**: Missing API keys, invalid paths
- **Data Errors**: Missing files, malformed content
- **API Errors**: Rate limits, network issues, invalid responses
- **Validation Errors**: Invalid parameters, unsupported combinations

### 3. Recovery Mechanisms

- **Automatic retry**: For transient network issues
- **Fallback options**: Alternative data sources
- **Partial results**: Save successful evaluations

## Testing Architecture

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full workflow testing
4. **Mock Tests**: API call simulation

### Test Data Strategy

-- **Synthetic Data**: Generated fixtures (temporary project structures)
-- **Legacy Sample Data**: Minimal `RCM6` subset for compatibility tests
-- **Mock Responses**: Model stubs + monkeypatched SDKs

## Scalability Considerations

### Current Limitations

-- Sequential processing (no concurrency)
-- Full encoded file loaded into memory
-- Synchronous file I/O

### Future Improvements

-- Optional async/parallel request orchestration
-- Streaming for large musical sources
-- On-disk or in-memory prompt+response caching
-- Pluggable persistence (database / vector store)

## Extension Points

### Adding New Models

1. Implement `LLMInterface`
2. Add to `dispatcher.py`
3. Update configuration
4. Add tests

### Adding New Formats

1. Add format-specific base prompt
2. Update data discovery logic
3. Add validation rules
4. Update documentation

### Adding New Features

- **Custom Metrics**: Response evaluation
- **Batch Analysis**: Cross-model comparison
- **Visualization**: Result charting
- **Export**: Multiple output formats
