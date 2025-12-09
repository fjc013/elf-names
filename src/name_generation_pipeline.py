"""Name generation pipeline orchestrating the complete elf name generation workflow."""

from typing import Tuple
from bedrock_client import BedrockClient
from seed_generator import SeedGenerator
from embedding_generator import EmbeddingGenerator
from llm_name_generator import LLMNameGenerator
from safety_filter import SafetyFilter
from models import UserInput
from exceptions import InputValidationError, NameGenerationError


class NameGenerationPipeline:
    """
    Orchestrates the complete elf name generation workflow.
    
    This pipeline coordinates between seed generation, embedding creation,
    LLM-based name generation, and safety validation to produce family-friendly,
    reproducible Christmas elf names.
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize with BedrockClient and all component dependencies.
        
        Instantiates all required components:
        - SeedGenerator for deterministic seed creation
        - EmbeddingGenerator for semantic embeddings and style hints
        - LLMNameGenerator for name generation
        - SafetyFilter for content validation
        
        Args:
            bedrock_client: BedrockClient instance for AWS Bedrock API access
        
        Requirements: 1.4, 1.5
        """
        self.bedrock_client = bedrock_client
        
        # Instantiate all component dependencies
        self.seed_generator = SeedGenerator()
        self.embedding_generator = EmbeddingGenerator(bedrock_client)
        self.llm_name_generator = LLMNameGenerator(bedrock_client)
        self.safety_filter = SafetyFilter(bedrock_client)

    def generate_elf_name(self, first_name: str, birth_month: str) -> str:
        """
        Main entry point for elf name generation.
        
        Orchestrates the complete workflow:
        1. Validate user input
        2. Generate deterministic seed from user input
        3. Create semantic embedding and convert to style hints
        4. Generate name using LLM with seed and style hints
        5. Validate name through safety filter
        6. Retry if unsafe, with fallback to safe name if needed
        
        Args:
            first_name: User's first name
            birth_month: User's birth month (e.g., "January", "February", etc.)
        
        Returns:
            str: Safe, validated elf name
        
        Raises:
            InputValidationError: If inputs are invalid (empty name or invalid month)
            NameGenerationError: If critical errors occur during generation
        
        Requirements: 1.4, 1.5, 2.5, 2.6
        """
        # Step 1: Input validation using UserInput model
        user_input = UserInput(first_name=first_name, birth_month=birth_month)
        try:
            user_input.validate_or_raise()
        except InputValidationError:
            # Re-raise validation errors as-is
            raise
        
        try:
            # Step 2: Generate deterministic seed from user input
            seed = self.seed_generator.generate_seed(first_name, birth_month)
            
            # Step 3: Create semantic embedding and convert to style hints
            # Combine first name and birth month for embedding
            embedding_text = f"{first_name} {birth_month}"
            embedding = self.embedding_generator.generate_embedding(embedding_text)
            style_hints = self.embedding_generator.embedding_to_style_hints(embedding)
            
            # Step 4: Generate name using LLM with seed and style hints
            generated_name = self.llm_name_generator.generate_name(seed, style_hints)
            
            # Step 5: Validate name through safety filter with retry logic
            # Pass the generator function so safety filter can regenerate if needed
            is_safe, validated_name = self.safety_filter.validate_name(
                name=generated_name,
                generator_func=self.llm_name_generator.generate_name,
                seed=seed,
                style_hints=style_hints
            )
            
            # Step 6: Return the validated name
            # Note: validated_name will be either the original safe name,
            # a regenerated safe name, or a fallback safe name
            return validated_name
            
        except InputValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Wrap other exceptions with context
            raise NameGenerationError(f"Error generating elf name: {str(e)}") from e
