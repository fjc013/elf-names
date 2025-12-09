"""Data models for the Elf Name Generator application."""

from dataclasses import dataclass
from typing import Optional
from exceptions import InputValidationError


@dataclass
class UserInput:
    """User input model containing first name and birth month."""
    first_name: str
    birth_month: str
    
    VALID_MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    def validate(self) -> bool:
        """
        Validates that the user input is valid.
        
        Returns:
            bool: True if input is valid, False otherwise
        """
        # Check that first_name is non-empty (not just whitespace)
        if not self.first_name or not self.first_name.strip():
            return False
        
        # Check that birth_month is one of the valid months
        if self.birth_month not in self.VALID_MONTHS:
            return False
        
        return True
    
    def validate_or_raise(self) -> None:
        """
        Validates user input and raises InputValidationError with specific message.
        
        Raises:
            InputValidationError: If validation fails with specific error message
        """
        # Check that first_name is non-empty (not just whitespace)
        if not self.first_name or not self.first_name.strip():
            raise InputValidationError("Please enter your first name")
        
        # Check that birth_month is one of the valid months
        if self.birth_month not in self.VALID_MONTHS:
            raise InputValidationError(
                f"Invalid birth month: {self.birth_month}. "
                f"Please select one of: {', '.join(self.VALID_MONTHS)}"
            )


@dataclass
class StyleHints:
    """Style hints derived from semantic embeddings."""
    adjective_style: str
    noun_style: str
    twist: str
    
    @staticmethod
    def from_embedding(embedding: list[float]) -> 'StyleHints':
        """
        Converts embedding values to style hints.
        
        Args:
            embedding: Vector representation of user input
            
        Returns:
            StyleHints: Style instructions for name generation
        """
        # Calculate statistics from embedding values
        if not embedding:
            # Default style hints if embedding is empty
            return StyleHints(
                adjective_style="cheerful",
                noun_style="winter object",
                twist="add sparkle"
            )
        
        avg_value = sum(embedding) / len(embedding)
        max_value = max(embedding)
        min_value = min(embedding)
        
        # Map positive values to cheerful adjectives
        if avg_value > 0.1:
            adjective_style = "cheerful"
        elif avg_value < -0.1:
            adjective_style = "gentle"
        else:
            adjective_style = "playful"
        
        # Map negative values to cozy/natural nouns
        if min_value < -0.2:
            noun_style = "cozy and natural"
        elif max_value > 0.2:
            noun_style = "bright winter object"
        else:
            noun_style = "winter object"
        
        # Map medium values to playful twists
        mid_range = max_value - min_value
        if mid_range > 0.5:
            twist = "add playful twist"
        elif mid_range < 0.2:
            twist = "add warmth"
        else:
            twist = "add sparkle"
        
        return StyleHints(
            adjective_style=adjective_style,
            noun_style=noun_style,
            twist=twist
        )


@dataclass
class GenerationContext:
    """Context information for name generation."""
    seed: str
    embedding: list[float]
    style_hints: StyleHints


@dataclass
class ElfName:
    """Generated elf name with validation status."""
    name: str
    is_safe: bool
    generation_context: Optional[GenerationContext] = None
