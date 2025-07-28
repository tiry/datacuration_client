"""
Tests for the Data Curation API client.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from data_curation_client.api import DataCurationAPIClient
from data_curation_client.config import config


@pytest.fixture
def mock_config():
    """Fixture to set up a mock configuration."""
    with patch("data_curation_client.api.config") as mock_config:
        mock_config.presign_endpoint = "https://test-api.example.com/presign"
        mock_config.get_headers.return_value = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
            "Accept": "text/json",
        }
        yield mock_config


@pytest.fixture
def api_client(mock_config):
    """Fixture to create an API client with mock configuration."""
    return DataCurationAPIClient(api_token="test_token")


def test_presign(api_client, mock_config):
    """Test the presign method."""
    with patch("requests.post") as mock_post:
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
            headers=mock_config.get_headers(),
            json={}
        )


def test_presign_with_options(api_client, mock_config):
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
            headers=mock_config.get_headers(),
            json=options
        )


def test_upload_file(api_client):
    """Test the upload_file method."""
    with patch("data_curation_client.api.DataCurationAPIClient.presign") as mock_presign, \
         patch("builtins.open", MagicMock()), \
         patch("requests.put") as mock_put, \
         patch("pathlib.Path.exists", return_value=True):
        
        # Set up the mock presign response
        mock_presign.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        
        # Set up the mock put response
        mock_put_response = MagicMock()
        mock_put.return_value = mock_put_response
        
        # Call the method
        result = api_client.upload_file("test_file.txt")
        
        # Verify the result
        assert result["job_id"] == "test-job-id"
        assert result["put_url"] == "https://test-s3.example.com/upload"
        assert result["get_url"] == "https://test-s3.example.com/results"
        
        # Verify the put request was made
        mock_put.assert_called_once()


def test_get_results(api_client):
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


def test_process_file(api_client):
    """Test the process_file method."""
    with patch("data_curation_client.api.DataCurationAPIClient.upload_file") as mock_upload, \
         patch("data_curation_client.api.DataCurationAPIClient.get_results") as mock_get_results:
        
        # Set up the mock upload response
        mock_upload.return_value = {
            "job_id": "test-job-id",
            "put_url": "https://test-s3.example.com/upload",
            "get_url": "https://test-s3.example.com/results",
        }
        
        # Set up the mock get_results response
        mock_get_results.return_value = "Curated text content"
        
        # Call the method
        result = api_client.process_file("test_file.txt")
        
        # Verify the result
        assert result == "Curated text content"
        
        # Verify the method calls
        mock_upload.assert_called_once_with("test_file.txt", None)
        mock_get_results.assert_called_once_with("https://test-s3.example.com/results")
