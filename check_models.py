"""
Quick script to check available Bedrock models in your region.
"""
import boto3
import os
import sys

# Get region from environment or use default
region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
profile = os.environ.get('AWS_PROFILE')

print(f"Checking Bedrock models in region: {region}")
if profile:
    print(f"Using AWS profile: {profile}")
    session = boto3.Session(profile_name=profile, region_name=region)
    bedrock = session.client('bedrock')
else:
    print("Using default AWS credentials")
    bedrock = boto3.client('bedrock', region_name=region)

try:
    # List foundation models
    response = bedrock.list_foundation_models()
    
    print("\n=== Available Models ===\n")
    
    # Filter for Nova and Titan models
    nova_models = []
    titan_models = []
    
    for model in response.get('modelSummaries', []):
        model_id = model.get('modelId', '')
        model_name = model.get('modelName', '')
        
        if 'nova' in model_id.lower() or 'nova' in model_name.lower():
            nova_models.append(model)
        elif 'titan' in model_id.lower() and 'embed' in model_id.lower():
            titan_models.append(model)
    
    print("Nova Models:")
    if nova_models:
        for model in nova_models:
            print(f"  - {model['modelId']}")
            print(f"    Name: {model.get('modelName', 'N/A')}")
            print(f"    Provider: {model.get('providerName', 'N/A')}")
            print()
    else:
        print("  No Nova models found")
    
    print("\nTitan Embedding Models:")
    if titan_models:
        for model in titan_models:
            print(f"  - {model['modelId']}")
            print(f"    Name: {model.get('modelName', 'N/A')}")
            print(f"    Provider: {model.get('providerName', 'N/A')}")
            print()
    else:
        print("  No Titan embedding models found")
    
    print("\n=== Recommended Model IDs ===")
    if nova_models:
        print(f"NOVA_LITE_MODEL_ID = \"{nova_models[0]['modelId']}\"")
    if titan_models:
        print(f"EMBEDDING_MODEL_ID = \"{titan_models[0]['modelId']}\"")
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure you have:")
    print("1. Valid AWS credentials configured")
    print("2. Bedrock access enabled in your AWS account")
    print("3. Model access granted in the Bedrock console")
    sys.exit(1)
