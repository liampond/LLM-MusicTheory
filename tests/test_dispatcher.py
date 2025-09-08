"""
Outcome-focused tests for the LLM dispatcher.

These tests validate observable behavior of get_llm without coupling to
internal import patterns or attribute names.
"""

import pytest

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.models.base import LLMInterface, PromptInput


@pytest.mark.unit
class TestDispatcherBasics:
    def test_supported_models_construct(self, mock_api_keys):
        # Keep a minimal smoke check; thorough interface checks live in contract tests
        model = get_llm("chatgpt")
        assert isinstance(model, LLMInterface)

    def test_invalid_model_names(self):
        for invalid in ["invalid", "gpt-4", "", 123, None]:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                get_llm(invalid)  # type: ignore[arg-type]

    def test_case_insensitive(self, mock_api_keys):
        for variant in ["ChatGPT", "CHATGPT", "Claude", "GEMINI"]:
            model = get_llm(variant)
            assert isinstance(model, LLMInterface)

    def test_fresh_instances(self, mock_api_keys):
        a = get_llm("chatgpt")
        b = get_llm("chatgpt")
        assert a is not b


@pytest.mark.unit
class TestDispatcherQuerySmoke:
    def test_model_query_returns_string(self, mock_api_keys):
        pi = PromptInput(
            system_prompt="You are a music theory expert.",
            user_prompt="Analyze: C major scale",
            temperature=0.2,
            max_tokens=32,
        )
        model = get_llm("chatgpt")
        out = model.query(pi)
        assert isinstance(out, str)
        assert out != ""


@pytest.mark.slow
class TestDispatcherPerformance:
    def test_repeated_instantiation_fast_enough(self, mock_api_keys):
        import time
        start = time.time()
        for _ in range(8):
            assert isinstance(get_llm("chatgpt"), LLMInterface)
        assert time.time() - start < 5.0
