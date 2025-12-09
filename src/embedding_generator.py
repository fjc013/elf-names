"""Embedding generation and style hint conversion for elf name generation."""

from typing import Dict
from bedrock_client import BedrockClient


class EmbeddingGenerator:
    """
    Generates semantic embeddings from user input and converts them to style hints.
    
    This component creates embedding vectors using AWS Bedrock and transforms
    those vectors into semantic instructions that guide name generation style.
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize with BedrockClient dependency.
        
        Args:
            bedrock_client: BedrockClient instance for embedding API calls
        """
        self.bedrock_client = bedrock_client
    
    def generate_embedding(self, text: str) -> list[float]:
        """
        Creates embedding vector from input text.
        
        Args:
            text: The text to generate an embedding for
        
        Returns:
            list[float]: Embedding vector as a list of floats
        
        Requirements: 4.4
        """
        return self.bedrock_client.generate_embedding(text)
    
    def embedding_to_style_hints(self, embedding: list[float]) -> Dict[str, str]:
        """
        Converts embedding values to semantic instructions for name style variation.
        
        Maps embedding vector values to style guidance:
        - Positive values -> cheerful adjective style
        - Negative values -> cozy/natural noun style  
        - Medium values -> playful twist additions
        
        Args:
            embedding: Embedding vector as list of floats
        
        Returns:
            Dictionary with keys 'adjective_style', 'noun_style', and 'twist'
        
        Requirements: 4.5, 4.6, 4.7, 4.8
        """
        if not embedding or len(embedding) == 0:
            # Default style hints if embedding is empty
            return {
                'adjective_style': 'cheerful',
                'noun_style': 'winter object',
                'twist': 'add sparkle'
            }
        
        # Calculate statistics from embedding vector
        avg_value = sum(embedding) / len(embedding)
        max_value = max(embedding)
        min_value = min(embedding)
        
        # Map positive values to cheerful adjective style (Requirement 4.6)
        if avg_value > 0.1:
            adjective_style = 'cheerful'
        elif avg_value > 0:
            adjective_style = 'bright'
        elif avg_value > -0.1:
            adjective_style = 'gentle'
        else:
            adjective_style = 'soft'
        
        # Map negative values to cozy/natural noun style (Requirement 4.7)
        if min_value < -0.2:
            noun_style = 'cozy'
        elif min_value < -0.1:
            noun_style = 'natural'
        elif min_value < 0:
            noun_style = 'warm'
        else:
            noun_style = 'winter object'
        
        # Map medium values to playful twist additions (Requirement 4.8)
        mid_range = max_value - min_value
        if mid_range > 0.5:
            twist = 'add playful twist'
        elif mid_range > 0.3:
            twist = 'add sparkle'
        elif mid_range > 0.1:
            twist = 'add warmth'
        else:
            twist = 'add magic'
        
        return {
            'adjective_style': adjective_style,
            'noun_style': noun_style,
            'twist': twist
        }
