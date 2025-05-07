# config/settings.py

from dotenv import load_dotenv
import os

load_dotenv()  # loads from .env

API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
    "deepseek": os.getenv("DEEPSEEK_API_KEY"),
}

# Default models by provider
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-haiku-20241022", # Cheapest
    "google": "models/gemini-1.5-flash-latest", # Cheapest, free for testing
    "deepseek": "deepseek-chat"
}

