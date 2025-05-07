# src/llm_music_theory/core/dispatcher.py

from llm_music_theory.models.chatgpt  import ChatGPTModel
from llm_music_theory.models.claude   import ClaudeModel
from llm_music_theory.models.gemini   import GeminiModel
from llm_music_theory.models.deepseek import DeepSeekModel
from llm_music_theory.models.base     import LLMInterface

def get_llm(model_name: str) -> LLMInterface:
    """
    Return an instance of the LLM wrapper class for the given model string.
    Example: 'chatgpt', 'gemini', 'claude', 'deepseek'
    """
    model_name = model_name.lower()

    if model_name == "chatgpt":
        return ChatGPTModel()
    elif model_name == "gemini":
        return GeminiModel()
    elif model_name == "claude":
        return ClaudeModel()
    elif model_name == "deepseek":
        return DeepSeekModel()
    else:
        raise ValueError(f"Unknown model: {model_name}")
