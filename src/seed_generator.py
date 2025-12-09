"""Seed generation component for deterministic elf name generation."""

import hashlib


class SeedGenerator:
    """Generates deterministic seeds from user input for reproducible name generation."""
    
    def generate_seed(self, first_name: str, birth_month: str) -> str:
        """
        Creates an 8-character seed from SHA-256 hash of name+month.
        
        Args:
            first_name: User's first name
            birth_month: User's birth month (e.g., "January", "February", etc.)
            
        Returns:
            Hexadecimal string of length 8
            
        Requirements: 4.1, 4.2
        """
        # Concatenate first_name and birth_month
        combined_input = first_name + birth_month
        
        # Create SHA-256 hash
        hash_object = hashlib.sha256(combined_input.encode('utf-8'))
        
        # Get hexadecimal representation
        hex_digest = hash_object.hexdigest()
        
        # Extract first 8 characters
        seed = hex_digest[:8]
        
        return seed
