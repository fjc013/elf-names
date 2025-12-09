"""Property-based tests for seed generation."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from hypothesis import given, settings, strategies as st
from seed_generator import SeedGenerator


class TestSeedGenerationProperties:
    """Property-based tests for SeedGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SeedGenerator()
    
    # Feature: elf-name-generator, Property 7: Seed generation consistency
    # Validates: Requirements 4.1, 4.2
    @given(
        first_name=st.text(min_size=1, max_size=50),
        birth_month=st.text(min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    def test_seed_generation_consistency(self, first_name, birth_month):
        """
        Property 7: Seed generation consistency
        
        For any first name and birth month combination, the generated seed should be:
        1. An 8-character hexadecimal string
        2. Deterministic (same input = same seed)
        
        Validates: Requirements 4.1, 4.2
        """
        # Generate seed twice with same inputs
        seed1 = self.generator.generate_seed(first_name, birth_month)
        seed2 = self.generator.generate_seed(first_name, birth_month)
        
        # Assert determinism: same inputs produce same seed
        assert seed1 == seed2, f"Seeds should be identical for same inputs: {seed1} != {seed2}"
        
        # Assert seed is exactly 8 characters
        assert len(seed1) == 8, f"Seed should be 8 characters, got {len(seed1)}"
        
        # Assert seed is hexadecimal (only contains 0-9, a-f)
        assert all(c in '0123456789abcdef' for c in seed1), \
            f"Seed should be hexadecimal, got: {seed1}"
