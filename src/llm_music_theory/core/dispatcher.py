"""Model dispatcher with lazy imports.

Avoid importing third-party SDKs at module import time by importing model
wrappers only when requested. This keeps test collection lightweight and allows
running without optional dependencies installed.
"""

from llm_music_theory.models.base import LLMInterface

def get_llm(model_name: str) -> LLMInterface:
    """Return an instance of the LLM wrapper class for the given model string.

    Supported values: 'chatgpt', 'gemini', 'claude', 'deepseek'
    """
    name = str(model_name).lower()

    if name == "chatgpt":
        # OpenAI dependency kept mandatory to satisfy default tests
        from llm_music_theory.models.chatgpt import ChatGPTModel
        return ChatGPTModel()
    elif name == "gemini":
        try:
            from llm_music_theory.models.gemini import GeminiModel
        except ImportError as e:
            raise RuntimeError(
                "Google Gemini support not installed. Install extras with: 'poetry install --with google'"
            ) from e
        return GeminiModel()
    elif name == "claude":
        try:
            from llm_music_theory.models.claude import ClaudeModel
        except ImportError as e:
            raise RuntimeError(
                "Anthropic Claude support not installed. Install extras with: 'poetry install --with anthropic'"
            ) from e
        return ClaudeModel()
    elif name == "deepseek":
        try:
            from llm_music_theory.models.deepseek import DeepSeekModel
        except ImportError as e:
            raise RuntimeError(
                "DeepSeek support not installed. Install extras with: 'poetry install --with deepseek'"
            ) from e
        return DeepSeekModel()
    else:
        raise ValueError(f"Unknown model: {name}")
