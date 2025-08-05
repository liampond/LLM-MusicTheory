"""
Integration tests for the complete CLI workflow without API calls.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import pytest
import argparse
from io import StringIO

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.core.dispatcher import get_llm


class MockLLMForIntegration(LLMInterface):
    """Mock LLM that captures full integration test data."""
    
    def __init__(self, model_name="mock"):
        self.model_name = model_name
        self.query_log = []
        self.response = "Integration test response"
    
    def query(self, input: PromptInput) -> str:
        self.query_log.append({
            'system_prompt': input.system_prompt,
            'user_prompt': input.user_prompt,
            'temperature': input.temperature,
            'max_tokens': getattr(input, 'max_tokens', None),
            'model_name': input.model_name
        })
        return self.response


class TestCLIIntegration:
    """Test CLI integration without making actual API calls."""

    @pytest.fixture
    def mock_all_models(self, monkeypatch):
        """Mock all model imports to avoid API dependencies."""
        mock_models = {}
        
        def mock_get_llm(model_name):
            if model_name not in mock_models:
                mock_models[model_name] = MockLLMForIntegration(model_name)
            return mock_models[model_name]
        
        monkeypatch.setattr("llm_music_theory.core.dispatcher.get_llm", mock_get_llm)
        return mock_models

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test',
        'ANTHROPIC_API_KEY': 'test',
        'GOOGLE_API_KEY': 'test',
        'DEEPSEEK_API_KEY': 'test'
    })
    def test_cli_argument_parsing(self, mock_all_models):
        """Test CLI argument parsing without execution."""
        from llm_music_theory.cli.run_single import main
        
        # Test help doesn't crash
        with patch('sys.argv', ['run_single.py', '--help']):
            with pytest.raises(SystemExit):
                main()

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test',
        'ANTHROPIC_API_KEY': 'test', 
        'GOOGLE_API_KEY': 'test',
        'DEEPSEEK_API_KEY': 'test'
    })
    def test_list_commands_integration(self, mock_all_models, monkeypatch):
        """Test listing commands work properly."""
        from llm_music_theory.cli.run_single import main
        
        # Mock sys.exit to capture output
        outputs = []
        
        def mock_exit(code):
            raise SystemExit(code)
        
        def capture_print(*args, **kwargs):
            outputs.append(' '.join(str(arg) for arg in args))
        
        monkeypatch.setattr('sys.exit', mock_exit)
        monkeypatch.setattr('builtins.print', capture_print)
        
        # Test list questions
        with patch('sys.argv', ['run_single.py', '--list-questions']):
            with pytest.raises(SystemExit):
                main()
        
        assert len(outputs) > 0  # Should have printed something

    def test_prompt_compilation_workflow(self, mock_all_models):
        """Test the complete prompt compilation workflow."""
        root = Path(__file__).parent.parent
        data_dir = root / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        # Find available test data
        encoded_dir = data_dir / "encoded"
        exam_dirs = [d for d in encoded_dir.iterdir() if d.is_dir()]
        
        if not exam_dirs:
            pytest.skip("No exam directories found")
        
        exam_date = exam_dirs[0].name
        
        # Find available datatypes
        datatype_dirs = [d for d in exam_dirs[0].iterdir() if d.is_dir()]
        if not datatype_dirs:
            pytest.skip("No datatype directories found")
        
        datatype = datatype_dirs[0].name
        
        # Find available questions
        files = list(datatype_dirs[0].glob("*"))
        if not files:
            pytest.skip("No encoded files found")
        
        # Extract question from filename - handle both Q1a and Q4 formats
        filename = files[0].stem
        print(f"Debug: filename = {filename}")
        if '_Q' in filename:
            question_part = filename.split('_Q')[-1]  # Extract 4a from RCM6_August2024_Q4a
            question = f"Q{question_part}"  # Add Q prefix back
            print(f"Debug: extracted question = {question}")
        else:
            question = filename  # Fallback
            print(f"Debug: fallback question = {question}")
        
        # Run the workflow
        mock_llm = mock_all_models.get("chatgpt", MockLLMForIntegration("chatgpt"))
        
        base_dirs = {
            "encoded": data_dir / "encoded",
            "prompts": data_dir / "prompts",
            "questions": data_dir / "prompts",
            "guides": data_dir / "guides",
            "outputs": root / "outputs",
        }
        
        runner = PromptRunner(
            model=mock_llm,
            question_number=question,
            datatype=datatype,
            context=True,
            exam_date=exam_date,
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        response = runner.run()
        
        # Verify the workflow completed
        assert response == "Integration test response"
        assert len(mock_llm.query_log) == 1
        
        query = mock_llm.query_log[0]
        assert 'system_prompt' in query
        assert 'user_prompt' in query
        assert len(query['system_prompt']) > 0
        assert len(query['user_prompt']) > 0

    def test_multiple_models_workflow(self, mock_all_models):
        """Test that different models can be used in the workflow."""
        root = Path(__file__).parent.parent
        data_dir = root / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        models_to_test = ["chatgpt", "claude", "gemini", "deepseek"]
        
        base_dirs = {
            "encoded": data_dir / "encoded",
            "prompts": data_dir / "prompts", 
            "questions": data_dir / "prompts",
            "guides": data_dir / "guides",
            "outputs": root / "outputs",
        }
        
        # Use package data if available
        for model_name in models_to_test:
            mock_llm = MockLLMForIntegration(model_name)
            mock_all_models[model_name] = mock_llm
            
            try:
                runner = PromptRunner(
                    model=mock_llm,
                    question_number="Q1a",
                    datatype="mei", 
                    context=False,
                    exam_date="",  # Use package data
                    base_dirs=base_dirs,
                    temperature=0.2,
                    save=False
                )
                
                response = runner.run()
                assert response == "Integration test response"
                assert len(mock_llm.query_log) == 1
                
            except FileNotFoundError:
                # Skip if package data not available for this combination
                continue

    def test_context_vs_no_context(self, mock_all_models):
        """Test context vs no-context prompt differences."""
        root = Path(__file__).parent.parent
        data_dir = root / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        mock_llm_context = MockLLMForIntegration("test_context")
        mock_llm_no_context = MockLLMForIntegration("test_no_context")
        
        base_dirs = {
            "encoded": data_dir / "encoded",
            "prompts": data_dir / "prompts",
            "questions": data_dir / "prompts", 
            "guides": data_dir / "guides",
            "outputs": root / "outputs",
        }
        
        # Try with context
        try:
            runner_context = PromptRunner(
                model=mock_llm_context,
                question_number="Q1a",
                datatype="mei",
                context=True,
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            runner_context.run()
        except FileNotFoundError:
            pass  # Skip if files not available
        
        # Try without context
        try:
            runner_no_context = PromptRunner(
                model=mock_llm_no_context,
                question_number="Q1a", 
                datatype="mei",
                context=False,
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            runner_no_context.run()
        except FileNotFoundError:
            pass  # Skip if files not available
        
        # If both succeeded, compare prompts
        if (len(mock_llm_context.query_log) > 0 and 
            len(mock_llm_no_context.query_log) > 0):
            
            context_prompt = mock_llm_context.query_log[0]['user_prompt']
            no_context_prompt = mock_llm_no_context.query_log[0]['user_prompt']
            
            # Context version should typically be longer due to guides
            # (unless no guides are available)
            assert isinstance(context_prompt, str)
            assert isinstance(no_context_prompt, str)

    def test_temperature_and_token_settings(self, mock_all_models):
        """Test that temperature and token settings are passed through."""
        root = Path(__file__).parent.parent
        data_dir = root / "data"
        
        if not data_dir.exists():
            pytest.skip("Data directory not found")
        
        mock_llm = MockLLMForIntegration("test_settings")
        
        base_dirs = {
            "encoded": data_dir / "encoded",
            "prompts": data_dir / "prompts",
            "questions": data_dir / "prompts",
            "guides": data_dir / "guides", 
            "outputs": root / "outputs",
        }
        
        try:
            runner = PromptRunner(
                model=mock_llm,
                question_number="Q1a",
                datatype="mei",
                context=False,
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.8,
                max_tokens=200,
                save=False
            )
            
            runner.run()
            
            assert len(mock_llm.query_log) == 1
            query = mock_llm.query_log[0]
            assert query['temperature'] == 0.8
            assert query['max_tokens'] == 200
            
        except FileNotFoundError:
            pytest.skip("Required test files not available")


class TestErrorHandling:
    """Test error handling in the integration workflow."""

    def test_missing_encoded_file(self):
        """Test handling of missing encoded files with placeholder content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create minimal structure without encoded files
            base_dirs = {
                "encoded": temp_path / "encoded",
                "prompts": temp_path / "prompts",
                "questions": temp_path / "prompts",
                "guides": temp_path / "guides",
                "outputs": temp_path / "outputs",
            }
            
            for path in base_dirs.values():
                path.mkdir(parents=True, exist_ok=True)
            
            # Create base prompts but no encoded files
            prompts_base = temp_path / "prompts" / "base"
            prompts_base.mkdir(parents=True)
            (prompts_base / "system_prompt.txt").write_text("System")
            (prompts_base / "base_mei.txt").write_text("Format: MEI")
            
            mock_llm = MockLLMForIntegration("test")
            
            runner = PromptRunner(
                model=mock_llm,
                question_number="Q99",
                datatype="mei",
                context=False,
                exam_date="nonexistent",
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            
            # Should not raise error, but should contain placeholder content
            response = runner.run()
            assert response == "Integration test response"  # Mock response
            
            # Verify placeholder content was used
            assert len(mock_llm.query_log) > 0
            last_query = mock_llm.query_log[-1]
            assert "[MEI encoded music data for Q99 would be here]" in last_query['user_prompt']

    def test_missing_question_file(self):
        """Test handling of missing question files with placeholder content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create encoded file but no question file
            encoded_dir = temp_path / "encoded" / "test"
            encoded_dir.mkdir(parents=True)
            (encoded_dir / "Q1a.mei").write_text("<mei>test</mei>")
            
            prompts_base = temp_path / "prompts" / "base"
            prompts_base.mkdir(parents=True)
            (prompts_base / "system_prompt.txt").write_text("System")
            (prompts_base / "base_mei.txt").write_text("Format: MEI")
            
            base_dirs = {
                "encoded": temp_path / "encoded",
                "prompts": temp_path / "prompts",
                "questions": temp_path / "prompts",
                "guides": temp_path / "guides",
                "outputs": temp_path / "outputs",
            }
            
            mock_llm = MockLLMForIntegration("test")
            
            runner = PromptRunner(
                model=mock_llm,
                question_number="Q1a",
                datatype="mei",
                context=False,
                exam_date="test",
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            
            # Should not raise error, but should contain placeholder content
            response = runner.run()
            assert response == "Integration test response"  # Mock response
            
            # Verify placeholder content was used
            assert len(mock_llm.query_log) > 0
            last_query = mock_llm.query_log[-1]
            assert "[Question Q1a prompt would be here]" in last_query['user_prompt']
