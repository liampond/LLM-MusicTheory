# LLM-Music2. **Install Poetry (if you don't have it)**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   Or see [Poetry's official installation guide](https://python-poetry.org/docs/main/#installing-with-the-official-installer).
   
   **Alternative installation via pipx (recommended):**
   ```bash
   python3 -m pip install --user pipx
   pipx install poetry
   ```
   
   **Add Poetry to your PATH:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
   You may need to add this line to your `~/.bashrc` or `~/.zshrc` file and restart your terminal.y

A modular toolkit for designing and testing music theory prompts for large language models (LLMs). Write modular prompt components, then use this tool to flexibly combine them and automate querying ChatGPT, Claude, Gemini, and DeepSeek. Built for experimentation and evaluation on official Royal Conservatory of Music (RCM) exam questions.

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
   Or see [Poetry’s official installation guide](https://python-poetry.org/docs/main/#installing-with-the-official-installer).

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
   This project requires Python 3.11 or higher. You can check your version with:
   ```bash
   python --version
   ```

7. **Troubleshooting**
   - If you get errors about missing dependencies, try running `poetry lock --no-update` then `poetry install` again.
   - If you have issues with conflicting Python versions, ensure your virtual environment uses the correct Python version:
     ```bash
     poetry env use python3.11  # or your preferred version >=3.11
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

- **OpenAI ChatGPT:** [Create OpenAI API Key](https://platform.openai.com/api-keys)
- **Anthropic Claude:** [Create Anthropic API Key](https://console.anthropic.com/account/keys)
- **DeepSeek:** [Create DeepSeek API Key](https://platform.deepseek.com/api_keys)
- **Google Gemini:** [Create Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)


> **Note:** You will need to set up billing with each provider. You will be charged for API usage according to their pricing. Be mindful of your usage to avoid unexpected charges.

## Settings and Configuration

Settings and configurations can be changed in `src/llm_music_theory/config/settings.py`. Currently, the only settings that you can change are the models. Each has a different price, performance, and niche. You can find information about the models, pricing, and their string identifiers here:

- **[OpenAI ChatGPT](https://platform.openai.com/docs/pricing):**
- **[Anthropic Claude](https://docs.anthropic.com/en/docs/about-claude/models/overview):**
- **[DeepSeek](https://api-docs.deepseek.com/quick_start/pricing):**
- **[Google Gemini](https://ai.google.dev/gemini-api/docs/models):**

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
- `--data-dir`: Path to your data directory (default: `./data/LLM-RCM`)
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

## Testing

This project includes comprehensive tests that validate the prompt generation process **without making actual API calls** to avoid costs. The tests use mock APIs to verify that prompts are compiled correctly and would be sent to the LLMs properly.

### Running Tests

**Quick test run:**
```bash
python run_tests.py
```

**Run specific test categories:**
```bash
python run_tests.py models        # Test model interfaces
python run_tests.py prompt        # Test prompt building
python run_tests.py runner        # Test prompt runner
python run_tests.py integration   # Test CLI integration
python run_tests.py comprehensive # Test with real data
python run_tests.py utils         # Test utility functions
python run_tests.py fast          # Quick tests only
```

**Using Poetry directly:**
```bash
poetry run pytest tests/ -v                    # Run all tests
poetry run pytest tests/test_models.py -v      # Test specific file
poetry run pytest tests/ -k "test_prompt"      # Test specific pattern
```

### What the Tests Validate

- **Model Interface Testing**: Verifies all LLM models (ChatGPT, Claude, Gemini, DeepSeek) receive correctly formatted prompts
- **Prompt Building**: Validates that prompt components are assembled correctly with proper structure
- **Data Loading**: Tests loading of encoded music files, questions, guides, and system prompts
- **CLI Integration**: Verifies command-line interface works without API calls
- **Real Data Testing**: Uses actual project data to validate end-to-end prompt compilation
- **Parameter Passing**: Ensures temperature, max_tokens, and other settings are passed correctly
- **Error Handling**: Tests proper handling of missing files and invalid inputs

### Test Environment

Tests use mock API keys and never make actual API calls:
- Mock environment variables are set automatically
- Real prompt compilation is tested but API calls are intercepted
- All tests run safely without incurring API costs
- Tests validate prompt correctness before any expensive operations

### Continuous Integration

GitHub Actions automatically run tests on:
- Push to main/develop branches
- Pull request creation
- Multiple Python versions (3.11, 3.12, 3.13)

The CI pipeline ensures all prompt generation is working correctly before merging changes.
