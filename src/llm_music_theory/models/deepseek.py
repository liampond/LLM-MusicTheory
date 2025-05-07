import os
import openai
from typing import Optional
from llm_music_theory.models.base import LLMInterface, PromptInput


class DeepSeekModel(LLMInterface):
    """
    DeepSeekModel uses an OpenAI-compatible API endpoint to query DeepSeek LLMs.
    It reads DEEPSEEK_API_KEY from the environment, supports per-call model overrides,
    temperature tuning, and optional token limits.
    """

    def __init__(self, model_name: Optional[str] = "deepseek-chat"):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise EnvironmentError("DEEPSEEK_API_KEY is not set in the environment.")
        openai.api_key = self.api_key
        openai.api_base = "https://api.deepseek.com/v1"
        self.model_name = model_name

    def query(self, input: PromptInput) -> str:
        """
        Sends a system + user prompt to the DeepSeek-compatible ChatCompletion endpoint.

        Parameters:
            input (PromptInput):
                - system_prompt (str): Instructions for the assistant.
                - user_prompt   (str): The combined prompt (format intro, encoded data, guides, question).
                - temperature   (float): Sampling temperature.
                - max_tokens    (Optional[int]): Maximum response tokens.
                - model_name    (Optional[str]): Override default model.

        Returns:
            str: The assistant's response text.
        """
        model = input.model_name or self.model_name
        max_tokens = getattr(input, "max_tokens", None) or 2048

        messages = [
            {"role": "system", "content": input.system_prompt},
            {"role": "user",   "content": input.user_prompt},
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=input.temperature,
            max_tokens=max_tokens,
        )

        # TODO: Hook in optional logging here for request/response tracing
        return response.choices[0].message.content.strip()
