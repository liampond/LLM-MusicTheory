"""
Test the PromptBuilder behavioral contracts and interface.

These tests define what the PromptBuilder should do, independent of implementation details.
"""
import pytest
from unittest.mock import Mock, patch

from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.models.base import PromptInput


class TestPromptBuilderInterfaceContract:
    """Keep only minimal interface checks unique to implementation tests."""
    
    def test_build_returns_prompt_input(self):
        builder = PromptBuilder(
            system_prompt="System prompt",
            format_specific_user_prompt="Format prompt",
            encoded_data="Encoded data",
            guides=["Guide 1"],
            question_prompt="Question prompt",
            temperature=0.5
        )
        result = builder.build()
        assert isinstance(result, PromptInput)


class TestPromptBuilderBehaviorContract:
    """Test PromptBuilder behavioral requirements."""
    
    def test_build_user_prompt_combines_sections(self):
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format section",
            encoded_data="Encoded section",
            guides=["Guide 1", "Guide 2"],
            question_prompt="Question section",
            temperature=0.0
        )
        user_prompt = builder.build_user_prompt()
        assert "Format section" in user_prompt
        assert "Encoded section" in user_prompt
        assert "Guide 1" in user_prompt
        assert "Guide 2" in user_prompt
        assert "Question section" in user_prompt
    
    def test_build_user_prompt_proper_formatting(self):
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data",
            guides=["Guide"],
            question_prompt="Question",
            temperature=0.0
        )
        user_prompt = builder.build_user_prompt()
        sections = user_prompt.split('\n\n')
        assert len(sections) >= 4
    
    def test_build_user_prompt_handles_empty_guides(self):
        """build_user_prompt MUST handle empty guides list."""
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data", 
            guides=[],  # Empty guides
            question_prompt="Question",
            temperature=0.0
        )
        
        user_prompt = builder.build_user_prompt()
        
        # Should still work with empty guides
        assert isinstance(user_prompt, str)
        assert "Format" in user_prompt
        assert "Data" in user_prompt
        assert "Question" in user_prompt
    
    def test_build_user_prompt_handles_none_guides(self):
        """build_user_prompt SHOULD handle None in guides list."""
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data",
            guides=["Guide 1", None, "Guide 2"],  # None in guides
            question_prompt="Question",
            temperature=0.0
        )
        
        user_prompt = builder.build_user_prompt()
        
        # Should handle None gracefully
        assert isinstance(user_prompt, str)
        assert "Guide 1" in user_prompt
        assert "Guide 2" in user_prompt
        # None should not cause issues
    
    def test_build_integrates_system_and_user_prompts(self):
        builder = PromptBuilder(
            system_prompt="You are a music expert",
            format_specific_user_prompt="Analyze this:",
            encoded_data="Music data",
            guides=["Context guide"],
            question_prompt="What is the key?",
            temperature=0.3
        )
        prompt_input = builder.build()
        user_prompt = prompt_input.user_prompt
        assert prompt_input.system_prompt == "You are a music expert"
        assert "Analyze this:" in user_prompt
        assert "Music data" in user_prompt
        assert "Context guide" in user_prompt
        assert "What is the key?" in user_prompt
        assert prompt_input.temperature == 0.3
    
    def test_build_preserves_model_name(self):
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data",
            guides=[],
            question_prompt="Question",
            temperature=0.0,
            model_name="test-model"
        )
        prompt_input = builder.build()
        assert prompt_input.model_name == "test-model"
    
    def test_build_handles_none_model_name(self):
        """build() MUST handle None model_name gracefully."""
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format", 
            encoded_data="Data",
            guides=[],
            question_prompt="Question",
            temperature=0.0,
            model_name=None
        )
        
        prompt_input = builder.build()
        
        # Should not cause errors
        assert isinstance(prompt_input, PromptInput)
        assert prompt_input.model_name is None


class TestPromptBuilderDataContract:
    """Test PromptBuilder data handling and validation."""
    
    def test_prompt_builder_stores_inputs_correctly(self):
        system = "System prompt"
        format_prompt = "Format prompt"
        encoded = "Encoded data"
        guides = ["Guide 1", "Guide 2"]
        question = "Question prompt"
        temp = 0.7
        model = "test-model"
        builder = PromptBuilder(
            system_prompt=system,
            format_specific_user_prompt=format_prompt,
            encoded_data=encoded,
            guides=guides,
            question_prompt=question,
            temperature=temp,
            model_name=model
        )
        assert builder.system_prompt == system
        assert builder.format_prompt == format_prompt
        assert builder.encoded_data == encoded
        assert builder.guides == guides
        assert builder.question_prompt == question
        assert builder.temperature == temp
        assert builder.model_name == model
    
    def test_prompt_builder_default_temperature(self):
        """PromptBuilder SHOULD provide reasonable temperature default."""
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data",
            guides=[],
            question_prompt="Question"
            # No temperature specified
        )
        
        # Should have some default temperature
        assert hasattr(builder, 'temperature')
        assert isinstance(builder.temperature, (int, float))
        assert 0.0 <= builder.temperature <= 1.0
    
    def test_prompt_builder_default_model_name(self):
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format",
            encoded_data="Data",
            guides=[],
            question_prompt="Question"
        )
        assert hasattr(builder, 'model_name')
        prompt_input = builder.build()
        assert isinstance(prompt_input, PromptInput)


