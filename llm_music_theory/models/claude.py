# llm_music_theory/models/claude.py

import os
import anthropic
from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.config.settings import DEFAULT_MODELS

class ClaudeModel(LLMInterface):
    def __init__(self, model_name=None):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set.")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_name = model_name or DEFAULT_MODELS["anthropic"]

    def query(self, input: PromptInput) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            temperature=input.temperature,
            system=input.system_prompt,
            messages=[{"role": "user", "content": input.user_prompt}]
        )
        return response.content[0].text.strip()
