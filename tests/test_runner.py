"""
Test the PromptRunner behavioral contracts and interface.

These tests define what the PromptRunner should do, independent of implementation details.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import LLMInterface, PromptInput


class MockLLM(LLMInterface):
    """Mock LLM for testing."""
    
    def __init__(self, response="Mock response"):
        self.response = response
        self.last_query = None
    
    def query(self, input: PromptInput) -> str:
        self.last_query = input
        return self.response


class TestPromptRunnerInterfaceContract:
    """Test that PromptRunner implements the required interface contract."""
    
    def test_prompt_runner_creation(self, tmp_path):
        """PromptRunner MUST be createable with required parameters."""
        mock_model = MockLLM()
        base_dirs = {
            "prompts": tmp_path / "prompts",
            "encoded": tmp_path / "encoded", 
            "outputs": tmp_path / "outputs"
        }
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs
        )
        
        assert isinstance(runner, PromptRunner)
        assert runner.model == mock_model
        assert runner.question_number == "Q1b"
        assert runner.datatype == "abc"
        assert runner.context is True
        assert runner.exam_date == "test_exam"
    
    def test_prompt_runner_has_run_method(self, tmp_path):
        """PromptRunner MUST have a run method."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs
        )
        
        assert hasattr(runner, 'run')
        assert callable(getattr(runner, 'run'))
    
    def test_prompt_runner_accepts_temperature(self, tmp_path):
        """PromptRunner MUST accept temperature parameter."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            temperature=0.7
        )
        
        assert runner.temperature == 0.7
    
    def test_prompt_runner_accepts_max_tokens(self, tmp_path):
        """PromptRunner MUST accept max_tokens parameter."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            max_tokens=100
        )
        
        assert runner.max_tokens == 100
    
    def test_prompt_runner_accepts_save_option(self, tmp_path):
        """PromptRunner MUST accept save parameter."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs,
            save=True
        )
        
        assert runner.save is True
        assert hasattr(runner, 'save_to')


class TestPromptRunnerBehaviorContract:
    """Test PromptRunner behavioral requirements."""
    
    def test_run_returns_string_response(self, tmp_path):
        """run() MUST return a string response from the model."""
        mock_model = MockLLM("Test response")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        # Mock the file system operations
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System prompt"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format prompt"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Encoded data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=["Guide"]):
            
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=True,
                exam_date="test_exam",
                base_dirs=base_dirs
            )
            
            result = runner.run()
            
            assert isinstance(result, str)
            assert result == "Test response"
    
    def test_run_builds_prompt_correctly(self, tmp_path):
        """run() MUST build and pass correct prompt to model."""
        mock_model = MockLLM("Response")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=["Guide"]):
            
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=True,
                exam_date="test_exam",
                base_dirs=base_dirs,
                temperature=0.5
            )
            
            runner.run()
            
            # Verify model was called with PromptInput
            assert mock_model.last_query is not None
            assert isinstance(mock_model.last_query, PromptInput)
            assert mock_model.last_query.system_prompt == "System"
            assert "Format" in mock_model.last_query.user_prompt
            assert "Data" in mock_model.last_query.user_prompt
            assert "Guide" in mock_model.last_query.user_prompt
            assert "Question" in mock_model.last_query.user_prompt
            assert mock_model.last_query.temperature == 0.5
    
    def test_run_applies_max_tokens_override(self, tmp_path):
        """run() MUST apply max_tokens override when provided."""
        mock_model = MockLLM("Response")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=[]):
            
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=False,
                exam_date="test_exam",
                base_dirs=base_dirs,
                max_tokens=150
            )
            
            runner.run()
            
            # max_tokens should be applied to prompt input
            assert hasattr(mock_model.last_query, 'max_tokens')
            assert mock_model.last_query.max_tokens == 150
    
    def test_run_saves_response_when_requested(self, tmp_path):
        """run() MUST save response to file when save=True."""
        mock_model = MockLLM("Test response to save")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=[]):
            
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=False,
                exam_date="test_exam",
                base_dirs=base_dirs,
                save=True
            )
            
            # Mock the save method
            with patch.object(runner, '_save_response') as mock_save:
                result = runner.run()
                
                # Should save the response
                mock_save.assert_called_once_with("Test response to save")
    
    def test_run_writes_input_bundle_when_saving(self, tmp_path):
        """run() SHOULD create a companion .input.json with prompt components when save=True."""
        mock_model = MockLLM("Bundle response")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}

        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="EncodedData"), \
             patch.object(PromptRunner, '_load_question', return_value="QuestionText"), \
             patch.object(PromptRunner, '_load_guides', return_value=["GuideOne", "GuideTwo"]):
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=True,
                exam_date="test_exam",
                base_dirs=base_dirs,
                save=True
            )
            runner.run()
            # Expect input bundle path attribute and file existence
            assert hasattr(runner, 'input_bundle_path')
            bundle_path = runner.input_bundle_path
            assert bundle_path.exists()
            text = bundle_path.read_text(encoding='utf-8')
            assert '"file_id": "Q1b"' in text
            assert '"encoded_data"' in text
            assert '"guides"' in text
            assert '"user_prompt_compiled"' in text
    
    def test_run_logs_execution_info(self, tmp_path):
        """run() SHOULD log execution information."""
        mock_model = MockLLM("Response")
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=[]):
            
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=True,
                exam_date="test_exam",
                base_dirs=base_dirs,
                temperature=0.3
            )
            
            # Mock the logger
            with patch.object(runner.logger, 'info') as mock_log:
                runner.run()
                
                # Should log running and received messages
                assert mock_log.call_count >= 2
                
                # Check log messages contain expected information
                log_messages = [call[0][0] for call in mock_log.call_args_list]
                running_msg = next((msg for msg in log_messages if "Running" in msg), None)
                received_msg = next((msg for msg in log_messages if "Received" in msg), None)
                
                assert running_msg is not None
                assert "Q1b" in running_msg
                assert "abc" in running_msg
                assert "context=True" in running_msg
                assert "temp=0.3" in running_msg
                
                assert received_msg is not None
                assert "Q1b" in received_msg


class TestPromptRunnerDataHandlingContract:
    """Test PromptRunner data loading and validation."""
    
    def test_prompt_runner_handles_valid_datatypes(self, tmp_path):
        """PromptRunner MUST handle all valid music format datatypes."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        valid_datatypes = ["abc", "humdrum", "mei", "musicxml"]
        
        for datatype in valid_datatypes:
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype=datatype,
                context=False,
                exam_date="test_exam",
                base_dirs=base_dirs
            )
            
            # Should normalize to lowercase
            assert runner.datatype == datatype.lower()
    
    def test_prompt_runner_handles_context_flag(self, tmp_path):
        """Keep a minimal context flag check; deep differences are in contract tests."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        runner_with_context = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=True,
            exam_date="test_exam",
            base_dirs=base_dirs
        )
        assert runner_with_context.context is True
    
    def test_prompt_runner_validates_base_dirs(self, tmp_path):
        """PromptRunner MUST validate base_dirs parameter."""
        mock_model = MockLLM()
        
        # Valid base_dirs
        valid_base_dirs = {
            "prompts": tmp_path / "prompts",
            "encoded": tmp_path / "encoded",
            "outputs": tmp_path / "outputs"
        }
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=valid_base_dirs
        )
        
        assert runner.base_dirs == valid_base_dirs
    
    def test_prompt_runner_stores_exam_date(self, tmp_path):
        """PromptRunner MUST store exam_date correctly."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        exam_dates = ["rcm6_2024_08", "test_exam", "exam_2023"]
        
        for exam_date in exam_dates:
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=False,
                exam_date=exam_date,
                base_dirs=base_dirs
            )
            
            assert runner.exam_date == exam_date


