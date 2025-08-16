from __future__ import annotations

from typing import List, Optional, Dict, Iterable, Sequence, Union
from llm_music_theory.models.base import PromptInput

__all__ = ["PromptBuilder"]


class PromptBuilder:
    """Assemble prompt components into a :class:`PromptInput`.

    Parameters
    ----------
    system_prompt: str | None
        The system / assistant role instruction (can be empty / None; passed through).
    format_specific_user_prompt: str
        Base formatting / style instructions for the target encoding format.
    encoded_data: str
        The raw musical encoding contents (ABC / MEI / MusicXML / etc.).
    guides: Sequence[str | None] | None
        Optional list of contextual guide texts; falsey / None values are ignored.
    question_prompt: str
        The user task / question text.
    temperature: float, default 0.0
        Sampling temperature (validated to [0.0, 1.0]).
    model_name: str | None, default None
        Optional explicit model name override.
    ordering: list[str] | None
        Optional explicit ordering of user prompt sections. Allowed keys:
        ["format_prompt", "encoded_data", "guides", "question_prompt"].
        If omitted, legacy ordering is used (format, encoded, guides*, question).
    section_headers: dict[str, str] | None
        Optional mapping from section key to markdown header label (without ###).
    """

    # Maintain explicit set of section keys for validation/extensibility.
    SECTION_KEYS = ("format_prompt", "encoded_data", "guides", "question_prompt")

    def __init__(
        self,
        system_prompt: Optional[str],
        format_specific_user_prompt: str,
        encoded_data: str,
        guides: Optional[Sequence[Optional[str]]],
        question_prompt: str,
        temperature: float = 0.0,
        model_name: Optional[str] = None,
        ordering: Optional[List[str]] = None,
        section_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.system_prompt: Optional[str] = system_prompt
        self.format_prompt: str = format_specific_user_prompt
        self.encoded_data: str = encoded_data
        # Normalize guides: keep order, drop None/empty after stripping.
        self.guides: List[str] = [
            g.strip() if isinstance(g, str) else g  # type: ignore[arg-type]
            for g in (guides or []) if g
        ]
        self.question_prompt: str = question_prompt
        # Store raw; validation + coercion deferred to build() to satisfy contract tests
        self.temperature = temperature  # type: ignore[assignment]
        self.model_name: Optional[str] = model_name
        # Optional custom ordering (validate subset)
        if ordering and any(o not in self.SECTION_KEYS for o in ordering):
            ordering = [o for o in ordering if o in self.SECTION_KEYS]
        self.ordering: Optional[List[str]] = ordering
        self.section_headers: Dict[str, str] = section_headers or {}

    def build_user_prompt(self) -> str:
        """
        Constructs the full user-facing prompt.
        Includes the format-specific intro, encoded file, guides, and question.
        """
        if not self.ordering:
            # Legacy ordering retained for backward compatibility.
            sections: List[str] = [
                self.format_prompt,
                self.encoded_data,
                *self.guides,
                self.question_prompt,
            ]
            return "\n\n".join(part.strip() for part in sections if part)

        component_map: Dict[str, Union[str, List[str]]] = {
            "format_prompt": self.format_prompt,
            "encoded_data": self.encoded_data,
            "guides": [g for g in self.guides if g],
            "question_prompt": self.question_prompt,
        }

        built_sections: List[str] = []
        for name in self.ordering:
            value = component_map.get(name)
            if value is None:
                continue
            header = self.section_headers.get(name)

            def _add(text: str) -> None:
                txt = text.strip()
                if not txt:
                    return
                if header:
                    built_sections.append(f"### {header}\n\n{txt}")
                else:
                    built_sections.append(txt)

            if isinstance(value, list):
                for v in value:
                    _add(v)
            else:
                _add(value)  # type: ignore[arg-type]

        return "\n\n".join(built_sections)

    def build(self) -> PromptInput:
        """Create the :class:`PromptInput` with validation.

        Raises
        ------
        TypeError
            If temperature is not numeric.
        ValueError
            If temperature outside [0.0, 1.0].
        """
        temp = self.temperature
        if not isinstance(temp, (int, float)):
            raise TypeError("temperature must be a number between 0.0 and 1.0")
        if not (0.0 <= float(temp) <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")
        return PromptInput(
            system_prompt=self.system_prompt or "",
            user_prompt=self.build_user_prompt(),
            temperature=float(temp),
            model_name=self.model_name,
        )
