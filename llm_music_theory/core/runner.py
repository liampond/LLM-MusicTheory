from pathlib import Path
from typing import Dict, List

from models.base import LLMInterface
from models.base import PromptInput
from prompts.prompt_builder import PromptBuilder
from utils.path_utils import load_text_file, find_encoded_file


class PromptRunner:
    """
    Loads all prompt components, assembles the full prompt,
    sends it to the model, and returns the response.
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
    ):
        """
        Args:
            model: An instance of a model implementing LLMInterface.
            question_number: e.g., "Q1a"
            datatype: One of "mei", "musicxml", "abc", "humdrum"
            context: Whether to use contextual prompt
            exam_date: e.g., "August2024"
            base_dirs: Dict of required folders: {"prompts": ..., "questions": ..., "encoded": ..., "guides": ...}
            temperature: Sampling temperature (default 0.0 for deterministic results)
        """
        self.model = model
        self.question_number = question_number
        self.datatype = datatype
        self.context = context
        self.exam_date = exam_date
        self.base_dirs = base_dirs
        self.temperature = temperature

    def run(self) -> str:
        """
        Assembles and sends the prompt, returns the LLM's response.
        """
        prompt_input = self._load_all()
        return self.model.query(prompt_input)

    def _load_all(self) -> PromptInput:
        # Define file paths
        system_path = self.base_dirs["prompts"] / "system_prompt.txt"
        user_prompt_path = self.base_dirs["prompts"] / f"AllPromptsUser_{self.datatype.upper()}.txt"
        encoded_path = find_encoded_file(self.question_number, self.datatype, self.base_dirs["encoded"])
        context_mode = "context" if self.context else "nocontext"
        question_path = self.base_dirs["questions"] / f"{self.question_number}.{context_mode}.txt"

        # Load contents
        system_prompt = load_text_file(system_path)
        format_user_prompt = load_text_file(user_prompt_path)
        encoded_data = load_text_file(encoded_path)
        question = load_text_file(question_path)
        guide_texts = self._find_guides()

        # Build full prompt
        builder = PromptBuilder(
            system_prompt=system_prompt,
            format_specific_user_prompt=format_user_prompt,
            encoded_data=encoded_data,
            guides=guide_texts,
            question_prompt=question,
            temperature=self.temperature,
            model_name=None  # You can customize this
        )

        return builder.build()

    def _find_guides(self) -> List[str]:
        """
        Stub: later this can be dynamic per-question.
        """
        guide_path = self.base_dirs["guides"] / "intervals.txt"
        return [load_text_file(guide_path)]
