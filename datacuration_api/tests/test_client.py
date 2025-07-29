"""
Tests for the Data Curation API client.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import Generator

from datacuration_api.client import DataCurationClient
from datacuration_api.config import config


@pytest.fixture
def mock_config() -> Generator[MagicMock, None, None]:
    """Fixture to set up a mock configuration."""
    with patch("datacuration_api.client.config") as mock_config:
        mock_config.presign_endpoint = "https://test-api.example.com/presign"
        mock_config.status_endpoint = "https://test-api.example.com/status"
        mock_config.auth_endpoint = "https://test-auth.example.com/token"
        mock_config.client_id = "test_client_id"
        mock_config.client_secret = "test_client_secret"
        mock_config.access_token = "test_access_token"
        mock_config.get_token_request_data.return_value = {
            "grant_type": "client_credentials",
            "scope": "environment_authorization",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
        mock_config.get_auth_headers.return_value = {
            "Authorization": "Bearer test_access_token",
            "Content-Type": "application/json",
            "Accept": "text/json",
        }
        yield mock_config


@pytest.fixture
def api_client(mock_config: MagicMock) -> DataCurationClient:
    """Fixture to create an API client with mock configuration."""
    return DataCurationClient(client_id="test_client_id", client_secret="test_client_secret")


def test_authenticate(api_client: DataCurationClient, mock_config: MagicMock) -> None:
    """Test the authenticate method."""
    with patch("requests.post") as mock_post:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 900,
            "token_type": "Bearer",
            "scope": "environment_authorization"
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = api_client.authenticate()
        
        # Verify the result
        assert result == "test_access_token"
        
        # Verify the config was validated
        mock_config.validate.assert_called_once()
        
        # Verify the token request was made correctly
        mock_post.assert_called_once_with(
            mock_config.auth_endpoint,
            data=mock_config.get_token_request_data(),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Verify the access token was stored
        assert mock_config.access_token == "test_access_token"
        assert mock_config.token_expiry == 900


def test_presign(api_client: DataCurationClient, mock_config: MagicMock) -> None:
    """Test the presign method."""
    with patch("requests.post") as mock_post, \
         patch("datacuration_api.client.DataCurationClient.authenticate") as mock_auth:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = api_client.presign()
        
        # Verify the result
        assert result["job_id"] == "test-job-id"
        assert result["put_url"] == "https://test-s3.example.com/upload"
        assert result["get_url"] == "https://test-s3.example.com/results"
        
        # Verify the request
        mock_post.assert_called_once_with(
            mock_config.presign_endpoint,
            headers=mock_config.get_auth_headers(),
            json={}
        )
        
        # Verify authentication was called when no access token is available
        mock_config.access_token = None
        api_client.presign()
        mock_auth.assert_called_once()


def test_presign_with_options(api_client: DataCurationClient, mock_config: MagicMock) -> None:
    """Test the presign method with options."""
    with patch("requests.post") as mock_post:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        mock_post.return_value = mock_response
        
        # Call the method with options
        options = {
            "chunking": True,
            "embedding": False,
            "normalization": "FULL"
        }
        result = api_client.presign(options)
        
        # Verify the request includes the options
        mock_post.assert_called_once_with(
            mock_config.presign_endpoint,
            headers=mock_config.get_auth_headers(),
            json=options
        )


def test_upload_file(api_client: DataCurationClient) -> None:
    """Test the upload_file method."""
    with patch("datacuration_api.client.DataCurationClient.presign") as mock_presign, \
         patch("builtins.open", MagicMock()), \
         patch("requests.put") as mock_put, \
         patch("pathlib.Path.exists", return_value=True):
        
        # Set up the mock presign response
        mock_presign.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        
        # Set up the mock file content
        mock_file_content = b"test file content"
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = mock_file_content
        
        with patch("builtins.open", return_value=mock_file):
            # Call the method
            result = api_client.upload_file("test_file.txt")
            
            # Verify the result
            assert result["job_id"] == "test-job-id"
            assert result["put_url"] == "https://test-s3.example.com/upload"
            assert result["get_url"] == "https://test-s3.example.com/results"
            
            # Verify the put request was made with correct headers
            mock_put.assert_called_once_with(
                "https://test-s3.example.com/upload",
                data=mock_file_content,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Length": str(len(mock_file_content))
                }
            )


def test_get_results(api_client: DataCurationClient) -> None:
    """Test the get_results method."""
    with patch("requests.get") as mock_get:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.text = "Curated text content"
        mock_get.return_value = mock_response
        
        # Call the method
        result = api_client.get_results("https://test-s3.example.com/results")
        
        # Verify the result
        assert result == "Curated text content"
        
        # Verify the request
        mock_get.assert_called_once_with("https://test-s3.example.com/results")


def test_check_status(api_client: DataCurationClient, mock_config: MagicMock) -> None:
    """Test the check_status method."""
    with patch("requests.get") as mock_get:
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobId": "test-job-id",
            "status": "Done"
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = api_client.check_status("test-job-id")
        
        # Verify the result
        assert result["jobId"] == "test-job-id"
        assert result["status"] == "Done"
        
        # Verify the request
        mock_get.assert_called_once_with(
            f"{mock_config.status_endpoint}/test-job-id",
            headers=mock_config.get_auth_headers()
        )


def test_process_file(api_client: DataCurationClient) -> None:
    """Test the process_file method."""
    with patch("datacuration_api.client.DataCurationClient.upload_file") as mock_upload, \
         patch("datacuration_api.client.DataCurationClient.check_status") as mock_check_status, \
         patch("datacuration_api.client.DataCurationClient.get_results") as mock_get_results:
        
        # Set up the mock upload response
        mock_upload.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        
        # Set up the mock check_status response
        mock_check_status.return_value = {
            "jobId": "test-job-id",
            "status": "Done"
        }
        
        # Set up the mock get_results response
        mock_get_results.return_value = "Curated text content"
        
        # Call the method
        result = api_client.process_file("test_file.txt")
        
        # Verify the result
        assert result == "Curated text content"
        
        # Verify the method calls
        mock_upload.assert_called_once_with("test_file.txt", None)
        mock_check_status.assert_called_once_with("test-job-id")
        mock_get_results.assert_called_once_with("https://test-s3.example.com/results")
