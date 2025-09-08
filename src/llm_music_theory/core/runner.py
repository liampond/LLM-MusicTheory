"""PromptRunner orchestrates prompt assembly and LLM querying.

Responsibilities:
    * Load the appropriate system/base format prompts, encoded data, guides, and question text.
    * Build a `PromptInput` via `PromptBuilder` with dataset‑specific ordering.
    * Invoke the provided model (`LLMInterface`) and optionally persist response + metadata bundle.

Non‑goals:
    * Network retries / rate limiting (leave to model wrapper).
    * Complex caching (could be layered later if needed).

Backward compatibility:
    * Retains support for legacy parameter names (`question_number`, `exam_date`).
    * Maintains existing attribute names used by tests (e.g. `question_number`).
"""

import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.utils.path_utils import (
    load_text_file,
    find_encoded_file,
    find_question_file,
    get_output_path,
)


class PromptRunner:
    """Build and execute a single prompt run.

    Instances are lightweight; create a new runner per prompt.
    """

    _EXT_MAP = {"mei": ".mei", "musicxml": ".musicxml", "abc": ".abc", "humdrum": ".krn"}

    def __init__(
        self,
        model: LLMInterface,
        file_id: Optional[str] = None,
        datatype: str = "mei",
        context: bool = False,
        dataset: str = "fux-counterpoint",
        base_dirs: Optional[Dict[str, Path]] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        save: bool = False,
        # Legacy aliases
        question_number: Optional[str] = None,
        exam_date: Optional[str] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.model: LLMInterface = model
        # Accept both new (file_id) and legacy (question_number)
        self.file_id: str = file_id or question_number or ""
        if not self.file_id:
            raise ValueError("file_id (or legacy question_number) is required")
            raise ValueError("file_id (or legacy question_number) is required")
        # Maintain legacy attribute names for tests
        self.question_number: str = self.file_id
        self.datatype: str = datatype.lower().strip()
        if self.datatype not in self._EXT_MAP:
            self.logger.warning("Unrecognized datatype '%s'; proceeding anyway", self.datatype)
        self.context: bool = bool(context)
        # exam_date kept for backward compatibility; dataset is new
        self.exam_date: str = exam_date or ""
        self.dataset: str = dataset
        self.base_dirs: Dict[str, Path] = base_dirs or {}
        self.temperature: float = float(temperature)
        if not (0.0 <= self.temperature <= 1.0):  # soft validation
            self.logger.warning("Temperature %.3f outside [0,1]; model may clamp internally", self.temperature)
        self.max_tokens: Optional[int] = max_tokens
        self.save: bool = bool(save)

        self.save_to: Optional[Path] = None
        if self.save:
            try:
                # Use the same extension as the input encoded file
                ext = f".{self.datatype}"
                self.save_to = get_output_path(
                    outputs_dir=self.base_dirs.get("outputs", Path("outputs")),
                    model_name=type(model).__name__,
                    file_id=self.file_id,
                    datatype=self.datatype,
                    context=self.context,
                    dataset=self.dataset,
                    ext=ext,
                )
            except Exception as e:  # pragma: no cover (rare path issues)
                self.logger.error("Failed to compute output path: %s", e)
                self.save_to = None

    # Public API -----------------------------------------------------------------
    def run(self) -> str:
        """Execute the prompt build + model query pipeline.

        Returns
        -------
        str
            Raw response text from the underlying model.
        """
        prompt_input = self._build_prompt_input()
        self.logger.info(
            f"Running {self.file_id} [{self.datatype}] dataset={self.dataset} context={self.context} temp={self.temperature}"
        )
        response = self.model.query(prompt_input)
        # Use f-string to match test expectation that the interpolated id appears directly
        self.logger.info(f"Received response for {self.file_id}")
        if self.save and self.save_to:
            self._persist_artifacts(response, prompt_input)
        return response

    # Internal helpers -----------------------------------------------------------
    def _build_prompt_input(self) -> PromptInput:
        system_prompt = self._load_system_prompt()
        format_prompt = self._load_base_format_prompt()
        encoded_data = self._load_encoded()
        question_text = self._load_question()
        guides = self._load_guides()
        # Stash raw components for later logging
        self._last_components = {
            "system_prompt": system_prompt,
            "format_prompt": format_prompt,
            "encoded_data": encoded_data,
            "guides": guides,
            "question_prompt": question_text,
        }
        # Dataset-specific ordering logic. For the new fux-counterpoint dataset
        # the user requested ordering: prompt.md (question), guides, base_<FORMAT>, encoded file.
        # Legacy datasets retain previous ordering.
        ordering = None
        section_headers = None
        if self.dataset == "fux-counterpoint":
            ordering = [
                "question_prompt",  # prompt.md baseline instructions
                "guides",  # contextual guide(s)
                "format_prompt",  # base_format instructions
                "encoded_data",  # the score / encoded file
            ]
            section_headers = {
                "question_prompt": "Task",
                "guides": "Guide",
                "format_prompt": f"Output Format ({self.datatype.upper()})",
                "encoded_data": f"Encoded {self.datatype.upper()} Source",
            }

        builder = PromptBuilder(
            system_prompt=system_prompt,
            format_specific_user_prompt=format_prompt,
            encoded_data=encoded_data,
            guides=guides,
            question_prompt=question_text,
            temperature=self.temperature,
            model_name=None,
            ordering=ordering,
            section_headers=section_headers,
        )
        prompt_input = builder.build()
        if self.max_tokens is not None:
            prompt_input.max_tokens = self.max_tokens
        return prompt_input

    def _load_system_prompt(self) -> str:
        """Return empty system prompt since we don't use system_prompt.txt files.
        
        Format-specific prompts in base_{datatype}.md handle all necessary instructions.
        """
        return ""

    def _load_base_format_prompt(self) -> str:
        base_dir = self.base_dirs.get("prompts", Path("")) / "base"
        for ext in ("md", "txt"):
            candidate = base_dir / f"base_{self.datatype}.{ext}"
            if candidate.exists():
                return load_text_file(candidate)
        raise FileNotFoundError(f"Base format prompt not found for {self.datatype} in {base_dir}")

    def _load_encoded(self) -> str:
        # New layout first: encoded/<datatype>/<file_id>.<ext>
        new_dir = self.base_dirs.get("encoded", Path("encoded")) / self.datatype
        path = find_encoded_file(self.file_id, self.datatype, new_dir, required=False)
        if path:
            return load_text_file(path)
        # Legacy with exam_date subfolder: encoded/<exam_date>/<datatype>/<file_id>.<ext>
        if self.exam_date:
            legacy_exam_dir = self.base_dirs.get("encoded", Path("encoded")) / self.exam_date / self.datatype
            path = find_encoded_file(self.file_id, self.datatype, legacy_exam_dir, required=False)
            if path:
                return load_text_file(path)
        # Plain legacy: encoded/<datatype>/<file_id>.<ext>
        legacy_plain = self.base_dirs.get("encoded", Path("encoded")) / self.datatype
        path = find_encoded_file(self.file_id, self.datatype, legacy_plain, required=True)
        if not path:
            raise FileNotFoundError(f"Encoded file not found: {self.file_id}.{self._EXT_MAP.get(self.datatype, '')} in {legacy_plain}")
        return load_text_file(path)

    def _load_question(self) -> str:
        # New dataset single prompt.md
        single_prompt = self.base_dirs.get("prompts", Path("")) / "prompt.md"
        if single_prompt.exists():
            return load_text_file(single_prompt)
        # Legacy per-question naming.
        suffix = "context" if self.context else "no_context"
        legacy_dir = self.base_dirs.get("prompts", Path("")) / "questions" / suffix / self.datatype
        path = find_question_file(self.file_id, self.context, legacy_dir, required=True)
        if not path:
            raise FileNotFoundError(f"Question file not found for {self.file_id} in {legacy_dir}")
        return load_text_file(path)

    def _load_guides(self) -> List[str]:
        guides_dir = self.base_dirs.get("guides", Path("guides"))
        collected: List[str] = []
        if self.context and guides_dir.exists():
            for f in sorted(guides_dir.iterdir()):
                if f.is_file() and f.suffix in {".txt", ".md"}:
                    collected.append(load_text_file(f))
        return collected

    def _save_response(self, response: str) -> None:
        if not self.save_to:
            return
        self.save_to.parent.mkdir(parents=True, exist_ok=True)
        self.save_to.write_text(response, encoding="utf-8")
        self.logger.info("Saved response to %s", self.save_to)

    def _persist_artifacts(self, response: str, prompt_input: PromptInput) -> None:
        """Persist response & prompt file (best effort)."""
        try:
            self._save_response(response)
        except Exception as e:  # pragma: no cover
            self.logger.warning("Failed to save response: %s", e)
        try:
            self._save_prompt_file(prompt_input)
        except Exception as e:  # pragma: no cover
            self.logger.warning("Failed to write prompt file: %s", e)

    # ------------------------------------------------------------------
    def _save_prompt_file(self, prompt_input: PromptInput) -> None:
        """Write a companion .prompt.txt file with metadata and complete prompt.

        File naming: <base>.prompt.txt next to the response file.
        Contains metadata header + system prompt + user prompt with all formatting preserved.
        """
        if not self.save_to:
            return
        prompt_path = self.save_to.with_suffix("")  # strip extension
        prompt_path = prompt_path.parent / (prompt_path.name + ".prompt.txt")

        # Build metadata section
        timestamp = datetime.now(timezone.utc).isoformat()
        components = getattr(self, "_last_components", {})
        
        metadata_lines = [
            "=== MODEL PARAMETERS ===",
            f"Timestamp: {timestamp}",
            f"File: {self.file_id}",
            f"Dataset: {self.dataset}",
            f"Datatype: {self.datatype}",
            f"Context: {'context' if self.context else 'nocontext'}",
            f"Model: {type(self.model).__name__}",
            f"Temperature: {self.temperature}",
            f"Max Tokens: {self.max_tokens}",
            f"Save Path: {self.save_to}",
        ]
        
        if prompt_input.model_name:
            metadata_lines.append(f"Model Name Override: {prompt_input.model_name}")
        if self.exam_date:
            metadata_lines.append(f"Exam Date: {self.exam_date}")
            
        # Add component lengths for reference
        if components:
            metadata_lines.append("")
            metadata_lines.append("Component Lengths:")
            for k, v in components.items():
                length = len(v) if isinstance(v, str) else sum(len(x) for x in v if x)
                metadata_lines.append(f"  {k}: {length} chars")

        # Build complete prompt file content
        content_parts = ["\n".join(metadata_lines)]
        
        if prompt_input.system_prompt and prompt_input.system_prompt.strip():
            content_parts.extend([
                "",
                "=== SYSTEM PROMPT ===",
                prompt_input.system_prompt.strip()
            ])
        
        content_parts.extend([
            "",
            "=== USER PROMPT ===",
            prompt_input.user_prompt
        ])
        
        full_content = "\n".join(content_parts)
        prompt_path.write_text(full_content, encoding="utf-8")
        self.logger.info("Saved prompt file to %s", prompt_path)
        self.prompt_file_path = prompt_path
