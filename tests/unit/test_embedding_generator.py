"""Unit tests for EmbeddingGenerator class."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from embedding_generator import EmbeddingGenerator
from bedrock_client import BedrockClient


class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator class."""
    
    def test_initialization(self):
        """Test that EmbeddingGenerator initializes with BedrockClient."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        assert generator.bedrock_client is mock_client
    
    def test_generate_embedding_calls_bedrock_client(self):
        """Test that generate_embedding delegates to BedrockClient."""
        mock_client = Mock(spec=BedrockClient)
        mock_embedding = [0.1, 0.2, 0.3, -0.1, -0.2]
        mock_client.generate_embedding.return_value = mock_embedding
        
        generator = EmbeddingGenerator(mock_client)
        result = generator.generate_embedding("test text")
        
        mock_client.generate_embedding.assert_called_once_with("test text")
        assert result == mock_embedding
    
    def test_embedding_to_style_hints_with_positive_values(self):
        """Test style hints mapping for positive embedding values (cheerful)."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        # Embedding with positive average
        embedding = [0.5, 0.3, 0.4, 0.2, 0.6]
        style_hints = generator.embedding_to_style_hints(embedding)
        
        assert 'adjective_style' in style_hints
        assert 'noun_style' in style_hints
        assert 'twist' in style_hints
        assert style_hints['adjective_style'] == 'cheerful'
    
    def test_embedding_to_style_hints_with_negative_values(self):
        """Test style hints mapping for negative embedding values (cozy/natural)."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        # Embedding with negative minimum
        embedding = [-0.5, -0.3, 0.1, -0.4, 0.0]
        style_hints = generator.embedding_to_style_hints(embedding)
        
        assert 'adjective_style' in style_hints
        assert 'noun_style' in style_hints
        assert 'twist' in style_hints
        assert style_hints['noun_style'] in ['cozy', 'natural', 'warm']
    
    def test_embedding_to_style_hints_with_medium_range(self):
        """Test style hints mapping for medium range values (playful twist)."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        # Embedding with large range (max - min > 0.5)
        embedding = [0.8, -0.3, 0.2, 0.5, -0.1]
        style_hints = generator.embedding_to_style_hints(embedding)
        
        assert 'twist' in style_hints
        assert style_hints['twist'] in ['add playful twist', 'add sparkle', 'add warmth', 'add magic']
    
    def test_embedding_to_style_hints_with_empty_embedding(self):
        """Test style hints with empty embedding returns defaults."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        style_hints = generator.embedding_to_style_hints([])
        
        assert style_hints == {
            'adjective_style': 'cheerful',
            'noun_style': 'winter object',
            'twist': 'add sparkle'
        }
    
    def test_embedding_to_style_hints_returns_all_required_keys(self):
        """Test that style hints always contains required keys."""
        mock_client = Mock(spec=BedrockClient)
        generator = EmbeddingGenerator(mock_client)
        
        # Test with various embeddings
        test_embeddings = [
            [0.1, 0.2, 0.3],
            [-0.1, -0.2, -0.3],
            [0.0, 0.0, 0.0],
            [0.5, -0.5, 0.0]
        ]
        
        for embedding in test_embeddings:
            style_hints = generator.embedding_to_style_hints(embedding)
            assert 'adjective_style' in style_hints
            assert 'noun_style' in style_hints
            assert 'twist' in style_hints
            assert isinstance(style_hints['adjective_style'], str)
            assert isinstance(style_hints['noun_style'], str)
            assert isinstance(style_hints['twist'], str)
            assert len(style_hints['adjective_style']) > 0
            assert len(style_hints['noun_style']) > 0
            assert len(style_hints['twist']) > 0
