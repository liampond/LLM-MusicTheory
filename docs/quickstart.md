# Quick Start Guide

Get up and running with LLM-MusicTheory in minutes.

## Your First Analysis

Once you've completed the [installation](installation.md), let's run a music theory analysis:

### Single Question Analysis

```bash
# Analyze counterpoint composition (default dataset)
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --datatype musicxml \
  --model gemini

# Analyze RCM6 questions with context (experimental - may have path issues)
poetry run python -m llm_music_theory.cli.run_single \
  --file Q1b \
  --datatype musicxml \
  --model gemini \
  --context \
  --dataset RCM6

# Simple text-only counterpoint analysis
poetry run python -m llm_music_theory.cli.run_single \
  --file Fux_CantusFirmus \
  --model chatgpt
```

### Understanding the Output

Results are saved in the `output/` directory with this structure:
```
output/
├── context/
│   ├── gemini-2.0-flash-exp/
│   │   └── Q1b.musicxml
│   └── gpt-4o/
│       └── Q1b.musicxml
└── no_context/
    └── gpt-4o/
        └── Q1b.txt
```

Each analysis also generates a `.prompt.txt` file containing the full prompt sent to the model, along with metadata including:
- **Timestamp**: Analysis time in Montreal timezone (EDT/EST)
- **API Duration**: How long the API call took (for performance monitoring)
- **Model Parameters**: Temperature, max tokens, and other settings
- **File Information**: Dataset, context type, and input format

**Example metadata:**
```
=== MODEL PARAMETERS ===
Timestamp: 2025-09-08 19:39:50 EDT
File: Fux_CantusFirmus_A
Dataset: fux-counterpoint
Datatype: musicxml
Context: nocontext
Model: GeminiModel
Temperature: 0.0
Max Tokens: None
API Duration: 100.78 seconds
Save Path: /path/to/output.musicxml
```

## What Just Happened?

1. **Question Loading**: The system loaded question `Q1b` from the questions database
2. **Prompt Building**: Combined the question with musical context (if requested)
3. **LLM Analysis**: Sent the prompt to your chosen model
4. **Result Storage**: Saved the analysis with proper file extension

## Available Questions

Current questions in the database:
- **Fux-Counterpoint dataset**: `Fux_CantusFirmus` (counterpoint composition)
- **RCM6 dataset**: `Q1b` (analysis question - experimental path support)

## Supported Models

### Provider Names (Simple)
For convenience, you can use provider aliases:
- **Google Gemini**: `gemini`
- **OpenAI ChatGPT**: `chatgpt`  
- **Anthropic Claude**: `claude`

### Specific Model Names (Advanced)
Both CLI tools support **model auto-detection** - you can specify exact model names directly:
- **OpenAI Models**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Anthropic Models**: `claude-3-sonnet`, `claude-3-haiku`, `claude-3-opus`
- **Google Models**: `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`

**Examples:**
```bash
# Using provider name
poetry run run-single --model gemini --file Q1b --datatype musicxml

# Using specific model with auto-detection
poetry run run-single --model gemini-2.5-pro --file Q1b --datatype musicxml

# Both approaches work identically - the system auto-detects the provider
```

## Supported Music Formats

- **MusicXML** (`.musicxml`): Industry standard format
- **MEI** (`.mei`): Music Encoding Initiative format
- **ABC Notation** (`.abc`): Text-based music notation
- **Humdrum** (`.krn`): Academic analysis format

## Example Workflows

### Compare Models on Same Question
```bash
# Test multiple models on counterpoint composition
for model in "gemini" "chatgpt" "claude"; do
  poetry run python -m llm_music_theory.cli.run_single \
    --file Fux_CantusFirmus \
    --datatype musicxml \
    --model "$model"
done
```

### Test Different Format Encodings
```bash
# Compare how models handle different music formats
for format in "musicxml" "mei" "abc" "humdrum"; do
  poetry run python -m llm_music_theory.cli.run_single \
    --file Fux_CantusFirmus \
    --datatype "$format" \
    --model gemini
done
```

### Batch Processing
```bash
# Use provider names (traditional approach)
poetry run python -m llm_music_theory.cli.run_batch \
  --models gemini,chatgpt,claude \
  --files Fux_CantusFirmus_A,Fux_CantusFirmus_C \
  --datatypes musicxml

# Use specific model names with auto-detection (new feature)
poetry run python -m llm_music_theory.cli.run_batch \
  --models gemini-2.5-pro,gpt-4o,claude-3-sonnet \
  --files Fux_CantusFirmus_A,Fux_CantusFirmus_C \
  --datatypes musicxml

# Mix provider names and specific models
poetry run python -m llm_music_theory.cli.run_batch \
  --models gemini,gpt-4o,claude-3-sonnet \
  --files Fux_CantusFirmus_A \
  --datatypes musicxml
```

## Next Steps

Now that you've run your first analysis:

1. **Explore Results**: Open the output files to see how different models analyze music
2. **Try Different Formats**: Test how format affects model understanding
3. **Compare Models**: See which models work best for your use case
4. **Customize Prompts**: Learn about prompt customization in the configuration guide
5. **Add Questions**: Learn to [add your own questions](adding-questions.md)

## Need Help?

- [Configuration](configuration.md) - Detailed usage information
- [Examples](examples.md) - Real-world usage examples
- [API Reference](api-reference.md) - Programming interface
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
