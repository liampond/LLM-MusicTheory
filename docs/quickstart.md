# Quick Start Guide

Get up and running with LLM-MusicTheory in minutes.

## Your First Analysis

Once you've completed the [installation](installation.md), let's run a music theory analysis:

### Single Question Analysis

```bash
# Analyze a specific question with context
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --encoded_type musicxml \
  --model gemini-2.0-flash-exp \
  --context

# Without musical context
python -m llm_music_theory.cli.run_single \
  --question Q1b \
  --model gpt-4o \
  --no-context
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
- `Q1b`: Counterpoint analysis question

## Supported Models

- **Google Gemini**: `gemini-2.0-flash-exp`, `gemini-1.5-pro`
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `o1-preview`, `o1-mini`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`

## Supported Music Formats

- **MusicXML** (`.musicxml`): Industry standard format
- **MEI** (`.mei`): Music Encoding Initiative format
- **ABC Notation** (`.abc`): Text-based music notation
- **Humdrum** (`.krn`): Academic analysis format

## Example Workflows

### Compare Models on Same Question
```bash
# Test multiple models on the same question
for model in "gemini-2.0-flash-exp" "gpt-4o" "claude-3-5-sonnet-20241022"; do
  python -m llm_music_theory.cli.run_single \
    --question Q1b \
    --encoded_type musicxml \
    --model "$model" \
    --context
done
```

### Test Different Format Encodings
```bash
# Compare how models handle different music formats
for format in "musicxml" "mei" "abc" "humdrum"; do
  python -m llm_music_theory.cli.run_single \
    --question Q1b \
    --encoded_type "$format" \
    --model gemini-2.0-flash-exp \
    --context
done
```

### Batch Processing
```bash
# Run multiple questions (when available)
python -m llm_music_theory.cli.run_batch \
  --questions Q1b \
  --encoded_type musicxml \
  --model gemini-2.0-flash-exp \
  --context
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
