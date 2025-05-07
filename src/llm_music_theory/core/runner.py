# core/runner.py

import logging
from pathlib import Path
from typing import Dict, List, Optional

from llm_music_theory.models.base import LLMInterface, PromptInput
from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.utils.path_utils import (
    load_text_file,
    find_encoded_file,
    find_question_file,
    list_guides,
    ensure_dir,
    get_output_path,
)


class PromptRunner:
    """
    Orchestrates loading of prompt components, building the prompt,
    querying the LLM, and optionally saving the response.
    """

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
        """
        Args:
            model: An instance implementing LLMInterface.
            question_number: e.g. "Q1a"
            datatype: "mei"|"musicxml"|"abc"|"humdrum"
            context: include guides if True
            exam_date: (unused for now) e.g. "August2024"
            base_dirs: {
                "prompts": Path,
                "questions": Path,
                "encoded": Path,
                "guides": Path,
                "outputs": Path
            }
            temperature: sampling temp (0.0–1.0)
            max_tokens: optional response token cap
            save: whether to persist the response to disk
        """
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.question_number = question_number
        self.datatype = datatype.lower()
        self.context = context
        self.exam_date = exam_date
        self.base_dirs = base_dirs
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.save = save

        if self.save:
            self.save_to = get_output_path(
                outputs_dir=base_dirs["outputs"],
                model_name=type(model).__name__,
                question_number=self.question_number,
                datatype=self.datatype,
                context=self.context,
            )
        else:
            self.save_to = None

    def run(self) -> str:
        """
        Build, send prompt, and return response (saving if requested).
        """
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
        """
        Load all components, assemble PromptInput, apply max_tokens override.
        """
        # 1. Resolve paths
        system_path = self.base_dirs["prompts"] / "system_prompt.txt"
        user_prompt_path = (
            self.base_dirs["prompts"]
            / f"AllPromptsUser_{self.datatype.upper()}.txt"
        )
        encoded_path = find_encoded_file(
            question_number=self.question_number,
            datatype=self.datatype,
            encoded_dir=self.base_dirs["encoded"],
        )
        question_path = find_question_file(
            question_number=self.question_number,
            context=self.context,
            questions_dir=self.base_dirs["questions"],
        )

        # 2. Load text content
        system_prompt = load_text_file(system_path)
        format_prompt = load_text_file(user_prompt_path)
        encoded_data = load_text_file(encoded_path)
        question_text = load_text_file(question_path)

        # 3. Load guides if requested
        guides: List[str] = []
        if self.context:
            for guide_name in list_guides(self.base_dirs["guides"]):
                guide_path = self.base_dirs["guides"] / f"{guide_name}.txt"
                guides.append(load_text_file(guide_path))

        # 4. Build the PromptInput
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

        # 5. Apply max_tokens override
        if self.max_tokens is not None:
            prompt_input.max_tokens = self.max_tokens

        return prompt_input

    def _save_response(self, response: str) -> None:
        """
        Persist the model's response to disk.
        """
        self.save_to.parent.mkdir(parents=True, exist_ok=True)
        self.save_to.write_text(response, encoding="utf-8")
        self.logger.info(f"Saved response to {self.save_to}")
