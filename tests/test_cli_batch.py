
"""
End-result focused tests for CLI batch processing.

These tests validate observable behavior of the CLI and worker without
depending on internal helper functions or implementation details that
aren't part of the public CLI contract.
"""
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from llm_music_theory.cli.run_batch import main, worker, load_project_env


@pytest.mark.unit
@pytest.mark.cli
class TestBatchCLI:
    """Outcome-focused CLI tests aligned with actual implementation."""

    def test_load_project_env_with_env_file(self, temp_project_dir):
        """Loads .env from project root when present."""
        env_file = temp_project_dir / ".env"
        env_file.write_text("API_KEY=test_value\nANOTHER_VAR=another_value")

        with patch("llm_music_theory.cli.run_batch.find_project_root", return_value=temp_project_dir), \
             patch("llm_music_theory.cli.run_batch.load_dotenv") as mock_load_dotenv:
            load_project_env()
            mock_load_dotenv.assert_called_once_with(dotenv_path=env_file)

    def test_worker_runs_prompt_runner_and_returns_true(self, tmp_path, mock_api_keys):
        """worker should instantiate model + PromptRunner and return True on success."""
        dirs = {
            "encoded": tmp_path / "encoded",
            "prompts": tmp_path / "prompts",
            "questions": tmp_path / "prompts" / "questions",
            "guides": tmp_path / "prompts" / "guides",
            "outputs": tmp_path / "outputs",
        }

        task = ("chatgpt", "Q1b", "abc", True, dirs, 0.2, None, True, False)

        with patch("llm_music_theory.cli.run_batch.get_llm") as mock_get_llm, \
             patch("llm_music_theory.cli.run_batch.PromptRunner") as mock_runner_cls:
            mock_get_llm.return_value = Mock()
            mock_runner = Mock()
            mock_runner.save_to = dirs["outputs"] / "dummy.txt"
            mock_runner.run.return_value = "ok"
            mock_runner_cls.return_value = mock_runner

            result = worker(task)

            assert result is True
            mock_runner_cls.assert_called_once()
            mock_runner.run.assert_called_once()

    def test_worker_skips_when_output_exists_and_no_overwrite(self, tmp_path, mock_api_keys):
        """worker should skip running when output already exists and overwrite is False."""
        outputs = tmp_path / "outputs"
        outputs.mkdir(parents=True)
        existing = outputs / "exists.txt"
        existing.write_text("already")

        dirs = {
            "encoded": tmp_path / "encoded",
            "prompts": tmp_path / "prompts",
            "questions": tmp_path / "prompts" / "questions",
            "guides": tmp_path / "prompts" / "guides",
            "outputs": outputs,
        }

        task = ("chatgpt", "Q1b", "abc", True, dirs, 0.0, None, True, False)

        with patch("llm_music_theory.cli.run_batch.get_llm") as mock_get_llm, \
             patch("llm_music_theory.cli.run_batch.PromptRunner") as mock_runner_cls:
            mock_get_llm.return_value = Mock()
            mock_runner = Mock()
            mock_runner.save_to = existing
            mock_runner_cls.return_value = mock_runner

            result = worker(task)

            assert result is True  # skipped is treated as success
            mock_runner.run.assert_not_called()

    def test_worker_handles_runner_exception(self, tmp_path, mock_api_keys):
        """worker should return False when runner.run() raises an error."""
        dirs = {
            "encoded": tmp_path / "encoded",
            "prompts": tmp_path / "prompts",
            "questions": tmp_path / "prompts" / "questions",
            "guides": tmp_path / "prompts" / "guides",
            "outputs": tmp_path / "outputs",
        }

        task = ("chatgpt", "Q1b", "abc", True, dirs, 0.0, None, True, False)

        with patch("llm_music_theory.cli.run_batch.get_llm") as mock_get_llm, \
             patch("llm_music_theory.cli.run_batch.PromptRunner") as mock_runner_cls:
            mock_get_llm.return_value = Mock()
            mock_runner = Mock()
            mock_runner.save_to = dirs["outputs"] / "file.txt"
            mock_runner.run.side_effect = RuntimeError("boom")
            mock_runner_cls.return_value = mock_runner

            assert worker(task) is False

    def _invoke_main(self, argv, list_questions=None, list_datatypes=None, worker_result=True):
        """Helper to run main() with patched dependencies and capture exit code."""
        with patch("llm_music_theory.cli.run_batch.load_project_env"), \
             patch("llm_music_theory.cli.run_batch.list_questions", return_value=list_questions or ["Q1a"]), \
             patch("llm_music_theory.cli.run_batch.list_datatypes", return_value=list_datatypes or ["abc"]), \
             patch("llm_music_theory.cli.run_batch.worker", return_value=worker_result), \
             patch.object(sys, "argv", argv):
            with pytest.raises(SystemExit) as exc:
                main()
            return exc.value.code

    def test_main_success_exit_zero(self):
        """main should exit 0 when all tasks succeed."""
        code = self._invoke_main([
            "run_batch.py", "--models", "chatgpt",
            "--questions", "Q1a", "--datatypes", "abc",
            "--jobs", "1"
        ], worker_result=True)
        assert code == 0

    def test_main_failure_exit_one(self):
        """main should exit 1 when any task fails."""
        code = self._invoke_main([
            "run_batch.py", "--models", "chatgpt",
            "--questions", "Q1a", "--datatypes", "abc",
            "--jobs", "1"
        ], worker_result=False)
        assert code == 1
