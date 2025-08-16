# User Guide

## Overview

This guide provides detailed instructions for using the LLM-MusicTheory package to evaluate Large Language Models on music theory tasks.

## Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- API keys for the LLM services you want to test

## Installation

### 1. Clone and Install

```bash
git clone https://github.com/liampond/LLM-MusicTheory.git
cd LLM-MusicTheory
poetry install
```

### 2. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

## Basic Usage

### Single Question Evaluation

Test a specific question with one model:

```bash
poetry run python -m llm_music_theory.cli.run_single \
    --file-id Q1b \
    --datatype mei \
    --model chatgpt \
    --context \
    --temperature 0.0
```

### Batch Evaluation

Evaluate multiple questions across different models and formats:

```bash
poetry run python -m llm_music_theory.cli.run_batch \
    --questions Q1a Q1b \
    --datatypes mei musicxml \
    --models chatgpt claude \
    --context \
    --temperature 0.7
```

## Command Line Options

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file-id` / `--question` | File/question ID (legacy alias supported) | Required |
| `--datatype` | Music format (mei, musicxml, abc, humdrum) | Required |
| `--model` | LLM model name | Required |
| `--context` | Include context in prompts | False |
| `--no-context` | Exclude context from prompts | True |
| `--temperature` | Sampling temperature (0.0-2.0) | 0.0 |
| `--max-tokens` | Maximum response tokens | None |
| `--save` | Save responses to files | True |
| `--output-dir` | Output directory path | `./outputs` |

### List Available Options

```bash
# List available questions (legacy datasets)
poetry run python -m llm_music_theory.cli.run_single --list-questions

# List available data types
poetry run python -m llm_music_theory.cli.run_single --list-datatypes

# List available models
poetry run python -m llm_music_theory.cli.run_single --list-models
```

## Output Files

Results are saved in the `outputs/` directory with the following structure:

```
outputs/
├── ChatGPT/
│   ├── fux-counterpoint__Q1b_mei_context.txt
│   └── fux-counterpoint__Q1b_mei_context.input.json
├── Claude/
│   └── fux-counterpoint__Q1b_musicxml_context.txt
└── DeepSeek/
    └── Q2a_abc_nocontext.txt
```

## Supported Models

| Model | Provider | Configuration |
|-------|----------|---------------|
| chatgpt | OpenAI | Requires `OPENAI_API_KEY` |
| claude | Anthropic | Requires `ANTHROPIC_API_KEY` |
| gemini | Google | Requires `GOOGLE_API_KEY` |
| deepseek | DeepSeek | Requires `DEEPSEEK_API_KEY` |

## Supported Music Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| MEI | `.mei` | Music Encoding Initiative XML |
| MusicXML | `.musicxml` | Standard music notation format |
| ABC | `.abc` | ASCII-based music notation |
| Humdrum | `.krn` | Kern format for music analysis |

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're using `poetry run` or have activated the virtual environment
2. **API Key Errors**: Check that your `.env` file contains valid API keys
3. **File Not Found**: Verify question and datatype combinations exist in the data directory

### Debug Mode

Run with verbose output for debugging:

```bash
poetry run python -m llm_music_theory.cli.run_single \
    --file-id Q1b \
    --datatype mei \
    --model chatgpt \
    --verbose
```

## Advanced Usage

### Custom Temperature Settings

Different models may respond better to different temperature settings:

```bash
# Conservative (deterministic)
--temperature 0.0

# Balanced
--temperature 0.7

# Creative
--temperature 1.2
```

### Batch Processing with Different Parameters

```bash
poetry run python -m llm_music_theory.cli.run_batch \
    --questions Q1a Q1b \
    --datatypes mei musicxml \
    --models chatgpt claude deepseek \
    --context \
    --temperature 0.0 0.5 0.9
```

This will test all combinations of questions, datatypes, models, context settings, and temperatures.
