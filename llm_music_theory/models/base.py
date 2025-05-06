# models/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptInput:
    """
    Unified structure for sending prompts to any LLM.
    """
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    model_name: Optional[str] = None


class LLMInterface(ABC):
    """
    Abstract base class for all LLM wrappers.
    Subclasses must implement the `query` method
    using their respective API format.
    """

    @abstractmethod
    def query(self, input: PromptInput) -> str:
        """
        Send a prompt to the LLM and return the response as plain text.
        
        Parameters:
            input (PromptInput): Contains system/user prompt and parameters.
        
        Returns:
            str: The LLM's generated response.
        """
        pass
