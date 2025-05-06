# llm_music_theory/models/deepseek.py

import os
import requests
from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.config.settings import DEFAULT_MODELS

class DeepSeekModel(LLMInterface):
    def __init__(self, model_name=None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise EnvironmentError("DEEPSEEK_API_KEY is not set.")
        self.model_name = model_name or DEFAULT_MODELS["deepseek"]
        self.url = "https://api.deepseek.com/chat/completions"

    def query(self, input: PromptInput) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": input.system_prompt},
                {"role": "user", "content": input.user_prompt}
            ],
            "temperature": input.temperature,
        }

        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
