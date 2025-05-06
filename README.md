# LLM-MusicTheory
Using prompt engineering to teach various LLMs how to do music theory. Tested using official Royal Conservatory of Music (RCM) examination questions.

This is a modular, OOP-based framework for querying LLMs (ChatGPT, Claude, Gemini, DeepSeek) to solve music theory problems using in-context learning and chain-of-thought prompting.

## Setup
```bash
git clone <your-repo-url>
cd llm-music-theory
poetry install
```

## Environment Variables
Store your API keys in `.env` (this file is git-ignored):
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

## Run a Single Prompt
```bash
poetry run python llm_music_theory/cli/run_single.py --model chatgpt --question Q4b --format mei --context True
```

## Run Batch
```bash
poetry run python llm_music_theory/cli/run_batch.py --model claude
```

## Directory Structure
```
llm_music_theory/
  cli/             # Command line interfaces
    run_single.py
    run_batch.py

  core/            # Execution logic
    runner.py
    dispatcher.py

  models/          # Each LLM API interface
    base.py
    chatgpt.py
    claude.py
    gemini.py
    deepseek.py

  encodings/       # MEI, MusicXML, Humdrum, ABC
    base.py
    mei.py
    musicxml.py
    humdrum.py
    abc.py

  prompts/         # System prompt + builder
    prompt_builder.py
    guide_loader.py
    system_prompt.txt

  config/          # YAML configs
    api_keys.yaml
    settings.yaml

  questions/       # Context/no-context files
    context/
    no_context/

  utils/           # Helper functions
    logger.py
    path_utils.py

outputs/            # Model outputs
