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
