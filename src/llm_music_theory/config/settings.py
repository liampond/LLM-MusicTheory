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
    "openai": "gpt-4.1-nano-2025-04-14",  # Cheapest, $0.10USD/MToken Input
    "anthropic": "claude-3-haiku-20240307", # Cheapest, $0.25USD/MToken Input
    "google": "models/gemini-1.5-flash-latest", # Cheapest, free for testing
    "deepseek": "deepseek-chat" # Cheapest, $0.07USD/MToken Input
}