class TestPromptRunnerErrorHandling:
    """Test PromptRunner error handling requirements."""
    
    def test_prompt_runner_handles_model_errors(self, tmp_path):
        """run() SHOULD handle model query errors appropriately."""
        class ErrorModel(LLMInterface):
            def query(self, input: PromptInput) -> str:
                raise Exception("Model API error")
        
        error_model = ErrorModel()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        with patch.object(PromptRunner, '_load_system_prompt', return_value="System"), \
             patch.object(PromptRunner, '_load_base_format_prompt', return_value="Format"), \
             patch.object(PromptRunner, '_load_encoded', return_value="Data"), \
             patch.object(PromptRunner, '_load_question', return_value="Question"), \
             patch.object(PromptRunner, '_load_guides', return_value=[]):
            
            runner = PromptRunner(
                model=error_model,
                question_number="Q1b",
                datatype="abc",
                context=False,
                exam_date="test_exam",
                base_dirs=base_dirs
            )
            
            # Should propagate model errors
            with pytest.raises(Exception, match="Model API error"):
                runner.run()
    
    def test_prompt_runner_handles_file_loading_errors(self, tmp_path):
        """run() SHOULD handle file loading errors appropriately."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs
        )
        
        # Mock file loading error
        with patch.object(runner, '_load_system_prompt', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                runner.run()


class TestPromptRunnerOutputContract:
    """Test PromptRunner output handling requirements."""
    
    def test_prompt_runner_configures_save_path_correctly(self, tmp_path):
        """PromptRunner MUST configure save path correctly when save=True."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        # Mock get_output_path to return a predictable path
        expected_path = tmp_path / "test_output.txt"
        with patch('llm_music_theory.core.runner.get_output_path', return_value=expected_path):
            runner = PromptRunner(
                model=mock_model,
                question_number="Q1b",
                datatype="abc",
                context=True,
                exam_date="test_exam",
                base_dirs=base_dirs,
                save=True
            )
            
            assert runner.save_to == expected_path
    
    def test_prompt_runner_no_save_path_when_save_false(self, tmp_path):
        """PromptRunner MUST NOT configure save path when save=False."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs,
            save=False
        )
        
        assert runner.save_to is None


class TestPromptRunnerDefaultValues:
    """Test PromptRunner default parameter handling."""
    
    def test_prompt_runner_default_temperature(self, tmp_path):
        """PromptRunner SHOULD provide reasonable temperature default."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs
            # No temperature specified
        )
        
        assert hasattr(runner, 'temperature')
        assert isinstance(runner.temperature, (int, float))
        assert 0.0 <= runner.temperature <= 1.0
    
    def test_prompt_runner_default_max_tokens(self, tmp_path):
        """PromptRunner SHOULD handle missing max_tokens gracefully."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs
            # No max_tokens specified
        )
        
        assert hasattr(runner, 'max_tokens')
        assert runner.max_tokens is None
    
    def test_prompt_runner_default_save(self, tmp_path):
        """PromptRunner SHOULD default save to False."""
        mock_model = MockLLM()
        base_dirs = {"prompts": tmp_path, "encoded": tmp_path, "outputs": tmp_path}
        
        runner = PromptRunner(
            model=mock_model,
            question_number="Q1b",
            datatype="abc",
            context=False,
            exam_date="test_exam",
            base_dirs=base_dirs
            # No save specified
        )
        
        assert runner.save is False
        assert runner.save_to is None
