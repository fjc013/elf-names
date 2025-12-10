"""Unit tests for SeedGenerator component."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from seed_generator import SeedGenerator


class TestSeedGenerator:
    """Test suite for SeedGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SeedGenerator()
    
    def test_generate_seed_returns_valid_hex_string(self):
        """Test that generated seed is a valid hexadecimal string."""
        seed = self.generator.generate_seed("Alice", "January")
        # Should be a valid hex string (variable length, but not empty)
        assert len(seed) > 0
        assert len(seed) <= 8  # Max 8 chars for 2^31-1
    
    def test_generate_seed_returns_hexadecimal(self):
        """Test that generated seed contains only hexadecimal characters."""
        seed = self.generator.generate_seed("Bob", "December")
        # All characters should be valid hex (0-9, a-f)
        assert all(c in '0123456789abcdef' for c in seed)
    
    def test_generate_seed_is_deterministic(self):
        """Test that same inputs produce same seed (reproducibility)."""
        seed1 = self.generator.generate_seed("Charlie", "March")
        seed2 = self.generator.generate_seed("Charlie", "March")
        assert seed1 == seed2
    
    def test_generate_seed_different_inputs_produce_different_seeds(self):
        """Test that different inputs produce different seeds."""
        seed1 = self.generator.generate_seed("Alice", "January")
        seed2 = self.generator.generate_seed("Bob", "January")
        seed3 = self.generator.generate_seed("Alice", "February")
        
        assert seed1 != seed2
        assert seed1 != seed3
        assert seed2 != seed3
    
    def test_generate_seed_with_known_input(self):
        """Test seed generation with a known input to verify implementation."""
        # This is a regression test - the seed should be deterministic
        seed = self.generator.generate_seed("Alice", "January")
        # Verify it's within valid range when converted to int
        seed_int = int(seed, 16)
        assert 0 <= seed_int <= 2147483647  # Max 32-bit signed int
        
    def test_generate_seed_within_valid_range(self):
        """Test that all generated seeds are within AWS Bedrock's valid range."""
        test_cases = [
            ("Alice", "January"),
            ("Bob", "December"),
            ("Charlie", "June"),
            ("Diana", "March"),
        ]
        
        for first_name, birth_month in test_cases:
            seed = self.generator.generate_seed(first_name, birth_month)
            seed_int = int(seed, 16)
            assert 0 <= seed_int <= 2147483647, f"Seed {seed_int} out of range for {first_name} {birth_month}"
