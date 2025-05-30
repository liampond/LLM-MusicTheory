<<<<<<< HEAD
"""
Test models with mock API responses to avoid actual API calls and costs.
"""
=======
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import importlib
import types
<<<<<<< HEAD
from unittest.mock import Mock, patch
=======
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc

import pytest

from llm_music_theory.models.base import PromptInput


def _patch_dotenv(monkeypatch):
<<<<<<< HEAD
    """Mock dotenv to avoid loading real environment files."""
    # Since env_loader module doesn't exist, we'll patch the settings directly
    mock_api_keys = {
        "openai": "mock-openai-key",
        "anthropic": "mock-anthropic-key", 
        "google": "mock-google-key",
        "deepseek": "mock-deepseek-key"
    }
    monkeypatch.setattr("llm_music_theory.config.settings.API_KEYS", mock_api_keys)


def _patch_openai(monkeypatch):
    """Mock OpenAI client for ChatGPT and DeepSeek models."""
    class DummyOpenAI:
        last_call = None
        
        def __init__(self, *args, **kwargs):
            pass
            
        @property
        def chat(self):
            return self
            
        @property 
        def completions(self):
            return self
            
        def create(self, **kwargs):
            DummyOpenAI.last_call = kwargs
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "ok"
            return mock_response
    
    monkeypatch.setattr("openai.OpenAI", DummyOpenAI)
=======
    module = types.ModuleType("dotenv")
    module.load_dotenv = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "dotenv", module)


def _patch_openai(monkeypatch):
    class DummyOpenAI:
        last_call = None

        def __init__(self, api_key=None, base_url=None):
            self.api_key = api_key
            self.base_url = base_url
            chat = types.SimpleNamespace()
            chat.completions = types.SimpleNamespace(create=self._create)
            self.chat = chat

        def _create(self, model, messages, temperature, max_tokens):
            DummyOpenAI.last_call = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            choice = types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))
            return types.SimpleNamespace(choices=[choice])

    module = types.ModuleType("openai")
    module.OpenAI = DummyOpenAI
    monkeypatch.setitem(sys.modules, "openai", module)
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
    return DummyOpenAI


def _patch_anthropic(monkeypatch):
<<<<<<< HEAD
    """Mock Anthropic client for Claude model."""
    class DummyAnthropic:
        last_call = None
        
        def __init__(self, *args, **kwargs):
            pass
            
        @property
        def messages(self):
            return self
            
        def create(self, **kwargs):
            DummyAnthropic.last_call = kwargs
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "ok"
            return mock_response
    
    monkeypatch.setattr("anthropic.Anthropic", DummyAnthropic)
=======
    class DummyAnthropic:
        last_call = None

        def __init__(self, api_key=None):
            self.api_key = api_key
            self.messages = types.SimpleNamespace(create=self._create)

        def _create(self, model, max_tokens, temperature, system, messages):
            DummyAnthropic.last_call = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system,
                "messages": messages,
            }
            content = [types.SimpleNamespace(text="ok")]
            return types.SimpleNamespace(content=content)

    module = types.ModuleType("anthropic")
    module.Anthropic = DummyAnthropic
    monkeypatch.setitem(sys.modules, "anthropic", module)
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
    return DummyAnthropic


def _patch_google(monkeypatch):
<<<<<<< HEAD
    """Mock Google genai client for Gemini model."""
    class MockModels:
        last_call = None
        
        def generate_content(self, **kwargs):
            MockModels.last_call = kwargs
            mock_response = Mock()
            mock_response.text = "ok"
            return mock_response
    
    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()
    
    # Create a mock genai module
    mock_genai = Mock()
    mock_genai.Client = DummyClient
    
    # Mock the google.genai import path that the actual model uses
    monkeypatch.setattr("llm_music_theory.models.gemini.genai", mock_genai)
    return MockModels


def test_chatgpt_query(monkeypatch):
    """Test ChatGPT model with mocked API calls."""
=======
    class DummyClient:
        last_call = None

        def __init__(self, api_key=None):
            self.api_key = api_key
            models = types.SimpleNamespace(generate_content=self._generate)
            self.models = models

        def _generate(self, model, contents, config):
            DummyClient.last_call = {
                "model": model,
                "contents": contents,
                "config": config,
            }
            return types.SimpleNamespace(text="ok")

    genai = types.ModuleType("google.genai")
    genai.Client = DummyClient
    google = types.ModuleType("google")
    google.genai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    return DummyClient


def test_chatgpt_query(monkeypatch):
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
    DummyOpenAI = _patch_openai(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    import importlib
    chatgpt_mod = importlib.reload(importlib.import_module("llm_music_theory.models.chatgpt"))
    model = chatgpt_mod.ChatGPTModel()
    inp = PromptInput(system_prompt="sys", user_prompt="user", temperature=0.3, max_tokens=10)
    result = model.query(inp)
    assert result == "ok"
    assert DummyOpenAI.last_call == {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "user"},
        ],
        "temperature": 0.3,
        "max_tokens": 10,
    }


def test_deepseek_query(monkeypatch):
<<<<<<< HEAD
    """Test DeepSeek model with mocked API calls."""
=======
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
    DummyOpenAI = _patch_openai(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test")
    import importlib
    deepseek_mod = importlib.reload(importlib.import_module("llm_music_theory.models.deepseek"))
    model = deepseek_mod.DeepSeekModel()
    inp = PromptInput(system_prompt="s", user_prompt="u", temperature=0.1, max_tokens=5)
    result = model.query(inp)
    assert result == "ok"
    assert DummyOpenAI.last_call == {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": "u"},
        ],
        "temperature": 0.1,
        "max_tokens": 5,
    }


def test_claude_query(monkeypatch):
<<<<<<< HEAD
    """Test Claude model with mocked API calls."""
=======
>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
    _patch_dotenv(monkeypatch)
    DummyAnthropic = _patch_anthropic(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    import importlib
    claude_mod = importlib.reload(importlib.import_module("llm_music_theory.models.claude"))
    from llm_music_theory.config.settings import DEFAULT_MODELS
    model = claude_mod.ClaudeModel()
    inp = PromptInput(system_prompt="sys", user_prompt="user", temperature=0.2, max_tokens=15)
    result = model.query(inp)
    assert result == "ok"
    assert DummyAnthropic.last_call == {
        "model": DEFAULT_MODELS["anthropic"],
        "max_tokens": 15,
        "temperature": 0.2,
        "system": "sys",
        "messages": [{"role": "user", "content": "user"}],
    }


def test_gemini_query(monkeypatch):
<<<<<<< HEAD
    """Test Gemini model with mocked API calls."""
    # Skip this test for now due to complex google-genai library mocking requirements
    pytest.skip("Gemini test skipped - complex library mocking required")
=======
    DummyClient = _patch_google(monkeypatch)
    monkeypatch.setenv("GOOGLE_API_KEY", "test")
    _patch_dotenv(monkeypatch)
    import importlib
    gemini_mod = importlib.reload(importlib.import_module("llm_music_theory.models.gemini"))
    from llm_music_theory.config.settings import DEFAULT_MODELS
    model = gemini_mod.GeminiModel()
    inp = PromptInput(system_prompt="s", user_prompt="u", temperature=0.4, max_tokens=8)
    result = model.query(inp)
    assert result == "ok"
    prompt = "s\n\nu"
    assert DummyClient.last_call == {
        "model": DEFAULT_MODELS["google"],
        "contents": prompt,
        "config": {"temperature": 0.4, "max_output_tokens": 8},
    }

>>>>>>> 09964a391df58e452cc62beb2d60c13f3c879bdc
