"""
Prompt building and compilation functionality.
"""
from typing import List, Optional
from llm_music_theory.models.base import PromptInput


class PromptBuilder:
    """
    Builds and compiles prompts for music theory questions.
    
    This class takes various prompt components and assembles them into
    a complete prompt that can be sent to LLM models.
    """
    
    def __init__(
        self,
        system_prompt: str,
        format_specific_user_prompt: str,
        encoded_data: str,
        guides: Optional[List[str]] = None,
        question_prompt: str = "",
        temperature: float = 0.0,
        model_name: Optional[str] = None
    ):
        """
        Initialize the PromptBuilder with components.
        
        Args:
            system_prompt: The system prompt for the LLM
            format_specific_user_prompt: Format-specific instructions
            encoded_data: The encoded music data
            guides: Optional list of guide content
            question_prompt: The specific question to ask
            temperature: Temperature setting for the model
            model_name: Name of the model (for compatibility)
        """
        self.system_prompt = system_prompt
        self.format_specific_user_prompt = format_specific_user_prompt
        self.encoded_data = encoded_data
        self.guides = guides or []
        self.question_prompt = question_prompt
        self.temperature = temperature
        self.model_name = model_name
    
    def build_user_prompt(self) -> str:
        """
        Build the complete user prompt from components.
        
        Returns:
            The assembled user prompt string
        """
        parts = []
        
        # Add format-specific instructions
        if self.format_specific_user_prompt:
            parts.append(self.format_specific_user_prompt.strip())
        
        # Add encoded data
        if self.encoded_data:
            parts.append(self.encoded_data.strip())
        
        # Add guides
        for guide in self.guides:
            if guide:
                parts.append(guide.strip())
        
        # Add question
        if self.question_prompt:
            parts.append(self.question_prompt.strip())
        
        return "\n\n".join(parts)
    
    def build(self) -> PromptInput:
        """
        Build complete PromptInput object for LLM.
        
        Returns:
            PromptInput object ready for LLM consumption
        """
        user_prompt = self.build_user_prompt()
        system_prompt = self.system_prompt.strip() if self.system_prompt else ""
        
        return PromptInput(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self.temperature,
            model_name=self.model_name
        )
    
    def build_prompt_input(self) -> PromptInput:
        """
        Alias for build() method for compatibility.
        
        Returns:
            PromptInput object ready for LLM consumption
        """
        return self.build()