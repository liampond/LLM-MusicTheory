# core/dispatcher.py

from models.chatgpt import ChatGPTModel
from models.gemini import GeminiModel
from models.claude import ClaudeModel
from models.deepseek import DeepSeekModel
from models.base import LLMInterface

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
