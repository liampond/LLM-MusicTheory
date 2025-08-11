"""
Test the prompt building and composition requirements.

These tests define how prompts SHOULD be constructed and validated,
independent of current implementation details.
"""
import pytest
pytestmark = pytest.mark.contract
from unittest.mock import Mock, patch
from pathlib import Path

from llm_music_theory.models.base import PromptInput


class TestPromptCompositionContract:
    """Test the core requirements for prompt composition."""
    
    def test_prompt_builder_exists(self):
        """System MUST provide a prompt building mechanism."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Should be importable and instantiable
        assert PromptBuilder is not None
        
        # Should be able to create instances
        builder = PromptBuilder(
            system_prompt="test system",
            format_specific_user_prompt="test format", 
            encoded_data="test data",
            guides=["test guide"],
            question_prompt="test question",
            temperature=0.5
        )
        assert builder is not None
    
    def test_prompt_builder_creates_prompt_input(self):
        """PromptBuilder MUST create valid PromptInput objects."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        builder = PromptBuilder(
            system_prompt="You are a music expert",
            format_specific_user_prompt="Format: MEI",
            encoded_data="<mei>test</mei>",
            guides=["Guide content"],
            question_prompt="What key is this?",
            temperature=0.7
        )
        
        prompt_input = builder.build()
        
        assert isinstance(prompt_input, PromptInput)
        assert prompt_input.system_prompt == "You are a music expert"
        assert prompt_input.temperature == 0.7
        assert isinstance(prompt_input.user_prompt, str)
        assert len(prompt_input.user_prompt) > 0
    
    def test_prompt_component_integration(self):
        """All prompt components MUST be integrated into the final prompt."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        components = {
            "system_prompt": "System instruction",
            "format_specific_user_prompt": "Format: ABC notation",
            "encoded_data": "X:1\nT:Test\nK:C\nCDEF|",
            "guides": ["Guide 1: intervals", "Guide 2: keys"],
            "question_prompt": "Analyze this melody",
            "temperature": 0.3
        }
        
        builder = PromptBuilder(**components)
        prompt_input = builder.build()
        
        # System prompt should be preserved
        assert prompt_input.system_prompt == components["system_prompt"]
        
        # User prompt should contain all user-facing components
        user_prompt = prompt_input.user_prompt
        assert components["format_specific_user_prompt"] in user_prompt
        assert components["encoded_data"] in user_prompt
        assert components["guides"][0] in user_prompt
        assert components["guides"][1] in user_prompt
        assert components["question_prompt"] in user_prompt
        
        # Temperature should be preserved
        assert prompt_input.temperature == components["temperature"]
    
    def test_prompt_component_separation(self):
        """Prompt components SHOULD be clearly separated in output."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        builder = PromptBuilder(
            system_prompt="System",
            format_specific_user_prompt="Format info",
            encoded_data="Data content", 
            guides=["Guide 1", "Guide 2"],
            question_prompt="Question content",
            temperature=0.5
        )
        
        prompt_input = builder.build()
        user_prompt = prompt_input.user_prompt
        
        # Components should be separated (exact format is flexible)
        # But they shouldn't be mashed together without separation
        assert "Format info" in user_prompt
        assert "Data content" in user_prompt
        assert "Guide 1" in user_prompt  
        assert "Guide 2" in user_prompt
        assert "Question content" in user_prompt
        
        # Should have some form of separation between components
        # (newlines, sections, etc. - exact format is implementation detail)
        assert len(user_prompt.split()) > 6  # More than just the components concatenated


