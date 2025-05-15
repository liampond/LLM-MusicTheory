import os
from typing import Optional
from openai import OpenAI
from llm_music_theory.models.base import LLMInterface, PromptInput


class ChatGPTModel(LLMInterface):
    """
    ChatGPTModel wraps OpenAI's ChatCompletion API (e.g., gpt-4, gpt-4o) 
    behind a uniform interface. It reads the API key from the environment,
    supports per-call model overrides, temperature tuning, and optional
    token limits.
    """

    def __init__(self, model_name: Optional[str] = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name

    def query(self, input: PromptInput) -> str:
        """
        Sends a system + user prompt to the ChatCompletion endpoint.

        Parameters:
            input (PromptInput): 
                - system_prompt (str): Instructions for the assistant.
                - user_prompt (str): The combined prompt (format intro, encoded data, guides, question).
                - temperature (float): Sampling temperature.
                - max_tokens (Optional[int]): Maximum response tokens.
                - model_name (Optional[str]): Override default model.

        Returns:
            str: The assistant's response text.
        """
        model = input.model_name or self.model_name
        max_tokens = getattr(input, "max_tokens", None) or 2048

        messages = [
            {"role": "system", "content": input.system_prompt},
            {"role": "user", "content": input.user_prompt},
        ]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=input.temperature,
            max_tokens=max_tokens,
        )

        # TODO: Add logging of request/response here for auditing if enabled
        return response.choices[0].message.content.strip()
