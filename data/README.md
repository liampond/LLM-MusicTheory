# Data Directory

This directory contains datasets and resources for the LLM-MusicTheory framework.

## Structure

### LLM-RCM/
Legacy dataset containing Royal Conservatory of Music (RCM) examination materials:

- **encoded/** - Sample music files in various formats (ABC, Humdrum, MEI, MusicXML, MuseScore)
- **prompts/** - Prompt templates and question sets for RCM examinations
  - **base/** - Base prompt templates including system prompts
  - **questions/** - Specific examination questions with context variations
- **guides/** - Additional guidance materials for prompt generation

## Adding New Datasets

To add new datasets:

1. Create a new subdirectory under `data/`
2. Follow the same structure as `LLM-RCM/` for consistency
3. Update the framework's configuration to recognize the new dataset
4. Add appropriate documentation

## Usage

The framework automatically discovers datasets in this directory. Specify the dataset name when running commands:

```bash
poetry run python src/llm_music_theory/cli/run_single.py --data-dir ./data/LLM-RCM --question Q1b --datatype mei
```
