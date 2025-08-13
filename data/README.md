# Data Directory

This directory contains datasets and resources for the LLM-MusicTheory framework.

## Structure

### RCM6/ (formerly LLM-RCM)
Legacy exam-style dataset retained for backwards-compatible tests. Prefer `fux-counterpoint` for new work.

  - **base/** - Base prompt templates including system prompts
  - **questions/** - Specific examination questions with context variations

## Adding New Datasets

To add new datasets:

1. Create a new subdirectory under `data/`
2. Follow the same structure as `RCM6/` if you need legacy compatibility
3. Update the framework's configuration to recognize the new dataset
4. Add appropriate documentation

## Usage

The framework automatically discovers datasets in this directory. Specify the dataset name when running commands:

```bash
poetry run python src/llm_music_theory/cli/run_single.py --data-dir ./data/RCM6 --question Q1b --datatype mei
```
