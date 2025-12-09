"""
Unit tests for LLMNameGenerator class.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from llm_name_generator import LLMNameGenerator
from bedrock_client import BedrockClient
from exceptions import NameGenerationError


class TestLLMNameGeneratorInitialization:
    """Tests for LLMNameGenerator initialization."""
    
    def test_successful_initialization(self):
        """Test that LLMNameGenerator initializes with BedrockClient dependency."""
        mock_client = Mock(spec=BedrockClient)
        generator = LLMNameGenerator(mock_client)
        
        assert generator.bedrock_client is mock_client


class TestBuildPrompt:
    """Tests for _build_prompt method."""
    
    def test_build_prompt_with_style_hints(self):
        """Test that prompt includes style hints."""
        mock_client = Mock(spec=BedrockClient)
        generator = LLMNameGenerator(mock_client)
        
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        prompt = generator._build_prompt("abc12345", style_hints)
        
        assert 'cheerful' in prompt
        assert 'winter object' in prompt
        assert 'add sparkle' in prompt
        assert '2 or 3 words' in prompt
        assert 'Christmas' in prompt
    
    def test_build_prompt_includes_safety_constraints(self):
        """Test that prompt includes all safety requirements."""
        mock_client = Mock(spec=BedrockClient)
        generator = LLMNameGenerator(mock_client)
        
        style_hints = {
            'adjective_style': 'bright',
            'noun_style': 'cozy',
            'twist': 'add warmth'
        }
        
        prompt = generator._build_prompt("def67890", style_hints)
        
        # Check for safety constraints (Requirements 2.1, 2.2, 2.3, 2.4)
        assert 'NO political' in prompt
        assert 'NO religious' in prompt
        assert 'NO body part' in prompt
        assert 'NO suggestive' in prompt
        assert 'family-friendly' in prompt
    
    def test_build_prompt_includes_format_requirements(self):
        """Test that prompt specifies format requirements."""
        mock_client = Mock(spec=BedrockClient)
        generator = LLMNameGenerator(mock_client)
        
        style_hints = {
            'adjective_style': 'gentle',
            'noun_style': 'natural',
            'twist': 'add magic'
        }
        
        prompt = generator._build_prompt("12345678", style_hints)
        
        # Check for format requirements (Requirement 3.1)
        assert '2 or 3 words' in prompt
        # Check for pattern examples (Requirement 3.4)
        assert 'Adjective-WinterObject' in prompt or 'PlayfulVerb-CozyNoun' in prompt


class TestGenerateName:
    """Tests for generate_name method."""
    
    def test_generate_name_success(self):
        """Test successful name generation."""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_nova_lite.return_value = "Sparkle Snowflake"
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        name = generator.generate_name("abc12345", style_hints)
        
        assert name == "Sparkle Snowflake"
        assert mock_client.invoke_nova_lite.called
    
    def test_generate_name_with_seed(self):
        """Test that seed is passed to Bedrock client."""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_nova_lite.return_value = "Jolly Tinsel"
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'bright',
            'noun_style': 'cozy',
            'twist': 'add warmth'
        }
        
        name = generator.generate_name("def67890", style_hints)
        
        # Verify seed was passed
        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args[0][1] == "def67890"  # Second argument is seed
    
    def test_generate_name_three_words(self):
        """Test that three-word names are accepted."""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_nova_lite.return_value = "Merry Jingles Peppermint"
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'playful',
            'noun_style': 'candy',
            'twist': 'add mischief'
        }
        
        name = generator.generate_name("12345678", style_hints)
        
        assert name == "Merry Jingles Peppermint"
        assert len(name.split()) == 3
    
    def test_generate_name_handles_empty_response(self):
        """Test retry logic for empty responses."""
        mock_client = Mock(spec=BedrockClient)
        # First call returns empty, second call returns valid name
        mock_client.invoke_nova_lite.side_effect = ["", "Twinkle Cocoa"]
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        name = generator.generate_name("abc12345", style_hints)
        
        assert name == "Twinkle Cocoa"
        assert mock_client.invoke_nova_lite.call_count == 2
    
    def test_generate_name_handles_whitespace_response(self):
        """Test retry logic for whitespace-only responses."""
        mock_client = Mock(spec=BedrockClient)
        # First call returns whitespace, second call returns valid name
        mock_client.invoke_nova_lite.side_effect = ["   ", "Cozy Candlelight"]
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'gentle',
            'noun_style': 'cozy',
            'twist': 'add warmth'
        }
        
        name = generator.generate_name("def67890", style_hints)
        
        assert name == "Cozy Candlelight"
        assert mock_client.invoke_nova_lite.call_count == 2
    
    def test_generate_name_fixes_too_many_words(self):
        """Test that names with more than 3 words are truncated."""
        mock_client = Mock(spec=BedrockClient)
        # Return name with 5 words
        mock_client.invoke_nova_lite.return_value = "Very Merry Sparkly Jingles Snowflake"
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        name = generator.generate_name("12345678", style_hints, max_retries=0)
        
        # Should truncate to first 3 words
        assert name == "Very Merry Sparkly"
        assert len(name.split()) == 3
    
    def test_generate_name_raises_error_for_single_word(self):
        """Test that single-word names raise NameGenerationError after retries."""
        mock_client = Mock(spec=BedrockClient)
        # Always return single word
        mock_client.invoke_nova_lite.return_value = "Sparkle"
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        with pytest.raises(NameGenerationError, match="only 1 word"):
            generator.generate_name("abc12345", style_hints, max_retries=1)
    
    def test_generate_name_raises_error_after_max_retries(self):
        """Test that NameGenerationError is raised after max retries for empty responses."""
        mock_client = Mock(spec=BedrockClient)
        # Always return empty
        mock_client.invoke_nova_lite.return_value = ""
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        with pytest.raises(NameGenerationError, match="Generated name is empty"):
            generator.generate_name("abc12345", style_hints, max_retries=2)
        
        # Should have tried 3 times (initial + 2 retries)
        assert mock_client.invoke_nova_lite.call_count == 3
    
    def test_generate_name_propagates_bedrock_errors(self):
        """Test that Bedrock API errors are propagated."""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_nova_lite.side_effect = Exception("API Error")
        
        generator = LLMNameGenerator(mock_client)
        style_hints = {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
        
        with pytest.raises(Exception, match="API Error"):
            generator.generate_name("abc12345", style_hints, max_retries=1)
