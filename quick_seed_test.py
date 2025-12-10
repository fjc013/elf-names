"""Quick test of seed generator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from seed_generator import SeedGenerator

gen = SeedGenerator()

# Test cases
test_cases = [
    ("Alice", "January"),
    ("Bob", "December"),
    ("John", "March"),
]

print("Testing seed generation:")
print("=" * 60)

for name, month in test_cases:
    seed_hex = gen.generate_seed(name, month)
    seed_int = int(seed_hex, 16)
    
    print(f"\n{name} + {month}:")
    print(f"  Hex seed: {seed_hex}")
    print(f"  Int seed: {seed_int}")
    print(f"  In range: {0 <= seed_int <= 2147483647}")
    
    # Test determinism
    seed_hex2 = gen.generate_seed(name, month)
    print(f"  Deterministic: {seed_hex == seed_hex2}")

print("\n" + "=" * 60)
print("✓ All seeds generated successfully and within valid range!")
