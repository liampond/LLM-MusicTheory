# config/settings.py

from dotenv import load_dotenv
import os

load_dotenv()

# Default models by provider
DEFAULT_MODELS = {
    "openai": "gpt-4.1-nano-2025-04-14",  # Cheapest, $0.10USD/MToken Input
    "anthropic": "claude-3-haiku-20240307",
    # Use a stable generally-available Gemini text model rather than a dated preview
    "google": "gemini-1.5-flash",
}

API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
}