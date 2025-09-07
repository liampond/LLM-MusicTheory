# Installation Guide

This guide walks you through setting up LLM-MusicTheory on your system.

## Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- API keys for one or more supported LLM providers

## Quick Install

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/LLM-MusicTheory.git
   cd LLM-MusicTheory
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate the environment**
   ```bash
   poetry shell
   ```

## API Key Configuration

You'll need API keys from at least one LLM provider:

### Google Gemini
- Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Set environment variable: `export GOOGLE_API_KEY="your-key"`

### OpenAI
- Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- Set environment variable: `export OPENAI_API_KEY="your-key"`

### Anthropic Claude
- Get API key from [Anthropic Console](https://console.anthropic.com/)
- Set environment variable: `export ANTHROPIC_API_KEY="your-key"`

### DeepSeek
- Get API key from [DeepSeek Platform](https://platform.deepseek.com/)
- Set environment variable: `export DEEPSEEK_API_KEY="your-key"`

## Environment Variables

Create a `.env` file in the project root:

```env
# Required: At least one API key
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Optional: Logging configuration
LOG_LEVEL=INFO
```

## Verification

Test your installation:

```bash
# Run a simple test
python -m pytest tests/test_models.py -v

# Test CLI interface
python -m llm_music_theory.cli.run_single --help
```

## Troubleshooting

### Common Issues

**Poetry not found**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

**Python version mismatch**
```bash
# Check Python version
python --version

# Use pyenv to manage Python versions if needed
pyenv install 3.11
pyenv local 3.11
```

**API key errors**
- Double-check your API keys are correctly set
- Verify the keys have necessary permissions
- Check for any trailing spaces in environment variables

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first music theory analysis
- [Configuration](configuration.md) - Customize the system for your needs
- [Examples](examples.md) - See practical usage examples
