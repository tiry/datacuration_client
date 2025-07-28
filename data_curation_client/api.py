"""
Data Curation API client implementation.

This module provides the core functionality to interact with the Hyland Data Curation API,
including authentication, file upload, and result retrieval.
"""

import json
import time
from typing import Dict, Any, Optional, Tuple, BinaryIO
import requests
from pathlib import Path

from .config import config


class DataCurationAPIClient:
    """Client for interacting with the Hyland Data Curation API."""
    
    def __init__(self, api_token: Optional[str] = None) -> None:
        """
        Initialize the API client.
        
        Args:
            api_token: Optional API token. If not provided, it will be loaded from config.
        """
        if api_token:
            config.update(api_token=api_token)
    
    def presign(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Call the presign endpoint to get URLs for file upload and result retrieval.
        
        Args:
            options: Optional processing options (normalization, chunking, embedding).
            
        Returns:
            Dict containing job_id, put_url, and get_url.
            
        Raises:
            ValueError: If the API token is missing.
            requests.RequestException: If the API request fails.
        """
        config.validate()
        
        # Default options if none provided
        if options is None:
            options = {}
        
        response = requests.post(
            config.presign_endpoint,
            headers=config.get_headers(),
            json=options
        )
        
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Upload a file to the Data Curation API.
        
        Args:
            file_path: Path to the file to upload.
            options: Optional processing options.
            
        Returns:
            Dict containing job_id, put_url, and get_url.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the API token is missing.
            requests.RequestException: If the API request fails.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get presigned URLs
        presign_data = self.presign(options)
        
        # Upload file to the put_url
        with open(file_path_obj, 'rb') as file:
            response = requests.put(
                presign_data['put_url'],
                data=file
            )
            response.raise_for_status()
        
        return presign_data
    
    def get_results(self, get_url: str) -> str:
        """
        Get the results of the data curation process.
        
        Args:
            get_url: URL to retrieve the results from.
            
        Returns:
            The curated text.
            
        Raises:
            requests.RequestException: If the API request fails.
        """
        response = requests.get(get_url)
        response.raise_for_status()
        return response.text
    
    def process_file(
        self, 
        file_path: str, 
        options: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        max_retries: int = 10,
        retry_delay: int = 2
    ) -> str:
        """
        Process a file through the Data Curation API and retrieve the results.
        
        Args:
            file_path: Path to the file to process.
            options: Optional processing options.
            wait: Whether to wait for processing to complete.
            max_retries: Maximum number of retries when waiting for results.
            retry_delay: Delay between retries in seconds.
            
        Returns:
            The curated text.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the API token is missing.
            requests.RequestException: If the API request fails.
            TimeoutError: If max_retries is reached while waiting for results.
        """
        # Upload the file and get URLs
        presign_data = self.upload_file(file_path, options)
        
        if not wait:
            return json.dumps(presign_data)
        
        # Wait for processing to complete and get results
        retries = 0
        while retries < max_retries:
            try:
                return self.get_results(presign_data['get_url'])
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    # Resource not ready yet, wait and retry
                    time.sleep(retry_delay)
                    retries += 1
                else:
                    # Other HTTP error
                    raise
        
        raise TimeoutError(f"Processing timed out after {max_retries} retries")
