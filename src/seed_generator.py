"""Seed generation component for deterministic elf name generation."""

import hashlib


class SeedGenerator:
    """Generates deterministic seeds from user input for reproducible name generation."""
    
    def generate_seed(self, first_name: str, birth_month: str) -> str:
        """
        Creates a seed from SHA-256 hash of name+month that fits within valid range.
        
        The seed is constrained to 0-2147483647 (max 32-bit signed integer)
        to ensure compatibility with AWS Bedrock models.
        
        Args:
            first_name: User's first name
            birth_month: User's birth month (e.g., "January", "February", etc.)
            
        Returns:
            Hexadecimal string representing a value between 0 and 2147483647
            
        Requirements: 4.1, 4.2
        """
        # Concatenate first_name and birth_month
        combined_input = first_name + birth_month
        
        # Create SHA-256 hash
        hash_object = hashlib.sha256(combined_input.encode('utf-8'))
        
        # Get hexadecimal representation
        hex_digest = hash_object.hexdigest()
        
        # Convert to integer and constrain to valid range (0 to 2^31 - 1)
        # This ensures compatibility with AWS Bedrock seed requirements
        seed_int = int(hex_digest, 16) % 2147483648  # 2^31
        
        # Convert back to hex string (without '0x' prefix)
        seed = hex(seed_int)[2:]
        
        return seed
