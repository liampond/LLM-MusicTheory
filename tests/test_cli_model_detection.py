"""Tests for CLI model name detection functionality."""

import pytest
from unittest.mock import patch, MagicMock
from llm_music_theory.cli.run_single import main


class TestCLIModelDetection:
    """Test CLI model name detection and argument handling."""

    @patch('llm_music_theory.cli.run_single.get_llm_with_model_name')
    @patch('llm_music_theory.cli.run_single.validate_api_key')
    @patch('llm_music_theory.cli.run_single.find_encoded_file')
    def test_model_name_only_gpt(self, mock_find_file, mock_validate, mock_get_llm):
        """Should work with just --model-name for GPT models."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.run.return_value = "Test response"
        mock_get_llm.return_value = mock_model
        mock_find_file.return_value = "test.mei"
        
        # Test CLI with just model-name
        args = [
            "--model-name", "gpt-4o",
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        with patch('llm_music_theory.cli.run_single.PromptRunner') as mock_runner:
            mock_runner_instance = MagicMock()
            mock_runner_instance.run.return_value = "Test response"
            mock_runner.return_value = mock_runner_instance
            
            result = main(args)
            
            # Should succeed
            assert result == 0
            
            # Should call model detection and loading
            mock_get_llm.assert_called_once_with("gpt-4o", "chatgpt")
            mock_validate.assert_called_once_with("chatgpt")

    @patch('llm_music_theory.cli.run_single.get_llm_with_model_name')
    @patch('llm_music_theory.cli.run_single.validate_api_key')
    @patch('llm_music_theory.cli.run_single.find_encoded_file')
    def test_model_name_only_claude(self, mock_find_file, mock_validate, mock_get_llm):
        """Should work with just --model-name for Claude models."""
        # Setup mocks
        mock_model = MagicMock()
        mock_get_llm.return_value = mock_model
        mock_find_file.return_value = "test.mei"
        
        # Test CLI with Claude model name
        args = [
            "--model-name", "claude-3-haiku-20240307",
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        with patch('llm_music_theory.cli.run_single.PromptRunner') as mock_runner:
            mock_runner_instance = MagicMock()
            mock_runner_instance.run.return_value = "Test response"
            mock_runner.return_value = mock_runner_instance
            
            result = main(args)
            
            # Should succeed
            assert result == 0
            
            # Should detect Claude and validate its API key
            mock_get_llm.assert_called_once_with("claude-3-haiku-20240307", "claude")
            mock_validate.assert_called_once_with("claude")

    @patch('llm_music_theory.cli.run_single.get_llm')
    @patch('llm_music_theory.cli.run_single.validate_api_key')
    @patch('llm_music_theory.cli.run_single.find_encoded_file')
    def test_backwards_compatibility_model_only(self, mock_find_file, mock_validate, mock_get_llm):
        """Should still work with just --model for backwards compatibility."""
        # Setup mocks
        mock_model = MagicMock()
        mock_get_llm.return_value = mock_model
        mock_find_file.return_value = "test.mei"
        
        # Test CLI with old-style --model flag
        args = [
            "--model", "claude",
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        with patch('llm_music_theory.cli.run_single.PromptRunner') as mock_runner:
            mock_runner_instance = MagicMock()
            mock_runner_instance.run.return_value = "Test response"
            mock_runner.return_value = mock_runner_instance
            
            result = main(args)
            
            # Should succeed
            assert result == 0
            
            # Should use old-style model loading
            mock_get_llm.assert_called_once_with("claude")
            mock_validate.assert_called_once_with("claude")

    def test_missing_model_arguments(self):
        """Should fail when neither --model nor --model-name is provided."""
        args = [
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        # Should raise SystemExit with code 2 due to missing model arguments
        with pytest.raises(SystemExit) as exc_info:
            main(args)
        
        assert exc_info.value.code == 2

    def test_invalid_model_name_detection(self):
        """Should fail gracefully when model name cannot be detected."""
        args = [
            "--model-name", "unknown-model-xyz",
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        # Should return error code 2 due to model detection error
        result = main(args)
        assert result == 2

    @patch('llm_music_theory.cli.run_single.get_llm_with_model_name')
    @patch('llm_music_theory.cli.run_single.validate_api_key')
    @patch('llm_music_theory.cli.run_single.find_encoded_file')
    def test_explicit_model_overrides_detection(self, mock_find_file, mock_validate, mock_get_llm):
        """When both --model and --model-name provided, --model should take precedence."""
        # Setup mocks
        mock_model = MagicMock()
        mock_get_llm.return_value = mock_model
        mock_find_file.return_value = "test.mei"
        
        # Provide both model and model-name (different providers)
        args = [
            "--model", "claude",  # Explicit Claude
            "--model-name", "gpt-4o",  # GPT model name
            "--file", "Fux_CantusFirmus", 
            "--datatype", "mei",
            "--no-save"
        ]
        
        with patch('llm_music_theory.cli.run_single.PromptRunner') as mock_runner:
            mock_runner_instance = MagicMock()
            mock_runner_instance.run.return_value = "Test response"
            mock_runner.return_value = mock_runner_instance
            
            result = main(args)
            
            # Should succeed
            assert result == 0
            
            # Should use explicit --model (claude) not auto-detected (chatgpt)
            mock_get_llm.assert_called_once_with("gpt-4o", "claude")
            mock_validate.assert_called_once_with("claude")
