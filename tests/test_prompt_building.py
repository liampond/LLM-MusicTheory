"""
Test the prompt building and compilation process without making API calls.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import pytest

from llm_music_theory.core.prompt_builder import PromptBuilder
from llm_music_theory.models.base import PromptInput


class TestPromptBuilder:
    """Test the PromptBuilder class for proper prompt assembly."""

    def test_build_user_prompt(self):
        """Test that user prompt is assembled correctly from components."""
        builder = PromptBuilder(
            system_prompt="You are a music theory expert.",
            format_specific_user_prompt="Music format: MEI.",
            encoded_data="<mei>...</mei>",
            guides=["Guide 1 content", "Guide 2 content"],
            question_prompt="What key is this in?",
            temperature=0.2
        )
        
        user_prompt = builder.build_user_prompt()
        
        # Check that all components are included
        assert "Music format: MEI." in user_prompt
        assert "<mei>...</mei>" in user_prompt
        assert "Guide 1 content" in user_prompt
        assert "Guide 2 content" in user_prompt
        assert "What key is this in?" in user_prompt
        
        # Check proper structure with double newlines
        sections = user_prompt.split("\n\n")
        assert len(sections) == 5  # format + encoded + guide1 + guide2 + question

    def test_build_with_empty_guides(self):
        """Test prompt building with empty guides list."""
        builder = PromptBuilder(
            system_prompt="System prompt",
            format_specific_user_prompt="Format prompt",
            encoded_data="Data",
            guides=[],
            question_prompt="Question",
            temperature=0.0
        )
        
        user_prompt = builder.build_user_prompt()
        sections = user_prompt.split("\n\n")
        assert len(sections) == 3  # format + data + question

    def test_build_prompt_input(self):
        """Test that PromptInput is created correctly."""
        builder = PromptBuilder(
            system_prompt="System prompt",
            format_specific_user_prompt="Format prompt",
            encoded_data="Data",
            guides=["Guide"],
            question_prompt="Question",
            temperature=0.5,
            model_name="test-model"
        )
        
        prompt_input = builder.build()
        
        assert isinstance(prompt_input, PromptInput)
        assert prompt_input.system_prompt == "System prompt"
        assert prompt_input.temperature == 0.5
        assert prompt_input.model_name == "test-model"
        assert "Format prompt" in prompt_input.user_prompt
        assert "Data" in prompt_input.user_prompt
        assert "Guide" in prompt_input.user_prompt
        assert "Question" in prompt_input.user_prompt

    def test_build_with_whitespace_handling(self):
        """Test that extra whitespace is properly handled."""
        builder = PromptBuilder(
            system_prompt="  System prompt  ",
            format_specific_user_prompt="  Format prompt  ",
            encoded_data="  Data  ",
            guides=["  Guide 1  ", "  Guide 2  "],
            question_prompt="  Question  ",
            temperature=0.0
        )
        
        user_prompt = builder.build_user_prompt()
        
        # Should not have leading/trailing whitespace on sections
        lines = user_prompt.split("\n")
        for line in lines:
            if line:  # Skip empty lines
                assert not line.startswith(" ")
                assert not line.endswith(" ")


class TestPromptInputValidation:
    """Test the PromptInput dataclass validation."""

    def test_prompt_input_creation(self):
        """Test basic PromptInput creation."""
        prompt_input = PromptInput(
            system_prompt="System",
            user_prompt="User",
            temperature=0.7,
            model_name="test-model",
            max_tokens=100
        )
        
        assert prompt_input.system_prompt == "System"
        assert prompt_input.user_prompt == "User"
        assert prompt_input.temperature == 0.7
        assert prompt_input.model_name == "test-model"
        assert prompt_input.max_tokens == 100

    def test_prompt_input_defaults(self):
        """Test PromptInput with default values."""
        prompt_input = PromptInput(
            system_prompt="System",
            user_prompt="User"
        )
        
        assert prompt_input.temperature == 0.0
        assert prompt_input.model_name is None
        assert prompt_input.max_tokens is None

    def test_prompt_input_temperature_ranges(self):
        """Test various temperature values."""
        # Test valid ranges
        for temp in [0.0, 0.5, 1.0, 1.5, 2.0]:
            prompt_input = PromptInput(
                system_prompt="System",
                user_prompt="User",
                temperature=temp
            )
            assert prompt_input.temperature == temp
