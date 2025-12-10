#!/usr/bin/env python3
"""Test seed with actual Bedrock API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bedrock_client import BedrockClient
from seed_generator import SeedGenerator

print("Testing seed generation with Bedrock...")

# Generate a seed
gen = SeedGenerator()
seed_hex = gen.generate_seed("John", "December")
seed_int = int(seed_hex, 16)

print(f"Generated seed: {seed_hex} (int: {seed_int})")
print(f"Seed in valid range (0-2147483647): {0 <= seed_int <= 2147483647}")

# Test with Bedrock
try:
    client = BedrockClient()
    print("\nTesting with Bedrock Nova Lite...")
    response = client.invoke_nova_lite("Generate a Christmas elf name", seed=seed_hex)
    print(f"✓ Success! Response: {response[:100]}...")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print("\n✓ Seed format is compatible with Bedrock!")
