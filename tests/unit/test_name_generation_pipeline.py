"""Unit tests for NameGenerationPipeline."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
# Add tests directory to path for test_data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from name_generation_pipeline import NameGenerationPipeline
from bedrock_client import BedrockClient
from exceptions import InputValidationError
from test_data import FALLBACK_SAFE_NAMES


class TestNameGenerationPipelineInitialization:
    """Test NameGenerationPipeline initialization."""
    
    def test_successful_initialization(self):
        """Test that pipeline initializes with all components."""
        # Create mock Bedrock client
        mock_bedrock = Mock(spec=BedrockClient)
        
        # Initialize pipeline
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        # Verify all components are initialized
        assert pipeline.bedrock_client is mock_bedrock
        assert pipeline.seed_generator is not None
        assert pipeline.embedding_generator is not None
        assert pipeline.llm_name_generator is not None
        assert pipeline.safety_filter is not None
    
    def test_components_use_bedrock_client(self):
        """Test that components are initialized with the Bedrock client."""
        mock_bedrock = Mock(spec=BedrockClient)
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        # Verify components have access to Bedrock client
        assert pipeline.embedding_generator.bedrock_client is mock_bedrock
        assert pipeline.llm_name_generator.bedrock_client is mock_bedrock
        assert pipeline.safety_filter.bedrock_client is mock_bedrock


class TestGenerateElfName:
    """Test generate_elf_name orchestration method."""
    
    def test_generate_elf_name_success(self):
        """Test successful elf name generation."""
        # Create mock Bedrock client
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_bedrock.invoke_nova_lite.side_effect = [
            "Sparkly Snowflake",  # Name generation
            "SAFE"  # Safety check
        ]
        
        # Initialize pipeline
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        # Generate elf name
        result = pipeline.generate_elf_name("Alice", "January")
        
        # Verify result is a string
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_elf_name_with_different_inputs(self):
        """Test that different inputs produce results."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.5, -0.2, 0.1]
        mock_bedrock.invoke_nova_lite.side_effect = [
            "Twinkle Star",
            "SAFE"
        ]
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        result = pipeline.generate_elf_name("Bob", "December")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_elf_name_empty_first_name_raises_error(self):
        """Test that empty first name raises InputValidationError."""
        mock_bedrock = Mock(spec=BedrockClient)
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        with pytest.raises(InputValidationError, match="Please enter your first name"):
            pipeline.generate_elf_name("", "January")
    
    def test_generate_elf_name_whitespace_first_name_raises_error(self):
        """Test that whitespace-only first name raises InputValidationError."""
        mock_bedrock = Mock(spec=BedrockClient)
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        with pytest.raises(InputValidationError, match="Please enter your first name"):
            pipeline.generate_elf_name("   ", "January")
    
    def test_generate_elf_name_invalid_month_raises_error(self):
        """Test that invalid month raises InputValidationError."""
        mock_bedrock = Mock(spec=BedrockClient)
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        with pytest.raises(InputValidationError, match="Invalid birth month"):
            pipeline.generate_elf_name("Alice", "InvalidMonth")
    
    def test_generate_elf_name_calls_all_components(self):
        """Test that generate_elf_name calls all pipeline components."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_bedrock.invoke_nova_lite.side_effect = [
            "Sparkly Snowflake",
            "SAFE"
        ]
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        # Generate name
        result = pipeline.generate_elf_name("Alice", "January")
        
        # Verify Bedrock was called for embedding
        assert mock_bedrock.generate_embedding.called
        
        # Verify Bedrock was called for name generation and safety check
        assert mock_bedrock.invoke_nova_lite.call_count >= 1
    
    def test_generate_elf_name_handles_unsafe_name_with_retry(self):
        """Test that unsafe names trigger retry logic."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_bedrock.invoke_nova_lite.side_effect = [
            "Unsafe Name",  # First generation
            "UNSAFE",  # Safety check fails
            "Safe Name",  # Regeneration
            "SAFE"  # Safety check passes
        ]
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        result = pipeline.generate_elf_name("Alice", "January")
        
        # Should return a safe name (either regenerated or fallback)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_elf_name_uses_fallback_after_max_retries(self):
        """Test that fallback name is used after max retry attempts."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.1, 0.2, 0.3]
        # All safety checks fail
        mock_bedrock.invoke_nova_lite.side_effect = [
            "Unsafe Name 1",
            "UNSAFE",
            "Unsafe Name 2",
            "UNSAFE",
            "Unsafe Name 3",
            "UNSAFE"
        ]
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        result = pipeline.generate_elf_name("Alice", "January")
        
        # Should return a fallback safe name
        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it's one of the fallback names
        assert result in FALLBACK_SAFE_NAMES
    
    def test_generate_elf_name_propagates_critical_errors(self):
        """Test that critical errors are propagated with context."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.side_effect = Exception("Critical error")
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        with pytest.raises(Exception, match="Error generating elf name"):
            pipeline.generate_elf_name("Alice", "January")
    
    def test_generate_elf_name_all_valid_months(self):
        """Test that all valid months are accepted."""
        mock_bedrock = Mock(spec=BedrockClient)
        mock_bedrock.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        pipeline = NameGenerationPipeline(mock_bedrock)
        
        valid_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        for month in valid_months:
            # Reset mock for each iteration
            mock_bedrock.invoke_nova_lite.side_effect = [
                "Test Name",
                "SAFE"
            ]
            
            # Should not raise an error
            result = pipeline.generate_elf_name("Alice", month)
            assert isinstance(result, str)
