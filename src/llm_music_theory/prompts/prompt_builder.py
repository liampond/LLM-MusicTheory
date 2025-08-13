from typing import List, Optional, Dict, Iterable
from llm_music_theory.models.base import PromptInput


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
        model_name: str = None,
        ordering: Optional[List[str]] = None,
        section_headers: Optional[Dict[str, str]] = None,
    ):
        self.system_prompt = system_prompt
        self.format_prompt = format_specific_user_prompt
        self.encoded_data = encoded_data
        self.guides = guides
        self.question_prompt = question_prompt
        self.temperature = temperature
        self.model_name = model_name
        # Optional custom ordering of components (names map to internal attrs)
        self.ordering = ordering
        self.section_headers = section_headers or {}

    def build_user_prompt(self) -> str:
        """
        Constructs the full user-facing prompt.
        Includes the format-specific intro, encoded file, guides, and question.
        """
        if not self.ordering:
            # Legacy / default ordering retained for backward compatibility
            sections: List[str] = [
                self.format_prompt,
                self.encoded_data,
                *self.guides,
                self.question_prompt,
            ]
            return "\n\n".join(part.strip() for part in sections if part)

        # Mapping from public names to internal data
        component_map: Dict[str, Iterable[str] | str] = {
            "format_prompt": self.format_prompt,
            "encoded_data": self.encoded_data,
            "guides": [g for g in self.guides if g],  # filter None
            "question_prompt": self.question_prompt,
        }

        built_sections: List[str] = []
        for name in self.ordering:
            if name not in component_map:
                continue  # silently skip unknown names
            value = component_map[name]
            header = self.section_headers.get(name)
            def _add(text: str):
                text = text.strip()
                if not text:
                    return
                if header:
                    built_sections.append(f"### {header}\n\n{text}")
                else:
                    built_sections.append(text)
            if isinstance(value, (list, tuple)):
                for v in value:
                    _add(v)
            else:
                _add(value)  # type: ignore[arg-type]

        return "\n\n".join(built_sections)

    def build(self) -> PromptInput:
        """
        Combines all elements into a PromptInput for model querying.
        """
        # Coerce/validate temperature into [0.0, 1.0]
        temp = self.temperature
        if not isinstance(temp, (int, float)):
            raise TypeError("temperature must be a number between 0.0 and 1.0")
        # clamp
        if temp < 0.0 or temp > 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

        return PromptInput(
            system_prompt=self.system_prompt,
            user_prompt=self.build_user_prompt(),
            temperature=float(temp),
            model_name=self.model_name
        )
