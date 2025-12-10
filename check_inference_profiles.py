"""
Check available inference profiles for Bedrock models.
"""
import boto3
import os

region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')
profile = os.environ.get('AWS_PROFILE')

print(f"Checking inference profiles in region: {region}")
if profile:
    print(f"Using AWS profile: {profile}")
    session = boto3.Session(profile_name=profile, region_name=region)
    bedrock = session.client('bedrock')
else:
    bedrock = boto3.client('bedrock', region_name=region)

try:
    # List inference profiles
    response = bedrock.list_inference_profiles()
    
    print("\n=== Available Inference Profiles ===\n")
    
    nova_profiles = []
    
    for profile in response.get('inferenceProfileSummaries', []):
        profile_id = profile.get('inferenceProfileId', '')
        profile_name = profile.get('inferenceProfileName', '')
        models = profile.get('models', [])
        
        print(f"Profile: {profile_name}")
        print(f"  ID: {profile_id}")
        print(f"  Models: {models}")
        print()
        
        if 'nova' in profile_name.lower() or any('nova' in str(m).lower() for m in models):
            nova_profiles.append(profile)
    
    print("\n=== Recommended for Nova Lite ===")
    for profile in nova_profiles:
        if 'lite' in profile.get('inferenceProfileName', '').lower():
            print(f"NOVA_LITE_MODEL_ID = \"{profile['inferenceProfileId']}\"")
            break
    
except Exception as e:
    print(f"Error: {e}")
    print("\nNote: Inference profiles may not be available in all regions.")
