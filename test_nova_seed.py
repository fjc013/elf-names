"""Test Nova Lite seed requirements."""
import boto3
import json
import os

region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')
profile = os.environ.get('AWS_PROFILE')

if profile:
    session = boto3.Session(profile_name=profile, region_name=region)
    bedrock_runtime = session.client('bedrock-runtime')
else:
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

# Test different seed values
test_seeds = [
    0,
    1,
    100,
    2147483647,  # Max 32-bit signed int
    4294967295,  # Max 32-bit unsigned int
]

model_id = "us.amazon.nova-lite-v1:0"

for seed_value in test_seeds:
    print(f"\nTesting seed: {seed_value}")
    
    request_body = {
        "messages": [{"role": "user", "content": [{"text": "Say hello"}]}],
        "inferenceConfig": {
            "max_new_tokens": 10,
            "temperature": 0.7,
            "seed": seed_value
        }
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        print(f"  ✓ Seed {seed_value} works!")
    except Exception as e:
        print(f"  ✗ Seed {seed_value} failed: {e}")
