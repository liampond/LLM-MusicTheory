"""Model dispatcher with lazy imports and alias support.

Design goals:
  * Avoid importing provider SDKs until needed (speedy test collection).
  * Provide clear, actionable error messages when optional extras missing.
  * Support convenient provider aliases (e.g. "openai" -> "chatgpt").
  * Return a fresh instance each call (no hidden singletons) for configurability.

Public surface:
  * get_llm(name) -> LLMInterface instance
  * list_available_models() -> list[str] of canonical model keys
"""

from __future__ import annotations

from typing import Callable, Dict, List

from llm_music_theory.models.base import LLMInterface

# Canonical model keys recognised by the project.
_CANONICAL: List[str] = ["chatgpt", "gemini", "claude"]

# Aliases map (lowercase) -> canonical key.
_ALIASES: Dict[str, str] = {
    "openai": "chatgpt",
    "gpt": "chatgpt",  # user convenience
    "anthropic": "claude",
    "google": "gemini",
}

# Factory registry storing zero-arg callables that instantiate each model wrapper.
# Using lambdas keeps imports lazy.
_REGISTRY: Dict[str, Callable[[], LLMInterface]] = {
    "chatgpt": lambda: __import__(
        "llm_music_theory.models.chatgpt", fromlist=["ChatGPTModel"]
    ).ChatGPTModel(),
    "gemini": lambda: _load_optional(
        module="llm_music_theory.models.gemini",
        cls="GeminiModel",
        extra="google",
        human_name="Google Gemini",
    ),
    "claude": lambda: _load_optional(
        module="llm_music_theory.models.claude",
        cls="ClaudeModel",
        extra="anthropic",
        human_name="Anthropic Claude",
    ),
}


def _load_optional(module: str, cls: str, extra: str, human_name: str) -> LLMInterface:
    """Helper to lazily import optional model wrappers.

    Raises a RuntimeError with installation guidance if the import fails.
    """
    try:
        mod = __import__(module, fromlist=[cls])
        return getattr(mod, cls)()
    except ImportError as e:  # pragma: no cover (depends on env without extra)
        raise RuntimeError(
            f"{human_name} support not installed. Install extras with: 'poetry install --with {extra}'"
        ) from e


def _normalise(name: str) -> str:
    return name.strip().lower()


def list_available_models() -> List[str]:
    """Return the list of canonical model identifiers."""
    return list(_CANONICAL)


def get_llm(model_name: str) -> LLMInterface:
    """Instantiate an LLM wrapper by name or alias.

    Parameters
    ----------
    model_name: str
        Canonical name or supported alias (case-insensitive).

    Returns
    -------
    LLMInterface
        Fresh instance of the requested model wrapper.

    Raises
    ------
    TypeError
        If model_name is not a string.
    ValueError
        If the name/alias is unknown.
    RuntimeError
        If an optional model is requested but the extra dependency is missing.
    """
    if not isinstance(model_name, str):  # keep tests tolerant
        raise TypeError("model_name must be a string")

    name = _normalise(model_name)
    # Resolve aliases
    canonical = _ALIASES.get(name, name)

    if canonical not in _REGISTRY:
        # Provide helpful hint with known names
        raise ValueError(
            f"Unknown model: '{model_name}'. Supported: {', '.join(_CANONICAL)}."
        )

    # Call factory for a fresh instance
    return _REGISTRY[canonical]()


def detect_model_provider(model_name: str) -> str:
    """Detect the model provider based on model name patterns.
    
    Args:
        model_name: The specific model name (e.g., "gpt-4o", "claude-3-sonnet", "gemini-1.5-pro")
        
    Returns:
        The canonical provider name ("chatgpt", "claude", or "gemini")
        
    Raises:
        ValueError: If the model name doesn't match any known patterns
    """
    if not isinstance(model_name, str):
        raise TypeError("model_name must be a string")
    
    name_lower = model_name.lower().strip()
    
    # OpenAI/ChatGPT patterns
    if any(pattern in name_lower for pattern in [
        "gpt-", "gpt3", "gpt4", "gpt-3", "gpt-4", "o1-", "text-davinci", "text-ada", "text-babbage", "text-curie"
    ]):
        return "chatgpt"
    
    # Anthropic/Claude patterns  
    if any(pattern in name_lower for pattern in [
        "claude", "anthropic", "haiku", "sonnet", "opus"
    ]):
        return "claude"
    
    # Google/Gemini patterns
    if any(pattern in name_lower for pattern in [
        "gemini", "bison", "gecko", "palm", "google"
    ]):
        return "gemini"
    
    # Fallback: raise error with helpful message
    raise ValueError(
        f"Cannot detect provider for model '{model_name}'. "
        f"Supported patterns: OpenAI (gpt-*), Anthropic (claude-*), Google (gemini-*). "
        f"You can also specify --model explicitly."
    )


def get_llm_with_model_name(model_name: str, provider: str | None = None) -> LLMInterface:
    """Get an LLM instance with automatic provider detection or explicit provider.
    
    Args:
        model_name: The specific model name (e.g., "gpt-4o", "claude-3-sonnet")
        provider: Optional explicit provider ("chatgpt", "claude", "gemini"). 
                 If None, will auto-detect from model_name.
                 
    Returns:
        LLMInterface instance configured with the specified model name
        
    Raises:
        ValueError: If provider cannot be detected or is invalid
        TypeError: If model_name is not a string
        RuntimeError: If optional dependencies are missing
    """
    if not isinstance(model_name, str):
        raise TypeError("model_name must be a string")
    
    # Use explicit provider or auto-detect
    if provider is None:
        provider = detect_model_provider(model_name)
    else:
        # Validate explicit provider
        provider = _normalise(provider)
        provider = _ALIASES.get(provider, provider)
        if provider not in _REGISTRY:
            raise ValueError(
                f"Unknown provider: '{provider}'. Supported: {', '.join(_CANONICAL)}."
            )
    
    # Get the model instance
    model = get_llm(provider)
    
    # Set the specific model name
    if hasattr(model, "model_name"):
        setattr(model, "model_name", model_name)
    else:
        # This shouldn't happen with current implementations, but be defensive
        raise RuntimeError(f"Model wrapper for {provider} doesn't support model_name configuration")
    
    return model
