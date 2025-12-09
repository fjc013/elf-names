"""Safety filter for validating family-friendly elf names."""

from typing import Tuple
from bedrock_client import BedrockClient
from exceptions import SafetyFilterError
import sys
import os

# Add tests directory to path to import test_data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))
from test_data import FALLBACK_SAFE_NAMES


class SafetyFilter:
    """
    Validates generated elf names for family-friendly content.
    
    This component uses LLM-based validation to detect inappropriate content
    including political, religious, body part, and suggestive references.
    Implements retry logic and fallback safe names when validation fails.
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize with BedrockClient dependency.
        
        Args:
            bedrock_client: BedrockClient instance for LLM validation
        
        Requirements: 2.5, 2.6
        """
        self.bedrock_client = bedrock_client

    def _check_safety(self, name: str) -> bool:
        """
        Uses LLM to evaluate name safety.
        
        Checks for inappropriate content including:
        - Political references
        - Religious references
        - Body part references
        - Suggestive content
        
        Args:
            name: The elf name to validate
        
        Returns:
            bool: True if name is safe, False otherwise
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        # Build safety validation prompt
        prompt = f"""You are a family-friendly content validator for a children's Christmas elf name generator.

Evaluate if the following elf name is appropriate for all ages and family-friendly.

Elf Name: "{name}"

The name is UNSAFE if it contains ANY of the following:
- Political references (politicians, political parties, political movements, etc.)
- Religious references (religious figures, religious terms, religious holidays other than Christmas, etc.)
- Body part references (any human or animal body parts)
- Suggestive content (anything with romantic, sexual, or inappropriate connotations)
- Offensive language or inappropriate themes

The name is SAFE if it:
- Uses Christmas-themed vocabulary (snow, candy, sparkle, winter, etc.)
- Is whimsical and playful
- Is appropriate for children of all ages

Respond with ONLY one word: "SAFE" or "UNSAFE"
Do not provide any explanation, just the single word."""

        try:
            # Call Bedrock to evaluate name safety
            response = self.bedrock_client.invoke_nova_lite(prompt, seed=None)
            
            # Parse response to determine if name is safe
            response_clean = response.strip().upper()
            
            # Check if response contains "SAFE" or "UNSAFE"
            if "SAFE" in response_clean and "UNSAFE" not in response_clean:
                return True
            elif "UNSAFE" in response_clean:
                return False
            else:
                # If response is unclear, err on the side of caution
                return False
                
        except Exception as e:
            # If safety check fails, err on the side of caution and mark as unsafe
            # This ensures we don't accidentally display inappropriate content
            return False

    def validate_name(self, name: str, generator_func=None, seed: str = None, style_hints: dict = None, max_attempts: int = 3) -> Tuple[bool, str]:
        """
        Validates name safety with retry logic and fallback.
        
        Calls _check_safety on the generated name. If unsafe, attempts to regenerate
        up to max_attempts times. If all attempts fail, returns a fallback safe name.
        
        Args:
            name: The elf name to validate
            generator_func: Optional function to regenerate names (should accept seed and style_hints)
            seed: Optional seed for regeneration
            style_hints: Optional style hints for regeneration
            max_attempts: Maximum number of validation attempts (default: 3)
        
        Returns:
            Tuple[bool, str]: (is_safe, validated_name)
                - is_safe: True if name passed validation, False if fallback was used
                - validated_name: The safe name (original if safe, regenerated if unsafe, or fallback)
        
        Requirements: 2.5, 2.6
        """
        # Try validating the original name
        for attempt in range(max_attempts):
            current_name = name if attempt == 0 else None
            
            # If this is a retry and we have a generator function, regenerate
            if attempt > 0 and generator_func is not None:
                try:
                    current_name = generator_func(seed, style_hints)
                except Exception as e:
                    # If regeneration fails, continue to next attempt or fallback
                    # Log the error but don't fail completely
                    current_name = None
            
            # If we don't have a name to check, skip to next attempt
            if current_name is None:
                continue
            
            # Check if the current name is safe
            try:
                is_safe = self._check_safety(current_name)
            except Exception as e:
                # If safety check fails, err on the side of caution
                # Continue to next attempt or fallback
                is_safe = False
            
            if is_safe:
                # Name is safe, return it
                return (True, current_name)
        
        # All attempts failed, use fallback safe name
        # Select a fallback name deterministically based on seed if available
        if seed:
            try:
                # Use seed to select a consistent fallback
                seed_int = int(seed, 16)
                fallback_index = seed_int % len(FALLBACK_SAFE_NAMES)
                fallback_name = FALLBACK_SAFE_NAMES[fallback_index]
            except (ValueError, TypeError):
                # If seed is invalid, use first fallback
                fallback_name = FALLBACK_SAFE_NAMES[0]
        else:
            # No seed provided, use first fallback
            fallback_name = FALLBACK_SAFE_NAMES[0]
        
        # Return fallback with is_safe=False to indicate we had to use fallback
        return (False, fallback_name)
