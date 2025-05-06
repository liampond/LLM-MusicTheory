# models/chatgpt.py

import os
import openai
from typing import Optional
from models.base import LLMInterface, PromptInput


class ChatGPTModel(LLMInterface):
    """
    Wrapper for OpenAI's ChatGPT (gpt-4o, gpt-4-turbo, etc.)
    """

    def __init__(self, model_name: Optional[str] = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in your environment.")
        self.model_name = model_name
        openai.api_key = self.api_key

    def query(self, input: PromptInput) -> str:
        """
        Converts PromptInput into OpenAI chat format and queries the API.

        Parameters:
            input (PromptInput): The prompt and settings.

        Returns:
            str: The model's response.
        """
        messages = [
            {"role": "system", "content": input.system_prompt},
            {"role": "user", "content": input.user_prompt}
        ]

        response = openai.ChatCompletion.create(
            model=input.model_name or self.model_name,
            messages=messages,
            temperature=input.temperature
        )

        return response["choices"][0]["message"]["content"].strip()
