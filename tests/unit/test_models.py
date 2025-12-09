"""Unit tests for data models."""

import pytest
from src.models import UserInput, StyleHints, GenerationContext, ElfName


class TestUserInput:
    """Tests for UserInput dataclass."""
    
    def test_valid_input(self):
        """Test that valid input passes validation."""
        user_input = UserInput(first_name="Alice", birth_month="January")
        assert user_input.validate() is True
    
    def test_empty_name(self):
        """Test that empty name fails validation."""
        user_input = UserInput(first_name="", birth_month="January")
        assert user_input.validate() is False
    
    def test_whitespace_only_name(self):
        """Test that whitespace-only name fails validation."""
        user_input = UserInput(first_name="   ", birth_month="January")
        assert user_input.validate() is False
    
    def test_invalid_month(self):
        """Test that invalid month fails validation."""
        user_input = UserInput(first_name="Alice", birth_month="InvalidMonth")
        assert user_input.validate() is False
    
    def test_all_valid_months(self):
        """Test that all 12 months are valid."""
        valid_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        for month in valid_months:
            user_input = UserInput(first_name="Alice", birth_month=month)
            assert user_input.validate() is True


class TestStyleHints:
    """Tests for StyleHints dataclass."""
    
    def test_from_embedding_positive_values(self):
        """Test style hints from embedding with positive values."""
        embedding = [0.5, 0.3, 0.4, 0.6]
        hints = StyleHints.from_embedding(embedding)
        
        assert hints.adjective_style == "cheerful"
        assert isinstance(hints.noun_style, str)
        assert isinstance(hints.twist, str)
    
    def test_from_embedding_negative_values(self):
        """Test style hints from embedding with negative values."""
        embedding = [-0.5, -0.3, -0.4, -0.2]
        hints = StyleHints.from_embedding(embedding)
        
        assert hints.adjective_style == "gentle"
        assert isinstance(hints.noun_style, str)
        assert isinstance(hints.twist, str)
    
    def test_from_embedding_mixed_values(self):
        """Test style hints from embedding with mixed values."""
        embedding = [0.1, -0.1, 0.05, -0.05]
        hints = StyleHints.from_embedding(embedding)
        
        assert hints.adjective_style == "playful"
        assert isinstance(hints.noun_style, str)
        assert isinstance(hints.twist, str)
    
    def test_from_embedding_empty(self):
        """Test style hints from empty embedding."""
        embedding = []
        hints = StyleHints.from_embedding(embedding)
        
        assert hints.adjective_style == "cheerful"
        assert hints.noun_style == "winter object"
        assert hints.twist == "add sparkle"
    
    def test_style_hints_fields(self):
        """Test that StyleHints has required fields."""
        hints = StyleHints(
            adjective_style="cheerful",
            noun_style="winter object",
            twist="add sparkle"
        )
        
        assert hints.adjective_style == "cheerful"
        assert hints.noun_style == "winter object"
        assert hints.twist == "add sparkle"


class TestGenerationContext:
    """Tests for GenerationContext dataclass."""
    
    def test_generation_context_creation(self):
        """Test that GenerationContext can be created with required fields."""
        style_hints = StyleHints(
            adjective_style="cheerful",
            noun_style="winter object",
            twist="add sparkle"
        )
        
        context = GenerationContext(
            seed="abc12345",
            embedding=[0.1, 0.2, 0.3],
            style_hints=style_hints
        )
        
        assert context.seed == "abc12345"
        assert context.embedding == [0.1, 0.2, 0.3]
        assert context.style_hints == style_hints


class TestElfName:
    """Tests for ElfName dataclass."""
    
    def test_elf_name_creation(self):
        """Test that ElfName can be created with required fields."""
        elf_name = ElfName(
            name="Sparkle Snowflake",
            is_safe=True
        )
        
        assert elf_name.name == "Sparkle Snowflake"
        assert elf_name.is_safe is True
        assert elf_name.generation_context is None
    
    def test_elf_name_with_context(self):
        """Test that ElfName can include generation context."""
        style_hints = StyleHints(
            adjective_style="cheerful",
            noun_style="winter object",
            twist="add sparkle"
        )
        
        context = GenerationContext(
            seed="abc12345",
            embedding=[0.1, 0.2, 0.3],
            style_hints=style_hints
        )
        
        elf_name = ElfName(
            name="Sparkle Snowflake",
            is_safe=True,
            generation_context=context
        )
        
        assert elf_name.name == "Sparkle Snowflake"
        assert elf_name.is_safe is True
        assert elf_name.generation_context == context
