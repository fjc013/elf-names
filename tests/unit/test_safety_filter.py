"""
Unit tests for SafetyFilter class.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from safety_filter import SafetyFilter, FALLBACK_SAFE_NAMES


class TestSafetyFilterInitialization:
    """Tests for SafetyFilter initialization."""
    
    def test_successful_initialization(self):
        """Test that SafetyFilter initializes successfully with BedrockClient."""
        mock_bedrock_client = Mock()
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        
        assert safety_filter.bedrock_client is not None
        assert safety_filter.bedrock_client == mock_bedrock_client
    
    def test_fallback_names_exist(self):
        """Test that fallback safe names list is defined."""
        mock_bedrock_client = Mock()
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        
        assert len(FALLBACK_SAFE_NAMES) > 0
        assert all(isinstance(name, str) for name in FALLBACK_SAFE_NAMES)


class TestCheckSafety:
    """Tests for _check_safety method."""
    
    def test_safe_name_returns_true(self):
        """Test that a safe Christmas-themed name returns True."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "SAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Sparkly Snowflake")
        
        assert result is True
        assert mock_bedrock_client.invoke_nova_lite.called
    
    def test_unsafe_name_returns_false(self):
        """Test that an unsafe name returns False."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Inappropriate Name")
        
        assert result is False
    
    def test_safe_response_with_extra_text(self):
        """Test that response containing SAFE (with extra text) is handled correctly."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "The name is SAFE for children"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Jolly Gingerbread")
        
        assert result is True
    
    def test_unsafe_response_with_extra_text(self):
        """Test that response containing UNSAFE (with extra text) is handled correctly."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "This is UNSAFE content"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Bad Name")
        
        assert result is False
    
    def test_unclear_response_returns_false(self):
        """Test that unclear response errs on the side of caution (returns False)."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "Maybe okay"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Unclear Name")
        
        assert result is False
    
    def test_exception_returns_false(self):
        """Test that exception during safety check returns False (fail-safe)."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.side_effect = Exception("API Error")
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Any Name")
        
        assert result is False
    
    def test_case_insensitive_safe_check(self):
        """Test that safety check is case-insensitive."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "safe"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        result = safety_filter._check_safety("Twinkle Star")
        
        assert result is True


class TestValidateName:
    """Tests for validate_name method."""
    
    def test_safe_name_passes_validation(self):
        """Test that a safe name passes validation on first attempt."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "SAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name("Sparkly Snowflake")
        
        assert is_safe is True
        assert validated_name == "Sparkly Snowflake"
    
    def test_unsafe_name_with_successful_regeneration(self):
        """Test that unsafe name triggers regeneration and succeeds."""
        mock_bedrock_client = Mock()
        # First call: unsafe, second call: safe
        mock_bedrock_client.invoke_nova_lite.side_effect = ["UNSAFE", "SAFE"]
        
        mock_generator = Mock(return_value="Jolly Tinsel")
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            generator_func=mock_generator,
            seed="abc12345",
            style_hints={'adjective_style': 'cheerful'}
        )
        
        assert is_safe is True
        assert validated_name == "Jolly Tinsel"
        assert mock_generator.called
    
    def test_unsafe_name_uses_fallback_after_max_attempts(self):
        """Test that fallback name is used after max retry attempts."""
        mock_bedrock_client = Mock()
        # All attempts return unsafe
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        mock_generator = Mock(return_value="Still Bad")
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            generator_func=mock_generator,
            seed="abc12345",
            style_hints={'adjective_style': 'cheerful'}
        )
        
        assert is_safe is False
        assert validated_name in FALLBACK_SAFE_NAMES
    
    def test_fallback_selection_with_seed(self):
        """Test that fallback name is selected deterministically based on seed."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            seed="00000001"
        )
        
        assert is_safe is False
        # Verify it's a fallback name
        assert validated_name in FALLBACK_SAFE_NAMES
        
        # Same seed should give same fallback
        is_safe2, validated_name2 = safety_filter.validate_name(
            "Bad Name",
            seed="00000001"
        )
        assert validated_name == validated_name2
    
    def test_fallback_without_seed(self):
        """Test that fallback works without seed (uses first fallback)."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name("Bad Name")
        
        assert is_safe is False
        assert validated_name == FALLBACK_SAFE_NAMES[0]
    
    def test_validate_without_generator_function(self):
        """Test validation without generator function (no regeneration)."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            seed="abc12345"
        )
        
        assert is_safe is False
        assert validated_name in FALLBACK_SAFE_NAMES
    
    def test_generator_exception_continues_to_fallback(self):
        """Test that generator exception doesn't break validation flow."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        mock_generator = Mock(side_effect=Exception("Generation failed"))
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            generator_func=mock_generator,
            seed="abc12345"
        )
        
        assert is_safe is False
        assert validated_name in FALLBACK_SAFE_NAMES
    
    def test_invalid_seed_uses_first_fallback(self):
        """Test that invalid seed format uses first fallback name."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_nova_lite.return_value = "UNSAFE"
        
        safety_filter = SafetyFilter(mock_bedrock_client)
        is_safe, validated_name = safety_filter.validate_name(
            "Bad Name",
            seed="not-hex"
        )
        
        assert is_safe is False
        assert validated_name == FALLBACK_SAFE_NAMES[0]
