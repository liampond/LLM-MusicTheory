"""PromptRunner orchestrates prompt assembly and LLM querying.

Refactored (Aug 2025) to support new dataset layout (e.g. fux-counterpoint)
while retaining backwards compatibility with legacy RCM style tests & code.
"""

import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.utils.path_utils import (
    load_text_file,
    find_encoded_file,
    find_question_file,
    get_output_path,
)


class PromptRunner:
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
        self.model = model
        # Accept both new (file_id) and legacy (question_number)
        self.file_id = file_id or question_number
        if not self.file_id:
            raise ValueError("file_id (or legacy question_number) is required")
        # Maintain legacy attribute names for tests
        self.question_number = self.file_id
        self.datatype = datatype.lower()
        self.context = context
        # exam_date kept for backward compatibility; dataset is new
        self.exam_date = exam_date or ""
        self.dataset = dataset
        self.base_dirs = base_dirs or {}
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.save = save

        if self.save:
            self.save_to = get_output_path(
                outputs_dir=self.base_dirs.get("outputs", Path("outputs")),
                model_name=type(model).__name__,
                file_id=self.file_id,
                datatype=self.datatype,
                context=self.context,
                dataset=self.dataset,
            )
        else:
            self.save_to = None

    # Public API -----------------------------------------------------------------
    def run(self) -> str:
        prompt_input = self._build_prompt_input()
        # Use f-string so tests that inspect raw log message see substituted values
        self.logger.info(
            f"Running {self.file_id} [{self.datatype}] dataset={self.dataset} context={self.context} temp={self.temperature}"
        )
        response = self.model.query(prompt_input)
        self.logger.info(f"Received response for {self.file_id}")
        if self.save and self.save_to:
            # Persist response
            self._save_response(response)
            # Persist accompanying input bundle (prompts, params, sources)
            try:
                self._save_input_bundle(prompt_input)
            except Exception as e:
                # Do not fail the main run if metadata persistence fails
                self.logger.warning("Failed to write input bundle: %s", e)
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
        builder = PromptBuilder(
            system_prompt=system_prompt,
            format_specific_user_prompt=format_prompt,
            encoded_data=encoded_data,
            guides=guides,
            question_prompt=question_text,
            temperature=self.temperature,
            model_name=None,
        )
        prompt_input = builder.build()
        if self.max_tokens is not None:
            prompt_input.max_tokens = self.max_tokens
        return prompt_input

    def _load_system_prompt(self) -> str:
        system_file = self.base_dirs.get("prompts", Path("")) / "base" / "system_prompt.txt"
        if system_file.exists():
            return load_text_file(system_file)
        return "You are a helpful music theory assistant."

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

    # ------------------------------------------------------------------
    def _save_input_bundle(self, prompt_input: PromptInput) -> None:
        """Write a companion JSON file capturing all prompt inputs & metadata.

        File naming: <base>.input.json next to the response file.
        Contains raw components + derived user prompt + config parameters.
        """
        if not self.save_to:
            return
        bundle_path = self.save_to.with_suffix("")  # strip .txt
        # keep original name, append .input.json
        bundle_path = bundle_path.parent / (bundle_path.name + ".input.json")

        components = getattr(self, "_last_components", {})
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_id": self.file_id,
            "datatype": self.datatype,
            "dataset": self.dataset,
            "context": self.context,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model_class": type(self.model).__name__,
            "model_name_override": prompt_input.model_name,
            "save_to": str(self.save_to),
            "exam_date": self.exam_date,
            "components": {
                **components,
                "user_prompt_compiled": prompt_input.user_prompt,
                "system_prompt": prompt_input.system_prompt,
            },
            "lengths": {
                k: (len(v) if isinstance(v, str) else sum(len(x) for x in v))
                for k, v in components.items()
            },
        }
        # Avoid huge accidental binary dumps: if any component extremely large, note it.
        MAX_INLINE = 200_000  # chars
        for k, v in list(data["components"].items()):
            if isinstance(v, str) and len(v) > MAX_INLINE:
                data["components"][k] = f"<omitted length={len(v)}>"
        bundle_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.logger.info("Saved input bundle to %s", bundle_path)
        self.input_bundle_path = bundle_path
