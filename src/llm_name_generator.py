"""LLM-based name generator for creating Christmas elf names."""

from typing import Dict, Optional
from bedrock_client import BedrockClient
from exceptions import NameGenerationError


class LLMNameGenerator:
    """
    Generates Christmas elf names using AWS Bedrock Nova 2 Lite model.
    
    This component constructs prompts with Christmas theme constraints,
    style hints from embeddings, and safety requirements, then invokes
    the LLM to generate whimsical, family-friendly elf names.
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize with BedrockClient dependency.
        
        Args:
            bedrock_client: BedrockClient instance for model invocation
        
        Requirements: 3.1, 3.2, 3.4
        """
        self.bedrock_client = bedrock_client
    
    def _build_prompt(self, seed: str, style_hints: Dict[str, str]) -> str:
        """
        Constructs prompt with constraints and style guidance.
        
        The prompt includes:
        - Christmas theme constraints
        - Style hints from embeddings
        - 2-3 word format requirement
        - Pattern examples (Adjective-WinterObject, etc.)
        - Safety constraints (no political, religious, body parts, suggestive content)
        
        Args:
            seed: Deterministic seed for reproducibility
            style_hints: Dictionary with adjective_style, noun_style, and twist keys
        
        Returns:
            str: Complete prompt for LLM
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 3.5
        """
        adjective_style = style_hints.get('adjective_style', 'cheerful')
        noun_style = style_hints.get('noun_style', 'winter object')
        twist = style_hints.get('twist', 'add sparkle')
        
        prompt = f"""Generate a whimsical Christmas elf name following these requirements:

FORMAT:
- The name must be exactly 2 or 3 words
- Follow one of these patterns:
  * Adjective-WinterObject (e.g., "Sparkly Snowflake")
  * PlayfulVerb-CozyNoun (e.g., "Twinkle Cocoa")
  * SillyCharacterName-SeasonalFlair (e.g., "Jingles Peppermint")

STYLE GUIDANCE:
- Use {adjective_style} adjectives
- Use {noun_style} for nouns
- {twist}

CHRISTMAS THEME:
- Use Christmas-themed vocabulary including: snow, light, candy, sparkle, animals, warmth, winter, mischief
- Make it whimsical and playful in tone
- If using invented words, ensure they are readable and pronounceable

SAFETY REQUIREMENTS (CRITICAL):
- NO political references
- NO religious references
- NO body part references
- NO suggestive content
- Must be family-friendly and appropriate for all ages

EXAMPLES:
- Sparkly Snowbell
- Twinkle Cocoa
- Jingles Peppermint
- Cozy Candlelight
- Merry Mittens

Generate ONE elf name that meets all requirements above. Return ONLY the name, nothing else."""
        
        return prompt
    
    def generate_name(self, seed: str, style_hints: Dict[str, str], max_retries: int = 2) -> str:
        """
        Generates elf name using seed for reproducibility and style hints for variation.
        Implements retry logic for empty or malformed responses.
        
        Args:
            seed: Deterministic seed (8-character hex string)
            style_hints: Dictionary with adjective_style, noun_style, and twist keys
            max_retries: Maximum number of retry attempts for empty/malformed responses
        
        Returns:
            str: Generated elf name (2-3 words)
        
        Raises:
            NameGenerationError: If unable to generate valid name after retries
        
        Requirements: 1.4, 1.5, 3.1, 3.2, 3.4
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Build prompt with constraints and style guidance
                prompt = self._build_prompt(seed, style_hints)
                
                # Invoke Bedrock client with prompt and seed for reproducibility
                response = self.bedrock_client.invoke_nova_lite(prompt, seed)
                
                # Parse and clean the response
                name = response.strip()
                
                # Handle empty responses
                if not name:
                    last_error = "Generated name is empty"
                    if attempt < max_retries:
                        # Retry with modified prompt
                        continue
                    else:
                        raise NameGenerationError(
                            f"Unable to generate valid name after {max_retries + 1} attempts: {last_error}"
                        )
                
                # Validate format: should be 2-3 words
                word_count = len(name.split())
                if word_count < 2 or word_count > 3:
                    if attempt < max_retries:
                        # Retry with stricter constraints
                        last_error = f"Generated name has {word_count} words (expected 2-3)"
                        continue
                    else:
                        # Try to fix the format
                        words = name.split()
                        if word_count > 3:
                            # Take first 3 words
                            name = ' '.join(words[:3])
                            return name
                        elif word_count == 1:
                            # This is malformed, use fallback
                            raise NameGenerationError(
                                f"Unable to generate valid name after {max_retries + 1} attempts: "
                                f"Generated name has only 1 word"
                            )
                
                return name
                
            except NameGenerationError:
                # Re-raise our custom errors
                raise
                
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    # Retry on any exception
                    continue
                else:
                    # Wrap and re-raise after all retries exhausted
                    raise NameGenerationError(
                        f"Unable to generate valid name after {max_retries + 1} attempts: {last_error}"
                    ) from e
        
        # Should not reach here, but just in case
        raise NameGenerationError(
            f"Failed to generate valid name after {max_retries + 1} attempts"
        )
