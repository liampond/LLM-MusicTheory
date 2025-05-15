import os
from typing import Optional
from anthropic import Anthropic
from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.config.settings import DEFAULT_MODELS


class ClaudeModel(LLMInterface):
    """
    ClaudeModel handles interaction with Anthropic's Claude API (v3).
    It uses environment-based API keys and supports optional model overrides.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set in the environment.")
        self.model_name = model_name or DEFAULT_MODELS["anthropic"]
        self.client = Anthropic(api_key=self.api_key)

    def query(self, input: PromptInput) -> str:
        """
        Queries Claude API using a structured system + user prompt.

        Parameters:
            input (PromptInput): Standardized prompt input, including:
                - system_prompt (str)
                - user_prompt (str)
                - temperature (float)
                - max_tokens (Optional[int])
                - model_name (Optional[str])

        Returns:
            str: LLM-generated response.
        """
        model = input.model_name or self.model_name
        max_tokens = input.max_tokens if hasattr(input, "max_tokens") and input.max_tokens else 1024

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=input.temperature,
            system=input.system_prompt,
            messages=[{"role": "user", "content": input.user_prompt}],
        )
        return response.content[0].text.strip()
