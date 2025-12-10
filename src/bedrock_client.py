"""
AWS Bedrock client for interacting with Nova 2 Lite model and embedding services.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError, EndpointConnectionError
import json
import time
import os
from typing import Optional
from exceptions import BedrockAPIError


class BedrockClient:
    """
    Client for AWS Bedrock API interactions.
    Handles authentication, model invocation, and embedding generation.
    
    Supports environment variables:
    - AWS_PROFILE: AWS profile name to use for authentication
    - AWS_DEFAULT_REGION: AWS region for Bedrock service (defaults to us-east-1)
    """
    
    # Model IDs for Bedrock services (using inference profiles for cross-region support)
    NOVA_LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"
    EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
    
    def __init__(self):
        """
        Initialize Bedrock client with AWS authentication.
        
        Uses environment variables for configuration:
        - AWS_PROFILE: Optional AWS profile name
        - AWS_DEFAULT_REGION: Optional AWS region (defaults to us-east-1)
        
        Creates a session with temporary credentials if AWS_PROFILE is set,
        otherwise uses default credential chain.
        
        Raises:
            BedrockAPIError: If AWS credentials are not found or authentication fails
        
        Requirements: 5.1, 5.2, 5.4
        """
        try:
            # Get configuration from environment variables
            aws_profile = os.environ.get('AWS_PROFILE')
            aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')
            
            # Create a session with profile if specified
            if aws_profile:
                # Use profile-based session for temporary credentials
                session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
                self.bedrock_runtime = session.client(service_name='bedrock-runtime')
            else:
                # Use default credential chain
                self.bedrock_runtime = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=aws_region
                )
            
        except NoCredentialsError as e:
            raise BedrockAPIError(
                "Unable to connect to AI service. Please ensure AWS credentials are configured."
            ) from e
            
        except PartialCredentialsError as e:
            raise BedrockAPIError(
                "Unable to connect to AI service. AWS credentials are incomplete."
            ) from e
            
        except EndpointConnectionError as e:
            raise BedrockAPIError(
                "Unable to connect to AI service. Please check your internet connection."
            ) from e
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            raise BedrockAPIError(
                f"Unable to connect to AI service: {error_message}"
            ) from e
            
        except Exception as e:
            raise BedrockAPIError(
                f"Unexpected error initializing AI service: {str(e)}"
            ) from e
    
    def invoke_nova_lite(self, prompt: str, max_retries: int = 3) -> str:
        """
        Invoke Nova 2 Lite model with the given prompt.
        Implements exponential backoff for rate limiting.
        
        Args:
            prompt: The prompt text to send to the model
            max_retries: Maximum number of retry attempts for rate limiting
        
        Returns:
            str: The generated text response from the model
        
        Raises:
            BedrockAPIError: If the API call fails after retries
            ValueError: If the response format is unexpected
            TimeoutError: If the request times out
        
        Requirements: 5.4
        """
        # Build request body according to Nova Lite API format
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                # Invoke the model
                response = self.bedrock_runtime.invoke_model(
                    modelId=self.NOVA_LITE_MODEL_ID,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                # Extract generated text from response
                if 'output' in response_body and 'message' in response_body['output']:
                    message = response_body['output']['message']
                    if 'content' in message and len(message['content']) > 0:
                        return message['content'][0]['text']
                
                raise ValueError("Unexpected response format from Nova Lite model")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                
                if error_code == 'ThrottlingException':
                    # Implement exponential backoff for rate limiting
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                        time.sleep(wait_time)
                        continue
                    else:
                        raise BedrockAPIError(
                            "Service is busy. Please try again in a moment."
                        ) from e
                        
                elif error_code == 'ModelTimeoutException':
                    raise BedrockAPIError(
                        "Request timed out. Please check your internet connection and try again."
                    ) from e
                    
                elif error_code == 'AccessDeniedException':
                    raise BedrockAPIError(
                        "Unable to connect to AI service. Please ensure AWS credentials are configured."
                    ) from e
                    
                elif error_code == 'ValidationException':
                    raise BedrockAPIError(
                        f"Invalid request: {error_message}"
                    ) from e
                    
                else:
                    raise BedrockAPIError(
                        f"AI service error: {error_message}"
                    ) from e
                    
            except EndpointConnectionError as e:
                raise BedrockAPIError(
                    "Unable to connect to AI service. Please check your internet connection."
                ) from e
                
            except json.JSONDecodeError as e:
                raise BedrockAPIError(
                    "Invalid response from AI service."
                ) from e
                
            except Exception as e:
                # Catch any other unexpected errors
                raise BedrockAPIError(
                    f"Unexpected error calling AI service: {str(e)}"
                ) from e
        
        # Should not reach here, but just in case
        raise BedrockAPIError("Failed to invoke model after all retries")
    
    def generate_embedding(self, text: str, max_retries: int = 3) -> list[float]:
        """
        Generate embedding vector for the given text using Bedrock embedding model.
        Implements exponential backoff for rate limiting.
        
        Args:
            text: The text to generate an embedding for
            max_retries: Maximum number of retry attempts for rate limiting
        
        Returns:
            list[float]: The embedding vector as a list of floats
        
        Raises:
            BedrockAPIError: If the API call fails after retries
            ValueError: If the response format is unexpected
        
        Requirements: 5.4
        """
        # Build request body for embedding model
        request_body = {
            "inputText": text
        }
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                # Invoke the embedding model
                response = self.bedrock_runtime.invoke_model(
                    modelId=self.EMBEDDING_MODEL_ID,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                # Extract embedding vector from response
                if 'embedding' in response_body:
                    embedding = response_body['embedding']
                    if isinstance(embedding, list) and len(embedding) > 0:
                        return embedding
                
                raise ValueError("Unexpected response format from embedding model")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                
                if error_code == 'ThrottlingException':
                    # Implement exponential backoff for rate limiting
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                        time.sleep(wait_time)
                        continue
                    else:
                        raise BedrockAPIError(
                            "Service is busy. Please try again in a moment."
                        ) from e
                        
                elif error_code == 'AccessDeniedException':
                    raise BedrockAPIError(
                        "Unable to connect to AI service. Please ensure AWS credentials are configured."
                    ) from e
                    
                elif error_code == 'ValidationException':
                    raise BedrockAPIError(
                        f"Invalid request: {error_message}"
                    ) from e
                    
                else:
                    raise BedrockAPIError(
                        f"AI service error: {error_message}"
                    ) from e
                    
            except EndpointConnectionError as e:
                raise BedrockAPIError(
                    "Unable to connect to AI service. Please check your internet connection."
                ) from e
                
            except json.JSONDecodeError as e:
                raise BedrockAPIError(
                    "Invalid response from AI service."
                ) from e
                
            except Exception as e:
                # Catch any other unexpected errors
                raise BedrockAPIError(
                    f"Unexpected error calling AI service: {str(e)}"
                ) from e
        
        # Should not reach here, but just in case
        raise BedrockAPIError("Failed to generate embedding after all retries")
