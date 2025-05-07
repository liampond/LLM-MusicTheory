# models/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptInput:
    """
    Encapsulates all parameters for a single LLM request.
    """
    system_prompt: str            # The system‐level instructions
    user_prompt: str              # The body: format intro + encoded data + guides + question
    temperature: float = 0.0      # Sampling temperature
    model_name: Optional[str] = None   # Override the default model if provided
    max_tokens: Optional[int] = None   # (Optional) token limit for the response


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
