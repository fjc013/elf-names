"""Test seed generation and conversion."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from seed_generator import SeedGenerator

# Test seed generation
gen = SeedGenerator()
seed_hex = gen.generate_seed("John", "December")
print(f"Generated seed (hex): {seed_hex}")
print(f"Seed length: {len(seed_hex)}")

# Convert to integer
seed_int = int(seed_hex, 16)
print(f"Seed as integer: {seed_int}")
print(f"Seed in range 0-2147483647: {0 <= seed_int <= 2147483647}")
print(f"Seed in range 0-4294967295: {0 <= seed_int <= 4294967295}")

# Test with different inputs
test_cases = [
    ("Alice", "January"),
    ("Bob", "June"),
    ("Charlie", "December"),
]

print("\nTesting multiple seeds:")
for name, month in test_cases:
    seed_hex = gen.generate_seed(name, month)
    seed_int = int(seed_hex, 16)
    print(f"{name} + {month}: {seed_hex} -> {seed_int}")
