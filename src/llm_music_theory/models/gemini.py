# models/gemini.py

import os
from typing import Optional

from google import genai

from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.config.settings import DEFAULT_MODELS


class GeminiModel(LLMInterface):
    """
    Wrapper for Google's Gemini models via the Google Gen AI SDK (google-genai).
    Reads GOOGLE_API_KEY from the environment, supports per-call model overrides,
    temperature control, and optional max_tokens.
    """

    def __init__(self, model_name: Optional[str] = None):
        # Load API key
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")

        # Initialize the client explicitly with the API key (avoid relying on ambient config)
        self.client = genai.Client(api_key=self.api_key)
        
        # Choose default model from settings if not overridden
        self.model_name = model_name or DEFAULT_MODELS["google"]

    def query(self, input: PromptInput) -> str:
        """
        Sends a single-turn prompt (system + user) to Gemini via generate_content.

        Parameters:
            input (PromptInput): 
                - system_prompt (str): High-level instructions for Gemini.
                - user_prompt   (str): The combined prompt (format intro, encoded data, guides, question).
                - temperature   (float): Sampling temperature.
                - max_tokens    (Optional[int]): Maximum tokens for the response.
                - model_name    (Optional[str]): Override for the model to use.

        Returns:
            str: The generated text from Gemini.
        """
        # Determine which model to call
        model_id = input.model_name or self.model_name
        
        # Fix model format - remove "models/" prefix if it exists
        if model_id.startswith("models/"):
            model_id = model_id[7:]  # Strip "models/" prefix
        
        # Build the prompt by concatenating system + user
        prompt = f"{input.system_prompt}\n\n{input.user_prompt}"

        # Configure generation settings
        config = {
            "temperature": input.temperature
        }
        if getattr(input, "max_tokens", None):
            config["max_output_tokens"] = input.max_tokens
        
        # Log the model name being used
        print(f"Using model: {model_id}")
            
        # Generate content using the client API
        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )

        # Return the trimmed result
        return response.text.strip()