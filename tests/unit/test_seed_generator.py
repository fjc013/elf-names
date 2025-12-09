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
    
    def test_generate_seed_returns_8_character_string(self):
        """Test that generated seed is exactly 8 characters long."""
        seed = self.generator.generate_seed("Alice", "January")
        assert len(seed) == 8
    
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
        """Test seed generation with a known input to verify SHA-256 implementation."""
        # This is a regression test - the exact value comes from SHA-256("AliceJanuary")
        seed = self.generator.generate_seed("Alice", "January")
        # First 8 characters of SHA-256 hash of "AliceJanuary"
        expected = "8090a3b7"
        assert seed == expected
