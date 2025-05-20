# LLM-MusicTheory

A modular toolkit for designing and testing music theory prompts for large language models (LLMs). Write modular prompt components, then use this tool to flexibly combine them and automate querying APIs like ChatGPT, Claude, Gemini, and DeepSeek. Built for experimentation and evaluation on official Royal Conservatory of Music (RCM) exam questions.

## Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/liampond/LLM-MusicTheory.git
   cd LLM-MusicTheory
   ```

2. **Install Poetry (if you don’t have it)**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   Or see [Poetry’s official installation guide](https://python-poetry.org/docs/#installation).

3. **Install dependencies**
   ```bash
   poetry install
   ```
   If you get a `poetry: command not found` error, make sure Poetry is in your PATH. You may need to restart your terminal or run:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

5. **Activate the Poetry environment**
   ```bash
   poetry shell
   ```

6. **Check your Python version**
   This project requires Python 3.9 or higher. You can check your version with:
   ```bash
   python --version
   ```

7. **Troubleshooting**
   - If you get errors about missing dependencies, try running `poetry lock --no-update` then `poetry install` again.
   - If you have issues with conflicting Python versions, ensure your virtual environment uses the correct Python version:
     ```bash
     poetry env use python3.13  # or your preferred version >=3.9
     ```

## Environment Variables

You must provide your own API keys to use the LLM providers. This is how they know who to charge for API usage. **Never share your API keys or commit them to version control.** (The `.env` file is already in `.gitignore`, but always double-check before sharing this file.)

### 1. Create a `.env` file in your project root

You can do this with the following command:
```bash
echo "OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
DEEPSEEK_API_KEY=your_key" > .env
```
Then, open `.env` in your editor and replace `your_key` with your actual keys.

### 2. Get your API keys

- **OpenAI ChatGPT:** [Create OpenAI ChatGPT API Key](https://platform.openai.com/api-keys)
- **Anthropic Claude:** [Create Anthropic Claude API Key](https://console.anthropic.com/account/keys)
- **DeepSeek:** [Create DeepSeek API Key](https://platform.deepseek.com/api_keys)
- **Google Gemini:** [Create Google Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)


> **Note:** You will need to set up billing with each provider. You will be charged for API usage according to their pricing. Be mindful of your usage to avoid unexpected charges.

## Run a Single Prompt

You can run a single music theory prompt against any supported LLM using the `run_single.py` script. This script combines your modular prompt components, sends the query to the selected API, and prints the model’s response.

**Example command:**
```bash
poetry run python src/llm_music_theory/cli/run_single.py --model gemini --question Q1b --datatype mei --context
```

### Common Flags

- `--model` (required): Which LLM to use. Options: `chatgpt`, `claude`, `gemini`, `deepseek`
- `--question` (required): The question ID (e.g., `Q1a`, `Q1b`)
- `--datatype` (required): The encoding format. Options: `mei`, `musicxml`, `abc`, `humdrum`
- `--context`: Include contextual guides (add this flag for context, omit for no context)
- `--examdate`: Specify the exam version/folder (default: `August2024`)
- `--temperature`: Sampling [temperature](https://learnprompting.org/docs/intermediate/configuration_hyperparameters?srsltid=AfmBOoo66sF4m6TbQQHn8HGvoJvoLwaoUITh6xeb2jbSHLC3LzBOcI0Z) (creativity) for the model (default: `0.0`)
- `--max-tokens`: Maximum tokens for the response (optional)
- `--save`: Save the model response to the outputs directory
- `--data-dir`: Path to your data directory (default: `./data`)
- `--outputs-dir`: Path to your outputs directory (default: `./outputs`)

### Listing Available Resources

You can also list available questions, datatypes, or guides:
- `--list-questions`
- `--list-datatypes`
- `--list-guides`

**Example:**
```bash
poetry run python src/llm_music_theory/cli/run_single.py --list-questions
```