class TestPromptValidation:
    """Test prompt validation requirements."""
    
    def test_required_component_validation(self):
        """PromptBuilder MUST validate required components."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Missing system_prompt
        with pytest.raises((TypeError, ValueError)):
            PromptBuilder(
                format_specific_user_prompt="format",
                encoded_data="data",
                guides=["guide"],
                question_prompt="question",
                temperature=0.5
            )
        
        # Missing question_prompt
        with pytest.raises((TypeError, ValueError)):
            PromptBuilder(
                system_prompt="system",
                format_specific_user_prompt="format", 
                encoded_data="data",
                guides=["guide"],
                temperature=0.5
            )
    
    def test_temperature_validation(self):
        """PromptBuilder MUST validate temperature parameter (enforced on build)."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        valid_components = {
            "system_prompt": "system",
            "format_specific_user_prompt": "format",
            "encoded_data": "data", 
            "guides": ["guide"],
            "question_prompt": "question"
        }
        
        # Valid temperatures
        for temp in [0.0, 0.5, 1.0]:
            builder = PromptBuilder(**valid_components, temperature=temp)
            prompt_input = builder.build()
            assert prompt_input.temperature == temp
        
        # Invalid temperatures are validated at build()
        for temp in [-0.1, 1.1, "invalid", None]:
            builder = PromptBuilder(**valid_components, temperature=temp)  # construction allowed
            with pytest.raises((ValueError, TypeError)):
                _ = builder.build()
    
    def test_empty_component_handling(self):
        """PromptBuilder SHOULD handle empty components gracefully."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Empty guides list should be acceptable
        builder = PromptBuilder(
            system_prompt="system",
            format_specific_user_prompt="format",
            encoded_data="data",
            guides=[],  # Empty guides
            question_prompt="question",
            temperature=0.5
        )
        
        prompt_input = builder.build()
        assert isinstance(prompt_input, PromptInput)
        
        # Empty strings should be handled appropriately
        builder = PromptBuilder(
            system_prompt="system",
            format_specific_user_prompt="",  # Empty format
            encoded_data="data",
            guides=["guide"],
            question_prompt="question", 
            temperature=0.5
        )
        
        prompt_input = builder.build()
        assert isinstance(prompt_input, PromptInput)


class TestPromptFormatSupport:
    """Test support for different music formats."""
    
    @pytest.mark.parametrize("format_name", ["mei", "musicxml", "abc", "humdrum"])
    def test_format_specific_prompts(self, format_name):
        """System SHOULD support format-specific prompt templates."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Each format should have appropriate base prompt content
        format_prompts = {
            "mei": "Music format: MEI",
            "musicxml": "Music format: MusicXML", 
            "abc": "Music format: ABC notation",
            "humdrum": "Music format: Humdrum"
        }
        
        builder = PromptBuilder(
            system_prompt="system",
            format_specific_user_prompt=format_prompts[format_name],
            encoded_data=f"<{format_name}>test</{format_name}>",
            guides=["guide"],
            question_prompt="question",
            temperature=0.5
        )
        
        prompt_input = builder.build()
        assert format_prompts[format_name] in prompt_input.user_prompt
    
    def test_format_data_validation(self):
        """System SHOULD validate format-specific data appropriately."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # This is a design requirement - the system should eventually
        # validate that encoded_data matches the specified format
        
        # For now, just ensure it doesn't crash with various inputs
        test_data = [
            "<mei>valid mei content</mei>",
            "X:1\nT:Test\nK:C\nCDEF|",  # ABC
            "<?xml version='1.0'?><score-partwise></score-partwise>",  # MusicXML
            "**kern\n4c\n*-"  # Humdrum
        ]
        
        for data in test_data:
            builder = PromptBuilder(
                system_prompt="system",
                format_specific_user_prompt="format",
                encoded_data=data,
                guides=["guide"],
                question_prompt="question",
                temperature=0.5
            )
            
            prompt_input = builder.build()
            assert data in prompt_input.user_prompt


class TestPromptContextHandling:
    """Test context vs non-context prompt modes."""
    
    def test_context_mode_support(self):
        """System SHOULD support both context and non-context modes."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        base_components = {
            "system_prompt": "system",
            "format_specific_user_prompt": "format",
            "encoded_data": "data",
            "question_prompt": "question",
            "temperature": 0.5
        }
        
        # Context mode - with guides
        context_builder = PromptBuilder(
            **base_components,
            guides=["Context guide 1", "Context guide 2"]
        )
        context_prompt = context_builder.build()
        
        # Non-context mode - without guides  
        no_context_builder = PromptBuilder(
            **base_components,
            guides=[]
        )
        no_context_prompt = no_context_builder.build()
        
        # Context prompt should be longer (includes guides)
        assert len(context_prompt.user_prompt) > len(no_context_prompt.user_prompt)
        
        # Context prompt should contain guide content
        assert "Context guide 1" in context_prompt.user_prompt
        assert "Context guide 2" in context_prompt.user_prompt
        
        # Non-context prompt should not contain guide content
        assert "Context guide 1" not in no_context_prompt.user_prompt
        assert "Context guide 2" not in no_context_prompt.user_prompt
    
    def test_guide_content_integration(self):
        """Guide content SHOULD be properly integrated in context mode."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        guides = [
            "Step 1: Identify the key signature",
            "Step 2: Analyze interval relationships", 
            "Step 3: Determine chord progressions"
        ]
        
        builder = PromptBuilder(
            system_prompt="system",
            format_specific_user_prompt="format",
            encoded_data="data",
            guides=guides,
            question_prompt="Analyze this music",
            temperature=0.5
        )
        
        prompt_input = builder.build()
        user_prompt = prompt_input.user_prompt
        
        # All guide content should be present
        for guide in guides:
            assert guide in user_prompt
        
        # Guides should appear before the final question
        question_pos = user_prompt.find("Analyze this music")
        for guide in guides:
            guide_pos = user_prompt.find(guide)
            assert guide_pos < question_pos, "Guides should appear before question"


class TestPromptBuilderPerformance:
    """Test performance requirements for prompt building."""
    
    @pytest.mark.slow
    def test_prompt_building_speed(self):
        """Prompt building SHOULD be fast for typical use cases."""
        import time
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Typical prompt components
        components = {
            "system_prompt": "You are a music theory expert." * 50,  # Larger content
            "format_specific_user_prompt": "Format: MEI notation",
            "encoded_data": "<mei>" + "test content " * 100 + "</mei>",  # Larger data
            "guides": [f"Guide {i}: content " * 20 for i in range(5)],  # Multiple guides
            "question_prompt": "Analyze this musical example in detail",
            "temperature": 0.7
        }
        
        # Build multiple prompts to test performance
        start_time = time.time()
        
        for _ in range(10):
            builder = PromptBuilder(**components)
            prompt_input = builder.build()
            assert isinstance(prompt_input, PromptInput)
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        # Should be fast (< 0.1 seconds per prompt)
        assert avg_time < 0.1, f"Average prompt building time {avg_time:.3f}s is too slow"
    
    def test_memory_efficiency(self):
        """Prompt building SHOULD be memory efficient."""
        from llm_music_theory.prompts.prompt_builder import PromptBuilder
        
        # Build many prompts to test memory usage
        prompts = []
        
        for i in range(100):
            builder = PromptBuilder(
                system_prompt=f"System prompt {i}",
                format_specific_user_prompt=f"Format {i}",
                encoded_data=f"Data {i}" * 50,
                guides=[f"Guide {i}.{j}" for j in range(3)],
                question_prompt=f"Question {i}",
                temperature=0.5
            )
            
            prompt_input = builder.build()
            prompts.append(prompt_input)
        
        # All prompts should be valid
        assert len(prompts) == 100
        for prompt in prompts:
            assert isinstance(prompt, PromptInput)
        
        # This is mainly a smoke test - actual memory measurement
        # would require more sophisticated tooling
