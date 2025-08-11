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

    def __post_init__(self):
        # Validate required string fields
        if not isinstance(self.system_prompt, str) or not isinstance(self.user_prompt, str):
            raise TypeError("system_prompt and user_prompt must be strings")

        # Validate temperature
        if not isinstance(self.temperature, (int, float)):
            raise TypeError("temperature must be a number between 0.0 and 1.0")
        if not (0.0 <= float(self.temperature) <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")

        # Validate max_tokens if provided
        if self.max_tokens is not None:
            if not isinstance(self.max_tokens, int) or self.max_tokens <= 0:
                raise ValueError("max_tokens must be a positive integer if provided")


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
