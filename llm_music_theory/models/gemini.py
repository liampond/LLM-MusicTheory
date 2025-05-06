# models/gemini.py

import os
import google.generativeai as genai
from models.base import LLMInterface, PromptInput
from llm_music_theory.config.settings import DEFAULT_MODELS


class GeminiModel(LLMInterface):
    """
    Wrapper for Gemini 1.5 Flash Lite using Google Generative AI SDK.
    """

    def __init__(self, model_name: str = None):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in your .env file.")
        genai.configure(api_key=api_key)
        self.model_name = model_name or DEFAULT_MODELS["google"]
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def query(self, input: PromptInput) -> str:
        # Gemini doesn’t use system vs user roles, so we merge
        prompt = f"{input.system_prompt.strip()}\n\n{input.user_prompt.strip()}"
        response = self.model.generate_content(prompt)
        return response.text.strip()
