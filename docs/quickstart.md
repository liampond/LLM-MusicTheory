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

# Analyze RCM6 questions with context (may have path issues)
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

## What Just Happened?

1. **Question Loading**: The system loaded question `Q1b` from the questions database
2. **Prompt Building**: Combined the question with musical context (if requested)
3. **LLM Analysis**: Sent the prompt to your chosen model
4. **Result Storage**: Saved the analysis with proper file extension

## Available Questions

Current questions in the database:
- **Fux-Counterpoint dataset**: `Fux_CantusFirmus` (counterpoint composition)
- **RCM6 dataset**: `Q1b` (analysis question - limited path support)

## Supported Models

Available model choices (use provider aliases for simplicity):
- **Google Gemini**: `gemini`
- **OpenAI ChatGPT**: `chatgpt`  
- **Anthropic Claude**: `claude`

*Note: Specific model versions (like `gpt-4o`) can be specified with `--model-name` parameter*

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
# Use the batch runner for multiple files (when available)
poetry run python -m llm_music_theory.cli.run_batch \
  --files Fux_CantusFirmus \
  --datatype musicxml \
  --model gemini
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
