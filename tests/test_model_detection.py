"""Tests for model detection functionality."""

import pytest
from llm_music_theory.core.dispatcher import detect_model_provider, get_llm_with_model_name


class TestModelDetection:
    """Test automatic model provider detection from model names."""

    def test_detect_openai_models(self):
        """OpenAI/ChatGPT model patterns should be detected correctly."""
        openai_models = [
            "gpt-4o",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "GPT-4O",  # case insensitive
            "text-davinci-003",
            "text-ada-001",
            "o1-preview",
            "o1-mini"
        ]
        
        for model in openai_models:
            assert detect_model_provider(model) == "chatgpt", f"Failed to detect {model} as chatgpt"

    def test_detect_anthropic_models(self):
        """Anthropic/Claude model patterns should be detected correctly."""
        anthropic_models = [
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229",
            "claude-2.1",
            "claude-instant-1.2",
            "CLAUDE-3-SONNET",  # case insensitive
        ]
        
        for model in anthropic_models:
            assert detect_model_provider(model) == "claude", f"Failed to detect {model} as claude"

    def test_detect_google_models(self):
        """Google/Gemini model patterns should be detected correctly."""
        google_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision",
            "GEMINI-1.5-PRO",  # case insensitive
            "palm-2",
            "text-bison-001",
        ]
        
        for model in google_models:
            assert detect_model_provider(model) == "gemini", f"Failed to detect {model} as gemini"

    def test_detect_unknown_model_raises_error(self):
        """Unknown model patterns should raise ValueError with helpful message."""
        unknown_models = [
            "unknown-model",
            "llama-2-70b",
            "mistral-7b",
            "random-model-name"
        ]
        
        for model in unknown_models:
            with pytest.raises(ValueError) as exc_info:
                detect_model_provider(model)
            
            error_msg = str(exc_info.value)
            assert "Cannot detect provider" in error_msg
            assert "OpenAI (gpt-*)" in error_msg
            assert "Anthropic (claude-*)" in error_msg
            assert "Google (gemini-*)" in error_msg

    def test_detect_empty_or_invalid_input(self):
        """Invalid input should raise appropriate errors."""
        with pytest.raises(TypeError):
            detect_model_provider(None)  # type: ignore
        
        with pytest.raises(TypeError):
            detect_model_provider(123)  # type: ignore
        
        with pytest.raises(ValueError):
            detect_model_provider("")
        
        with pytest.raises(ValueError):
            detect_model_provider("   ")


class TestGetLLMWithModelName:
    """Test the get_llm_with_model_name function."""

    def test_auto_detect_chatgpt(self):
        """Should auto-detect ChatGPT from model name."""
        model = get_llm_with_model_name("gpt-4o")
        assert hasattr(model, "model_name")
        assert getattr(model, "model_name") == "gpt-4o"
        assert "ChatGPTModel" in str(type(model))

    def test_explicit_provider_override(self):
        """Should use explicit provider when provided."""
        # Test that explicit provider overrides auto-detection
        model = get_llm_with_model_name("gpt-4o", provider="chatgpt")
        assert hasattr(model, "model_name")
        assert getattr(model, "model_name") == "gpt-4o"

    def test_invalid_explicit_provider(self):
        """Should raise error for invalid explicit provider."""
        with pytest.raises(ValueError) as exc_info:
            get_llm_with_model_name("gpt-4o", provider="invalid-provider")
        
        assert "Unknown provider" in str(exc_info.value)

    def test_invalid_model_name_type(self):
        """Should raise TypeError for non-string model names."""
        with pytest.raises(TypeError):
            get_llm_with_model_name(123)  # type: ignore
        
        with pytest.raises(TypeError):
            get_llm_with_model_name(None)  # type: ignore

    def test_auto_detect_unknown_model(self):
        """Should raise error when auto-detection fails."""
        with pytest.raises(ValueError) as exc_info:
            get_llm_with_model_name("unknown-model-xyz")
        
        assert "Cannot detect provider" in str(exc_info.value)
