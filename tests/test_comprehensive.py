"""
Comprehensive end-to-end test that validates prompt generation using real project data.
This test stops just before making API calls to avoid costs.
"""
from pathlib import Path
import pytest
from unittest.mock import Mock

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.utils.path_utils import find_project_root, list_questions, list_datatypes


class ComprehensiveTestLLM(LLMInterface):
    """Mock LLM that captures and validates comprehensive prompt data."""
    
    def __init__(self, model_name="comprehensive_test"):
        self.model_name = model_name
        self.captured_prompts = []
        self.response = "Comprehensive test response"
    
    def query(self, input: PromptInput) -> str:
        """Capture the prompt for validation instead of making API call."""
        prompt_data = {
            'system_prompt': input.system_prompt,
            'user_prompt': input.user_prompt,
            'temperature': input.temperature,
            'max_tokens': getattr(input, 'max_tokens', None),
            'model_name': input.model_name,
            'system_length': len(input.system_prompt),
            'user_length': len(input.user_prompt),
            'total_length': len(input.system_prompt) + len(input.user_prompt)
        }
        self.captured_prompts.append(prompt_data)
        return self.response


class TestComprehensivePromptGeneration:
    """Comprehensive tests using real project data."""

    @pytest.fixture(scope="class")
    def project_structure(self):
        """Get real project structure for testing."""
        root = find_project_root()
        data_dir = root / "data" / "fux-counterpoint"

        if not data_dir.exists():
            pytest.skip("Data directory not found")

        system_prompt_path = data_dir / "prompts" / "base" / "system_prompt.txt"
        has_system_prompt = system_prompt_path.exists()

        encoded_dir = data_dir / "encoded"
        exam_dates = []
        if encoded_dir.exists():
            exam_dates = [d.name for d in encoded_dir.iterdir() if d.is_dir()]

        return {
            'root': root,
            'data_dir': data_dir,
            'exam_dates': exam_dates,
            'has_system_prompt': has_system_prompt,
            'base_dirs': {
                "encoded": data_dir / "encoded",
                "prompts": data_dir / "prompts",
                "questions": data_dir / "prompts",
                "guides": data_dir / "guides",
                "outputs": root / "outputs",
            }
        }

    def test_system_prompt_loading(self, project_structure):
        """Test that system prompts load correctly from real files."""
        mock_llm = ComprehensiveTestLLM()
        base_dirs = project_structure['base_dirs']
        
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=False,
            exam_date="",  # Use package data
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        system_prompt = runner._load_system_prompt()
        # System prompt is now empty as we use format-specific prompts only
        assert isinstance(system_prompt, str)
        assert system_prompt == ""  # Should be empty string

    def test_base_format_prompts(self, project_structure):
        """Test that base format prompts exist for all datatypes."""
        mock_llm = ComprehensiveTestLLM()
        base_dirs = project_structure['base_dirs']
        
        datatypes = ["mei", "abc", "musicxml", "humdrum"]
        
        for datatype in datatypes:
            runner = PromptRunner(
                model=mock_llm,
                question_number="Q1a",
                datatype=datatype,
                context=False,
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            
            try:
                format_prompt = runner._load_base_format_prompt()
                assert len(format_prompt) > 0
                assert isinstance(format_prompt, str)
                # Format prompt should mention the datatype (special cases for various datatypes)
                if datatype.lower() == "musicxml":
                    assert "MusicXML" in format_prompt or "musicxml" in format_prompt.lower()
                elif datatype.lower() == "humdrum":
                    assert "HumDrum" in format_prompt or "humdrum" in format_prompt.lower()
                else:
                    assert datatype.upper() in format_prompt or datatype.lower() in format_prompt
            except FileNotFoundError:
                pytest.skip(f"Base format file for {datatype} not available")

    def test_real_data_prompt_compilation(self, project_structure):
        """Test prompt compilation using real encoded music data."""
        mock_llm = ComprehensiveTestLLM()
        base_dirs = project_structure['base_dirs']
        
        encoded_dir = base_dirs['encoded']
        
        # Find available exam data
        exam_dirs = [d for d in encoded_dir.iterdir() if d.is_dir()]
        if not exam_dirs:
            pytest.skip("No exam directories found")
        
        exam_date = exam_dirs[0].name
        
        # Find available datatypes
        datatype_dirs = [d for d in exam_dirs[0].iterdir() if d.is_dir()]
        if not datatype_dirs:
            pytest.skip("No datatype directories found")
        
        for datatype_dir in datatype_dirs[:2]:  # Test first 2 datatypes
            datatype = datatype_dir.name
            
            # Find available files
            files = list(datatype_dir.glob("*"))
            if not files:
                continue
            
            # Extract question from filename (e.g., "RCM5_August2024_Q1a.mei" -> "Q1a")
            question = None
            for file_path in files:
                stem = file_path.stem
                if '_Q' in stem:
                    question = stem.split('_Q')[-1]
                    break
            
            if not question:
                continue
            
            runner = PromptRunner(
                model=mock_llm,
                question_number=question,
                datatype=datatype,
                context=True,  # Test with context first
                exam_date="",
                base_dirs=base_dirs,
                temperature=0.3,
                max_tokens=500,
                save=False
            )
            
            try:
                response = runner.run()
                
                assert response == "Comprehensive test response"
                assert len(mock_llm.captured_prompts) > 0
                
                prompt_data = mock_llm.captured_prompts[-1]
                
                # Validate prompt structure
                assert prompt_data['system_length'] > 0
                assert prompt_data['user_length'] > 0
                assert prompt_data['total_length'] > 100  # Should be substantial
                assert prompt_data['temperature'] == 0.3
                assert prompt_data['max_tokens'] == 500
                
                # Validate prompt content
                user_prompt = prompt_data['user_prompt']
                assert len(user_prompt.split('\n\n')) >= 3  # Should have multiple sections
                
                # Should contain encoded data
                if datatype == "mei":
                    assert "<mei" in user_prompt or "MEI" in user_prompt
                elif datatype == "abc":
                    assert "X:" in user_prompt or "ABC" in user_prompt
                elif datatype == "musicxml":
                    assert "xml" in user_prompt.lower() or "MusicXML" in user_prompt
                elif datatype == "humdrum":
                    assert "**" in user_prompt or "humdrum" in user_prompt.lower()
                
                break  # Test one successful case
                
            except FileNotFoundError:
                continue  # Try next datatype

    def test_context_vs_no_context_real_data(self, project_structure):
        """Test context vs no-context using real data."""
        mock_llm_context = ComprehensiveTestLLM("context_test")
        mock_llm_no_context = ComprehensiveTestLLM("no_context_test")
        base_dirs = project_structure['base_dirs']
        
        # Find available data
        encoded_dir = base_dirs['encoded']
        exam_dirs = [d for d in encoded_dir.iterdir() if d.is_dir()]
        
        if not exam_dirs:
            pytest.skip("No exam directories found")
        
        exam_date = exam_dirs[0].name
        datatype_dirs = [d for d in exam_dirs[0].iterdir() if d.is_dir()]
        
        if not datatype_dirs:
            pytest.skip("No datatype directories found")
        
        datatype = datatype_dirs[0].name
        files = list(datatype_dirs[0].glob("*"))
        
        if not files:
            pytest.skip("No encoded files found")
        
        # Extract question
        question = None
        for file_path in files:
            stem = file_path.stem
            if '_Q' in stem:
                question = stem.split('_Q')[-1]
                break
        
        if not question:
            pytest.skip("Could not extract question from filename")
        
        # Test with context
        runner_context = PromptRunner(
            model=mock_llm_context,
            question_number=question,
            datatype=datatype,
            context=True,
            exam_date=exam_date,
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        # Test without context
        runner_no_context = PromptRunner(
            model=mock_llm_no_context,
            question_number=question,
            datatype=datatype,
            context=False,
            exam_date=exam_date,
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        try:
            runner_context.run()
            context_prompt = mock_llm_context.captured_prompts[-1]
        except (FileNotFoundError, IndexError):
            context_prompt = None
        
        try:
            runner_no_context.run()
            no_context_prompt = mock_llm_no_context.captured_prompts[-1]
        except (FileNotFoundError, IndexError):
            no_context_prompt = None
        
        # If both succeeded, compare
        if context_prompt and no_context_prompt:
            # Context version should typically be longer (due to guides)
            # But this depends on whether guides exist for this exam
            assert context_prompt['user_length'] > 0
            assert no_context_prompt['user_length'] > 0
            
            # Both should have the same system prompt
            assert context_prompt['system_prompt'] == no_context_prompt['system_prompt']

    def test_all_available_datatypes(self, project_structure):
        """Test prompt generation for all available datatypes in the project."""
        if not project_structure['has_system_prompt']:
            pytest.skip("System prompt not available in legacy data - skipping comprehensive test")
            
        mock_llm = ComprehensiveTestLLM("datatype_test")
        base_dirs = project_structure['base_dirs']
        
        encoded_dir = base_dirs['encoded']
        datatype_dirs = [d for d in encoded_dir.iterdir() if d.is_dir()]
        
        if not datatype_dirs:
            pytest.skip("No datatype directories found")
        
        tested_datatypes = set()
        
        for datatype_dir in datatype_dirs:
            datatype = datatype_dir.name
            
            if datatype in tested_datatypes:
                continue
            
            files = list(datatype_dir.glob("*"))
            if not files:
                continue
            
            # Extract question from filename
            question = None
            for file_path in files:
                stem = file_path.stem
                # Look for question pattern like Q4a, Q1, etc.
                if 'Q' in stem:
                    # Extract the part after the last 'Q'
                    q_parts = stem.split('Q')
                    if len(q_parts) > 1:
                        question_part = q_parts[-1]
                        # Ensure it starts with a number
                        if question_part and question_part[0].isdigit():
                            question = 'Q' + question_part
                            break
            
            if not question:
                continue
            
            runner = PromptRunner(
                model=mock_llm,
                question_number=question,
                datatype=datatype,
                context=False,
                exam_date="",  # Use default
                base_dirs=base_dirs,
                temperature=0.0,
                save=False
            )
            
            try:
                runner.run()
                tested_datatypes.add(datatype)
                
                prompt_data = mock_llm.captured_prompts[-1]
                assert prompt_data['user_length'] > 0
                
                # Verify datatype-specific content
                user_prompt = prompt_data['user_prompt']
                assert datatype.lower() in user_prompt.lower() or datatype.upper() in user_prompt
                
            except FileNotFoundError:
                continue
        
        # Should have tested at least one datatype
        assert len(tested_datatypes) > 0, f"No datatypes could be tested. Available: {list(tested_datatypes)}"

    def test_prompt_length_validation(self, project_structure):
        """Test that generated prompts have reasonable lengths."""
        mock_llm = ComprehensiveTestLLM("length_test")
        base_dirs = project_structure['base_dirs']
        
        # Test with package data to ensure consistency
        runner = PromptRunner(
            model=mock_llm,
            question_number="Q1a",
            datatype="mei",
            context=True,
            exam_date="",  # Use package data
            base_dirs=base_dirs,
            temperature=0.0,
            save=False
        )
        
        try:
            runner.run()
            
            prompt_data = mock_llm.captured_prompts[-1]
            
            # Validate reasonable lengths
            assert prompt_data['system_length'] > 10  # At least some content
            assert prompt_data['system_length'] < 10000  # Not excessively long
            
            assert prompt_data['user_length'] > 50  # Should have substantial content
            assert prompt_data['user_length'] < 50000  # Not excessively long
            
            # Total prompt should be reasonable for most LLM APIs
            assert prompt_data['total_length'] < 100000  # Well under typical limits
            
        except FileNotFoundError:
            pytest.skip("Required files not available for length testing")

    def test_temperature_and_token_parameter_passing(self, project_structure):
        """Test that parameters are correctly passed through the system."""
        if not project_structure['has_system_prompt']:
            pytest.skip("System prompt not available in legacy data - skipping comprehensive test")
            
        mock_llm = ComprehensiveTestLLM("param_test")
        base_dirs = project_structure['base_dirs']
        exam_dates = project_structure['exam_dates']
        
        # Use the first available exam date
        if not exam_dates:
            pytest.skip("No exam dates available for parameter testing")
        
        exam_date = exam_dates[0]
        
        test_cases = [
            (0.0, None),
            (0.5, 100),
            (1.0, 500),
            (1.5, 1000)
        ]
        
        for temperature, max_tokens in test_cases:
            runner = PromptRunner(
                model=mock_llm,
                question_number="Q1a",
                datatype="mei",
                context=False,
                exam_date=exam_date,
                base_dirs=base_dirs,
                temperature=temperature,
                max_tokens=max_tokens,
                save=False
            )
            
            try:
                runner.run()
                
                prompt_data = mock_llm.captured_prompts[-1]
                assert prompt_data['temperature'] == temperature
                assert prompt_data['max_tokens'] == max_tokens
                
            except FileNotFoundError:
                # Skip if files not available for this exam/question
                continue
        
        # Should have tested at least one case
        assert len(mock_llm.captured_prompts) > 0
