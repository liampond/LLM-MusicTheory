"""
Test the PromptRunner class for proper prompt compilation without API calls.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import pytest

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import LLMInterface, PromptInput


class MockLLM(LLMInterface):
    """Mock LLM for testing that captures the query without making API calls."""
    
    def __init__(self):
        self.last_query = None
        self.response = "Mock response"
    
    def query(self, input: PromptInput) -> str:
        self.last_query = input
        return self.response


class TestPromptRunner:
    """Test the PromptRunner class for proper data loading and prompt assembly."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directory structure
            encoded_base = temp_path / "encoded" / "test_exam"
            encoded_mei_dir = encoded_base / "mei"
            encoded_mei_dir.mkdir(parents=True)
            encoded_abc_dir = encoded_base / "abc"
            encoded_abc_dir.mkdir(parents=True)
            
            prompts_dir = temp_path / "prompts"
            prompts_dir.mkdir(parents=True)
            
            base_dir = prompts_dir / "base"
            base_dir.mkdir(parents=True)
            
            # Context files are separated by datatype
            questions_context_dir = prompts_dir / "test_exam" / "context" / "mei"
            questions_context_dir.mkdir(parents=True)
            
            # No context files are all in one directory
            questions_no_context_dir = prompts_dir / "test_exam" / "no_context"
            questions_no_context_dir.mkdir(parents=True)
            
            guides_dir = temp_path / "guides"
            guides_dir.mkdir(parents=True)
            
            outputs_dir = temp_path / "outputs"
            outputs_dir.mkdir(parents=True)
            
            # Create test files
            (base_dir / "system_prompt.txt").write_text("System: Analyze music theory.")
            (base_dir / "base_mei.txt").write_text("Music format: MEI. Analyze the following:")
            (base_dir / "base_abc.txt").write_text("Music format: ABC. Analyze the following:")
            
            (encoded_mei_dir / "Q1a.mei").write_text("<mei><note pitch='C4'/></mei>")
            (encoded_abc_dir / "Q1a.abc").write_text("X:1\nT:Test\nM:4/4\nK:C\nCDEF|")
            
            # Create question files with real-world naming patterns
            # Context files go in datatype-specific directories
            (questions_context_dir / "MEI_test_exam_Q1a_ContextPrompt.txt").write_text("What key is this piece in?")
            # No context files go in the no_context directory without datatype subdir
            (questions_no_context_dir / "test_exam_Q1a_NoContextPrompt.txt").write_text("What key is this piece in?")
            
            (guides_dir / "harmonic_analysis.txt").write_text("Guide: Look for key signatures.")
            
            yield temp_path

    @pytest.fixture
    def base_dirs(self, temp_data_dir):
        """Create base_dirs mapping for testing."""
        return {
            "encoded": temp_data_dir / "encoded",
            "prompts": temp_data_dir / "prompts",
            "questions": temp_data_dir / "prompts",
            "guides": temp_data_dir / "guides",
            "outputs": temp_data_dir / "outputs",
        }

    def test_prompt_runner_initialization(self, base_dirs):
        """Test PromptRunner initialization."""
        mock_llm = MockLLM()
        
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.5,
            max_tokens=100,
            save=False
        )
        
        assert runner.question_number == "Q1a"
        assert runner.datatype == "mei"
        assert runner.context is True
        assert runner.temperature == 0.5
        assert runner.max_tokens == 100
        assert runner.save is False

    def test_load_system_prompt(self, base_dirs, temp_data_dir):
        """Test loading system prompt from external file."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        system_prompt = runner._load_system_prompt()
        assert system_prompt == "System: Analyze music theory."

    def test_load_base_format_prompt(self, base_dirs, temp_data_dir):
        """Test loading base format prompt."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        format_prompt = runner._load_base_format_prompt()
        assert format_prompt == "Music format: MEI. Analyze the following:"

    def test_load_encoded_data(self, base_dirs, temp_data_dir):
        """Test loading encoded music data."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        encoded_data = runner._load_encoded()
        assert encoded_data == "<mei><note pitch='C4'/></mei>"

    def test_load_question_with_context(self, base_dirs, temp_data_dir):
        """Test loading question text with context."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        question = runner._load_question()
        assert question == "What key is this piece in?"

    def test_load_question_no_context(self, base_dirs, temp_data_dir):
        """Test loading question text without context."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        question = runner._load_question()
        assert question == "What key is this piece in?"

    def test_load_guides_with_context(self, base_dirs, temp_data_dir):
        """Test loading guides when context is enabled."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        guides = runner._load_guides()
        assert len(guides) == 1
        assert guides[0] == "Guide: Look for key signatures."

    def test_load_guides_no_context(self, base_dirs, temp_data_dir):
        """Test that no guides are loaded when context is disabled."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        guides = runner._load_guides()
        assert len(guides) == 0

    def test_build_prompt_input(self, base_dirs, temp_data_dir):
        """Test complete prompt input building."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.7,
            max_tokens=150
        )
        
        prompt_input = runner._build_prompt_input()
        
        assert isinstance(prompt_input, PromptInput)
        assert prompt_input.system_prompt == "System: Analyze music theory."
        assert prompt_input.temperature == 0.7
        assert prompt_input.max_tokens == 150
        
        # Check that user prompt contains all components
        user_prompt = prompt_input.user_prompt
        assert "Music format: MEI" in user_prompt
        assert "<mei><note pitch='C4'/></mei>" in user_prompt
        assert "Guide: Look for key signatures." in user_prompt
        assert "What key is this piece in?" in user_prompt

    def test_run_without_save(self, base_dirs, temp_data_dir):
        """Test running prompt compilation without saving."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        response = runner.run()
        
        # Check that the mock LLM received the correct prompt
        assert mock_llm.last_query is not None
        assert response == "Mock response"
        
        # Verify prompt components are present
        user_prompt = mock_llm.last_query.user_prompt
        assert "Music format: MEI" in user_prompt
        assert "<mei><note pitch='C4'/></mei>" in user_prompt
        assert "What key is this piece in?" in user_prompt

    def test_run_with_save(self, base_dirs, temp_data_dir):
        """Test running prompt compilation with saving enabled."""
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0,
            save=True
        )
        
        response = runner.run()
        
        assert response == "Mock response"
        assert runner.save_to is not None
        assert runner.save_to.exists()
        assert runner.save_to.read_text() == "Mock response"

    def test_different_datatypes(self, base_dirs, temp_data_dir):
        """Test runner with different data types."""
        # Add test files for different formats
        encoded_dir = base_dirs["encoded"] / "test_exam"
        prompts_dir = base_dirs["prompts"]
        base_dir = prompts_dir / "base"
        
        (encoded_dir / "Q1a.abc").write_text("X:1\nT:Test\nK:C\nCDEF|")
        (base_dir / "base_abc.txt").write_text("Music format: ABC notation.")
        
        mock_llm = MockLLM()
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.0
        )
        
        runner.run()
        
        user_prompt = mock_llm.last_query.user_prompt
        assert "Music format: ABC notation." in user_prompt
        assert "X:1" in user_prompt
        assert "CDEF" in user_prompt
