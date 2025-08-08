# core/runner.py

import logging
from pathlib import Path
from typing import Dict, List, Optional
from importlib import resources

from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.utils.path_utils import (
    load_text_file,
    find_encoded_file,
    find_question_file,
    list_guides,
    get_output_path,
)


class PromptRunner:
    """
    Orchestrates loading of prompt components, building the prompt,
    querying the LLM, and optionally saving the response.
    """

    # extension mapping for fallback
    _EXT_MAP = {
        "mei":      ".mei",
        "musicxml": ".musicxml",
        "abc":      ".abc",
        "humdrum":  ".krn",
    }

    def __init__(
        self,
        model: LLMInterface,
        question_number: str,
        datatype: str,
        context: bool,
        exam_date: str,
        base_dirs: Dict[str, Path],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        save: bool = False,
    ):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.question_number = question_number
        self.datatype = datatype.lower()
        self.context = context
        self.exam_date = exam_date  # e.g. "rcm6_2024_08"
        self.base_dirs = base_dirs
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.save = save

        if save:
            self.save_to = get_output_path(
                outputs_dir=base_dirs["outputs"],
                model_name=type(model).__name__,
                question_number=question_number,
                datatype=self.datatype,
                context=context,
            )
        else:
            self.save_to = None

    def run(self) -> str:
        prompt_input = self._build_prompt_input()
        self.logger.info(
            f"Running {self.question_number} [{self.datatype}] "
            f"context={self.context} temp={self.temperature}"
        )
        response = self.model.query(prompt_input)
        self.logger.info(f"Received response for {self.question_number}")

        if self.save and self.save_to:
            self._save_response(response)

        return response

    def _build_prompt_input(self) -> PromptInput:
        # 1. Load system & base-format prompt
        system_prompt = self._load_system_prompt()
        format_prompt = self._load_base_format_prompt()

        # 2. Encoded music (external → package)
        encoded_data = self._load_encoded()

        # 3. Question text (external → package)
        question_text = self._load_question()

        # 4. Guides (external → package)
        guides = self._load_guides()

        # 5. Assemble
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

        # 6. max_tokens override
        if self.max_tokens is not None:
            prompt_input.max_tokens = self.max_tokens

        return prompt_input

    def _load_system_prompt(self) -> str:
        """
        Load system prompt from external data directory.
        """
        ext = self.base_dirs["prompts"] / "base" / "system_prompt.txt"
        if ext.exists():
            return load_text_file(ext)
        raise FileNotFoundError(f"System prompt not found at {ext}")

    def _load_base_format_prompt(self) -> str:
        """
        Load base format prompt from external data directory.
        """
        filename = f"base_{self.datatype}.txt"
        ext = self.base_dirs["prompts"] / "base" / filename
        if ext.exists():
            return load_text_file(ext)
        raise FileNotFoundError(f"Base format prompt not found at {ext}")

    def _load_encoded(self) -> str:
        """
        Load encoded music file from external data directory.
        """
        # External path includes exam_date
        ext_dir = self.base_dirs["encoded"] / self.exam_date / self.datatype
        ext_path = find_encoded_file(
            question_number=self.question_number,
            datatype=self.datatype,
            encoded_dir=ext_dir,
            required=False
        )
        if ext_path:
            return load_text_file(ext_path)

        # Try without exam_date subdirectory (legacy structure)
        ext_dir = self.base_dirs["encoded"] / self.datatype
        ext_path = find_encoded_file(
            question_number=self.question_number,
            datatype=self.datatype,
            encoded_dir=ext_dir,
            required=True
        )
        return load_text_file(ext_path)

    def _load_question(self) -> str:
        """
        External first (data/prompts/{exam_date}/{context|no_context}/{datatype}/…),
        then fallback to package prompts/questions/{context|no_context}/{datatype}/….
        """
        suffix = "context" if self.context else "no_context"
        
        # External path structure differs for context vs no_context
        if self.context:
            # Context files are organized by datatype: data/prompts/{exam_date}/context/{datatype}/
            questions_dir = self.base_dirs["prompts"] / self.exam_date / suffix / self.datatype
        else:
            # No context files are all in one directory: data/prompts/{exam_date}/no_context/
            questions_dir = self.base_dirs["prompts"] / self.exam_date / suffix
        
        ext_q = find_question_file(
            question_number=self.question_number,
            context=self.context,
            questions_dir=questions_dir,
            required=False
        )
        if ext_q:
            return load_text_file(ext_q)

        # Fallback to direct directory structure (legacy)
        pkg_dir = self.base_dirs["prompts"] / "questions" / suffix / self.datatype
        ext_q = find_question_file(
            question_number=self.question_number,
            context=self.context,
            questions_dir=pkg_dir,
            required=True
        )
        return load_text_file(ext_q)

    def _load_guides(self) -> List[str]:
        """
        Load guides from external data directory.
        """
        guides_list: List[str] = []
        ext_dir = self.base_dirs["guides"]
        if self.context and ext_dir.exists():
            for guide_name in list_guides(ext_dir):
                guides_list.append(load_text_file(ext_dir / f"{guide_name}.txt"))
        return guides_list

    def _save_response(self, response: str) -> None:
        """
        Persist the model's response to disk.
        """
        self.save_to.parent.mkdir(parents=True, exist_ok=True)
        self.save_to.write_text(response, encoding="utf-8")
        self.logger.info(f"Saved response to {self.save_to}")
