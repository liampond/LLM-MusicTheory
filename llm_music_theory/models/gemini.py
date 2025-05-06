import os
import google.generativeai as genai
from typing import Optional
from llm_music_theory.models.base import LLMInterface, PromptInput


class GeminiModel(LLMInterface):
    """
    GeminiModel provides a structured wrapper for Google Generative AI (Gemini).
    It reads GOOGLE_API_KEY from the environment, supports per-call model overrides,
    temperature tuning, and optional token limits.
    """

    def __init__(self, model_name: Optional[str] = "gemini-pro"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def query(self, input: PromptInput) -> str:
        """
        Sends a system + user prompt to the Gemini chat endpoint.

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
        max_output_tokens = getattr(input, "max_tokens", None) or 2048

        # Start a chat with empty history
        chat = self.model.start_chat(history=[])
        prompt_text = f"{input.system_prompt}\n\n{input.user_prompt}"
        response = chat.send_message(
            prompt_text,
            generation_config={
                "temperature": input.temperature,
                "max_output_tokens": max_output_tokens
            }
        )

        # TODO: Hook in optional logging here for request/response tracing
        return response.text.strip()
