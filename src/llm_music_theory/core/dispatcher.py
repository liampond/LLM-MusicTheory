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
        from llm_music_theory.models.chatgpt import ChatGPTModel
        return ChatGPTModel()
    elif name == "gemini":
        from llm_music_theory.models.gemini import GeminiModel
        return GeminiModel()
    elif name == "claude":
        from llm_music_theory.models.claude import ClaudeModel
        return ClaudeModel()
    elif name == "deepseek":
        from llm_music_theory.models.deepseek import DeepSeekModel
        return DeepSeekModel()
    else:
        raise ValueError(f"Unknown model: {name}")
