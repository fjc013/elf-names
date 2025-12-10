"""
Unit tests for BedrockClient class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from bedrock_client import BedrockClient
from exceptions import BedrockAPIError


class TestBedrockClientInitialization:
    """Tests for BedrockClient initialization and authentication."""
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_successful_initialization_default(self, mock_boto_client):
        """Test that BedrockClient initializes successfully with default settings."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        client = BedrockClient()
        
        assert client.bedrock_runtime is not None
        mock_boto_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='us-east-2'
        )
    
    @patch('bedrock_client.boto3.Session')
    @patch.dict('os.environ', {'AWS_PROFILE': 'test-profile', 'AWS_DEFAULT_REGION': 'us-west-2'})
    def test_initialization_with_profile(self, mock_session):
        """Test that BedrockClient uses AWS_PROFILE for session-based authentication."""
        mock_session_instance = Mock()
        mock_client = Mock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        
        client = BedrockClient()
        
        assert client.bedrock_runtime is not None
        mock_session.assert_called_once_with(
            profile_name='test-profile',
            region_name='us-west-2'
        )
        mock_session_instance.client.assert_called_once_with(service_name='bedrock-runtime')
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {'AWS_DEFAULT_REGION': 'eu-west-1'}, clear=True)
    def test_initialization_with_custom_region(self, mock_boto_client):
        """Test that BedrockClient uses AWS_DEFAULT_REGION environment variable."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        client = BedrockClient()
        
        assert client.bedrock_runtime is not None
        mock_boto_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='eu-west-1'
        )
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_no_credentials_error(self, mock_boto_client):
        """Test that BedrockAPIError is raised when AWS credentials are missing."""
        mock_boto_client.side_effect = NoCredentialsError()
        
        with pytest.raises(BedrockAPIError, match="AWS credentials are configured"):
            BedrockClient()
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_partial_credentials_error(self, mock_boto_client):
        """Test that BedrockAPIError is raised when AWS credentials are incomplete."""
        mock_boto_client.side_effect = PartialCredentialsError(
            provider='test', cred_var='test'
        )
        
        with pytest.raises(BedrockAPIError, match="credentials are incomplete"):
            BedrockClient()


class TestInvokeNovaLite:
    """Tests for invoke_nova_lite method."""
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_invoke_without_seed(self, mock_boto_client):
        """Test invoking Nova Lite without a seed."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock successful response
        mock_response = {
            'body': MagicMock(),
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        response_body = {
            'output': {
                'message': {
                    'content': [{'text': 'Sparkle Snowflake'}]
                }
            }
        }
        mock_response['body'].read.return_value = json.dumps(response_body).encode()
        mock_client.invoke_model.return_value = mock_response
        
        client = BedrockClient()
        result = client.invoke_nova_lite("Generate an elf name")
        
        assert result == 'Sparkle Snowflake'
        assert mock_client.invoke_model.called
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_invoke_without_seed_parameter(self, mock_boto_client):
        """Test invoking Nova Lite without seed parameter (new approach)."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock successful response
        mock_response = {
            'body': MagicMock(),
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        response_body = {
            'output': {
                'message': {
                    'content': [{'text': 'Jolly Tinsel'}]
                }
            }
        }
        mock_response['body'].read.return_value = json.dumps(response_body).encode()
        mock_client.invoke_model.return_value = mock_response
        
        client = BedrockClient()
        result = client.invoke_nova_lite("Generate an elf name")
        
        assert result == 'Jolly Tinsel'
        
        # Verify seed was NOT included in request
        call_args = mock_client.invoke_model.call_args
        request_body = json.loads(call_args[1]['body'])
        assert 'seed' not in request_body['inferenceConfig']
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_invoke_with_max_retries(self, mock_boto_client):
        """Test invoking Nova Lite with custom max_retries parameter."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock successful response
        mock_response = {
            'body': MagicMock(),
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        response_body = {
            'output': {
                'message': {
                    'content': [{'text': 'Sparkle Bell'}]
                }
            }
        }
        mock_response['body'].read.return_value = json.dumps(response_body).encode()
        mock_client.invoke_model.return_value = mock_response
        
        client = BedrockClient()
        result = client.invoke_nova_lite("Generate an elf name", max_retries=5)
        
        assert result == 'Sparkle Bell'
    
    @patch('bedrock_client.boto3.client')
    @patch('bedrock_client.time.sleep')  # Mock sleep to speed up test
    @patch.dict('os.environ', {}, clear=True)
    def test_throttling_exception(self, mock_sleep, mock_boto_client):
        """Test handling of API rate limiting with exponential backoff."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock throttling error
        error_response = {
            'Error': {
                'Code': 'ThrottlingException',
                'Message': 'Rate exceeded'
            }
        }
        mock_client.invoke_model.side_effect = ClientError(
            error_response=error_response,
            operation_name='InvokeModel'
        )
        
        client = BedrockClient()
        
        with pytest.raises(BedrockAPIError, match="Service is busy"):
            client.invoke_nova_lite("Generate an elf name")
        
        # Verify exponential backoff was attempted (3 retries)
        assert mock_client.invoke_model.call_count == 3


class TestGenerateEmbedding:
    """Tests for generate_embedding method."""
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_generate_embedding_success(self, mock_boto_client):
        """Test successful embedding generation."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock successful response
        mock_response = {
            'body': MagicMock(),
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        response_body = {
            'embedding': [0.1, 0.2, 0.3, -0.1, -0.2]
        }
        mock_response['body'].read.return_value = json.dumps(response_body).encode()
        mock_client.invoke_model.return_value = mock_response
        
        client = BedrockClient()
        result = client.generate_embedding("John December")
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert result == [0.1, 0.2, 0.3, -0.1, -0.2]
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_generate_embedding_unexpected_format(self, mock_boto_client):
        """Test handling of unexpected response format."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock response with unexpected format
        mock_response = {
            'body': MagicMock(),
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        response_body = {'unexpected': 'format'}
        mock_response['body'].read.return_value = json.dumps(response_body).encode()
        mock_client.invoke_model.return_value = mock_response
        
        client = BedrockClient()
        
        with pytest.raises(BedrockAPIError, match="Unexpected error calling AI service"):
            client.generate_embedding("John December")
    
    @patch('bedrock_client.boto3.client')
    @patch.dict('os.environ', {}, clear=True)
    def test_generate_embedding_access_denied(self, mock_boto_client):
        """Test handling of access denied errors."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Mock access denied error
        error_response = {
            'Error': {
                'Code': 'AccessDeniedException',
                'Message': 'Access denied'
            }
        }
        mock_client.invoke_model.side_effect = ClientError(
            error_response=error_response,
            operation_name='InvokeModel'
        )
        
        client = BedrockClient()
        
        with pytest.raises(BedrockAPIError, match="AWS credentials are configured"):
            client.generate_embedding("John December")
