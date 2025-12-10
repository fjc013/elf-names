"""
Quick test to verify Bedrock connection and model access.
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bedrock_client import BedrockClient
from exceptions import BedrockAPIError

print("Testing Bedrock connection...")
print("=" * 50)

try:
    # Initialize client
    print("\n1. Initializing BedrockClient...")
    client = BedrockClient()
    print("   ✓ Client initialized successfully")
    
    # Test Nova Lite model
    print("\n2. Testing Nova Lite model...")
    print(f"   Model ID: {client.NOVA_LITE_MODEL_ID}")
    response = client.invoke_nova_lite("Say 'Hello, Elf!'")
    print(f"   ✓ Response: {response[:100]}...")
    
    # Test Titan embedding model
    print("\n3. Testing Titan Embedding model...")
    print(f"   Model ID: {client.EMBEDDING_MODEL_ID}")
    embedding = client.generate_embedding("test")
    print(f"   ✓ Embedding generated (dimension: {len(embedding)})")
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! Your Bedrock setup is working.")
    print("=" * 50)
    
except BedrockAPIError as e:
    print(f"\n✗ Bedrock API Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your AWS credentials are configured")
    print("2. Verify you have Bedrock access in your AWS account")
    print("3. Ensure model access is granted in Bedrock console")
    print("4. Check your AWS_DEFAULT_REGION is set correctly")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ Unexpected Error: {e}")
    sys.exit(1)
