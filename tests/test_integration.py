"""Integration tests against fux-counterpoint dataset only."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.models.base import LLMInterface, PromptInput


class MockLLMForIntegration(LLMInterface):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.query_log = []
        self.response = "Integration test response"

    def query(self, input: PromptInput) -> str:
        self.query_log.append({
            "system_prompt": input.system_prompt,
            "user_prompt": input.user_prompt,
            "temperature": input.temperature,
            "max_tokens": getattr(input, "max_tokens", None)
        })
        return self.response


class TestCLIIntegration:
    @pytest.fixture
    def mock_all_models(self):
        return {name: MockLLMForIntegration(name) for name in ["chatgpt", "claude", "gemini", "deepseek"]}

    @patch.dict(os.environ, {"OPENAI_API_KEY": "x", "ANTHROPIC_API_KEY": "x", "GOOGLE_API_KEY": "x", "DEEPSEEK_API_KEY": "x"})
    def test_prompt_compilation_workflow(self, mock_all_models):
        root = Path(__file__).parent.parent
        data_dir = root / "data" / "fux-counterpoint"
        if not data_dir.exists():
            pytest.skip("fux-counterpoint dataset missing")
        mei_file = data_dir / "encoded" / "mei" / "Fux_CantusFirmus.mei"
        if not mei_file.exists():
            pytest.skip("cantus firmus file missing")
        base_dirs = {
            "encoded": data_dir / "encoded",
            "prompts": data_dir / "prompts",
            "questions": data_dir / "prompts",
            "guides": data_dir / "guides",
            "outputs": root / "outputs",
        }
        llm = mock_all_models["chatgpt"]
        resp = PromptRunner(
            model=llm,
            question_number="Fux_CantusFirmus",
            datatype="mei",
            context=True,
            exam_date="",
            base_dirs=base_dirs,
            temperature=0.0,
            save=False,
        ).run()
        assert resp == "Integration test response"
        assert llm.query_log

    def test_missing_encoded_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_dirs = {k: tmp_path / k for k in ["encoded", "prompts", "guides", "outputs", "questions"]}
            for p in base_dirs.values():
                p.mkdir(parents=True, exist_ok=True)
            class Dummy(LLMInterface):
                def query(self, input: PromptInput) -> str:
                    return "x"
            dummy = Dummy()
            with pytest.raises(FileNotFoundError):
                PromptRunner(
                    model=dummy,
                    question_number="NoFile",
                    datatype="mei",
                    context=False,
                    exam_date="",
                    base_dirs=base_dirs,
                    temperature=0.0,
                    save=False
                ).run()

    def test_missing_question_file(self):
        """Test handling of missing question files."""
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
            
            with pytest.raises(FileNotFoundError):
                runner.run()
