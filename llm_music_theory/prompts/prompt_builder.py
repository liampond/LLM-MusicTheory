from typing import List
from models.base import PromptInput


class PromptBuilder:
    """
    Assembles all parts of the prompt into a single PromptInput object
    that can be passed to any LLM.
    """

    def __init__(
        self,
        system_prompt: str,
        format_specific_user_prompt: str,
        encoded_data: str,
        guides: List[str],
        question_prompt: str,
        temperature: float = 0.0,
        model_name: str = None
    ):
        self.system_prompt = system_prompt
        self.format_prompt = format_specific_user_prompt
        self.encoded_data = encoded_data
        self.guides = guides
        self.question_prompt = question_prompt
        self.temperature = temperature
        self.model_name = model_name

    def build_user_prompt(self) -> str:
        """
        Constructs the full user-facing prompt.
        Includes the format-specific intro, encoded file, guides, and question.
        """
        sections = [
            self.format_prompt,
            self.encoded_data,
            *self.guides,
            self.question_prompt
        ]
        return "\n\n".join(part.strip() for part in sections if part)

    def build(self) -> PromptInput:
        """
        Combines all elements into a PromptInput for model querying.
        """
        return PromptInput(
            system_prompt=self.system_prompt,
            user_prompt=self.build_user_prompt(),
            temperature=self.temperature,
            model_name=self.model_name
        )