class TestPromptBuilderErrorHandling:
    """Test PromptBuilder error handling requirements."""
    
    def test_prompt_builder_handles_empty_strings(self):
        builder = PromptBuilder(
            system_prompt="",
            format_specific_user_prompt="",
            encoded_data="Data",
            guides=[],
            question_prompt="Question",
            temperature=0.5
        )
        prompt_input = builder.build()
        assert isinstance(prompt_input, PromptInput)
        assert prompt_input.system_prompt == ""
        assert "Data" in prompt_input.user_prompt
        assert "Question" in prompt_input.user_prompt
    
    def test_prompt_builder_handles_none_inputs(self):
        """PromptBuilder SHOULD handle None inputs appropriately."""
        # This should either work gracefully or raise appropriate errors
        try:
            builder = PromptBuilder(
                system_prompt=None,
                format_specific_user_prompt="Format",
                encoded_data="Data",
                guides=[],
                question_prompt="Question",
                temperature=0.5
            )
            prompt_input = builder.build()
            # If it succeeds, result should be valid
            assert isinstance(prompt_input, PromptInput)
        except (TypeError, ValueError, AttributeError):
            # This is also acceptable behavior for None inputs
            pass
    
    def test_prompt_builder_handles_invalid_temperature(self):
        """PromptBuilder SHOULD validate temperature values."""
        # Test with valid temperatures - these should work
        valid_temps = [0.0, 0.5, 1.0]
        for temp in valid_temps:
            builder = PromptBuilder(
                system_prompt="System",
                format_specific_user_prompt="Format",
                encoded_data="Data",
                guides=[],
                question_prompt="Question",
                temperature=temp
            )
            prompt_input = builder.build()
            assert prompt_input.temperature == temp
        
        # Test with invalid temperatures - implementation should handle appropriately
        invalid_temps = [-0.1, 1.1, "invalid", None]
        for temp in invalid_temps:
            try:
                builder = PromptBuilder(
                    system_prompt="System",
                    format_specific_user_prompt="Format",
                    encoded_data="Data",
                    guides=[],
                    question_prompt="Question",
                    temperature=temp
                )
                prompt_input = builder.build()
                # If it succeeds, temperature should be reasonable
                assert 0.0 <= prompt_input.temperature <= 1.0
            except (TypeError, ValueError):
                # This is acceptable behavior for invalid inputs
                pass


class TestPromptBuilderIntegrationContract:
    """Test PromptBuilder integration requirements."""
    
    def test_prompt_builder_output_compatible_with_models(self):
        """PromptBuilder output MUST be compatible with LLM models."""
        builder = PromptBuilder(
            system_prompt="You are a helpful assistant",
            format_specific_user_prompt="Analyze this music:",
            encoded_data="X:1\nT:Test\nK:C\nC D E F|",
            guides=["Consider the key signature"],
            question_prompt="What is the key?",
            temperature=0.7
        )
        
        prompt_input = builder.build()
        
        # Must be PromptInput type
        assert isinstance(prompt_input, PromptInput)
        
        # Must have required fields for LLM consumption
        assert isinstance(prompt_input.system_prompt, str)
        assert isinstance(prompt_input.user_prompt, str)
        assert isinstance(prompt_input.temperature, (int, float))
        
        # Content should be substantial
        assert len(prompt_input.system_prompt.strip()) > 0
        assert len(prompt_input.user_prompt.strip()) > 0
    
    def test_prompt_builder_reproducible_output(self):
        """PromptBuilder MUST produce consistent output for same inputs."""
        inputs = {
            "system_prompt": "System",
            "format_specific_user_prompt": "Format",
            "encoded_data": "Data",
            "guides": ["Guide"],
            "question_prompt": "Question",
            "temperature": 0.5
        }
        
        builder1 = PromptBuilder(**inputs)
        builder2 = PromptBuilder(**inputs)
        
        prompt1 = builder1.build()
        prompt2 = builder2.build()
        
        # Should produce identical results
        assert prompt1.system_prompt == prompt2.system_prompt
        assert prompt1.user_prompt == prompt2.user_prompt
        assert prompt1.temperature == prompt2.temperature
        assert prompt1.model_name == prompt2.model_name
