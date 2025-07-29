"""
Data Curation API client implementation.

This module provides the core functionality to interact with the Hyland Data Curation API,
including authentication, file upload, and result retrieval.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Tuple, BinaryIO
import requests
from pathlib import Path

from .config import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DataCurationClient:
    """Client for interacting with the Hyland Data Curation API."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:
        """
        Initialize the API client.
        
        Args:
            client_id: Optional client ID. If not provided, it will be loaded from config.
            client_secret: Optional client secret. If not provided, it will be loaded from config.
        """
        if client_id:
            config.update(client_id=client_id)
        if client_secret:
            config.update(client_secret=client_secret)
    
    def authenticate(self) -> str:
        """
        Authenticate with the API and get an access token.
        
        Returns:
            str: The access token.
            
        Raises:
            ValueError: If client_id or client_secret is missing.
            requests.RequestException: If the authentication request fails.
        """
        config.validate()
        
        logger.info(f"Authenticating with endpoint: {config.auth_endpoint}")
        
        # Make a POST request to the auth endpoint
        try:
            response = requests.post(
                config.auth_endpoint,
                data=config.get_token_request_data(),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            logger.info(f"Auth response status code: {response.status_code}")
            response.raise_for_status()
            token_data = response.json()
            
            # Store the access token and expiry time
            config.access_token = token_data["access_token"]
            config.token_expiry = token_data.get("expires_in", 900)  # Default to 15 minutes if not provided
            
            logger.info("Authentication successful")
            return config.access_token
        except requests.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    def presign(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the presign endpoint to get URLs for file upload and result retrieval.
        
        Args:
            options: Optional processing options (normalization, chunking, embedding).
            
        Returns:
            Dict containing job_id, put_url, and get_url.
            
        Raises:
            ValueError: If authentication credentials are missing.
            requests.RequestException: If the API request fails.
        """
        config.validate()
        
        # Ensure we have a valid access token
        if not config.access_token:
            self.authenticate()
        
        # Default options if none provided
        if options is None:
            options = {}
        
        logger.info(f"Calling presign endpoint: {config.presign_endpoint}")
        logger.info(f"Presign options: {options}")
        
        try:
            response = requests.post(
                config.presign_endpoint,
                headers=config.get_auth_headers(),
                json=options
            )
            
            logger.info(f"Presign response status code: {response.status_code}")
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            logger.info(f"Presign successful, job_id: {result.get('job_id', 'unknown')}")
            return result
        except requests.RequestException as e:
            logger.error(f"Presign request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    def upload_file(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Uploading file: {file_path}")
        logger.info(f"File size: {file_path_obj.stat().st_size} bytes")
        
        # Get presigned URLs
        presign_data = self.presign(options)
        
        # Upload file to the put_url
        try:
            with open(file_path_obj, 'rb') as file:
                file_content = file.read()
                file_size = len(file_content)
                
                logger.info(f"Uploading to put_url: {presign_data['put_url']}")
                
                response = requests.put(
                    presign_data['put_url'],
                    data=file_content,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "Content-Length": str(file_size)
                    }
                )
                
                logger.info(f"Upload response status code: {response.status_code}")
                response.raise_for_status()
                logger.info("File upload successful")
        except requests.RequestException as e:
            logger.error(f"File upload failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
        
        return presign_data
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a data curation job.
        
        Args:
            job_id: The job ID to check.
            
        Returns:
            Dict containing job status information.
            
        Raises:
            ValueError: If the access token is missing.
            requests.RequestException: If the API request fails.
        """
        if not config.access_token:
            self.authenticate()
        
        status_url = f"{config.status_endpoint}/{job_id}"
        logger.info(f"Checking job status at: {status_url}")
        
        try:
            response = requests.get(
                status_url,
                headers=config.get_auth_headers()
            )
            
            logger.info(f"Status check response code: {response.status_code}")
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            logger.info(f"Status check result: {result}")
            return result
        except requests.RequestException as e:
            logger.error(f"Status check failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
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
        logger.info(f"Getting results from: {get_url}")
        
        try:
            response = requests.get(get_url)
            logger.info(f"Get results response code: {response.status_code}")
            response.raise_for_status()
            result = str(response.text)
            logger.info(f"Results retrieved, length: {len(result)} characters")
            return result
        except requests.RequestException as e:
            logger.error(f"Get results failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
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
        logger.info(f"Processing file: {file_path}")
        logger.info(f"Options: {options}")
        logger.info(f"Wait for completion: {wait}")
        
        # Upload the file and get URLs
        presign_data = self.upload_file(file_path, options)
        job_id = presign_data['job_id']
        
        if not wait:
            logger.info("Not waiting for results, returning presign data")
            return json.dumps(presign_data)
        
        # Wait for processing to complete
        retries = 0
        while retries < max_retries:
            try:
                # Check job status
                logger.info(f"Checking job status (attempt {retries+1}/{max_retries})")
                status_data = self.check_status(job_id)
                logger.info(f"Job status: {status_data.get('status', 'unknown')}")
                
                if status_data.get('status') == 'Done':
                    # Job is complete, get results
                    logger.info(f"Job complete, retrieving results from: {presign_data['get_url']}")
                    result = self.get_results(presign_data['get_url'])
                    logger.info(f"Results retrieved, length: {len(result)} characters")
                    return result
                
                # Job is still processing, wait and retry
                logger.info(f"Job still processing, waiting {retry_delay} seconds before retry")
                time.sleep(retry_delay)
                retries += 1
            except requests.HTTPError as e:
                if e.response and e.response.status_code == 404:
                    # Resource not ready yet, wait and retry
                    logger.info(f"Resource not ready (404), waiting {retry_delay} seconds before retry")
                    time.sleep(retry_delay)
                    retries += 1
                else:
                    # Other HTTP error
                    logger.error(f"HTTP error while checking status: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        logger.error(f"Response content: {e.response.text}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error while checking status: {str(e)}")
                raise
        
        logger.error(f"Processing timed out after {max_retries} retries")
        raise TimeoutError(f"Processing timed out after {max_retries} retries")
