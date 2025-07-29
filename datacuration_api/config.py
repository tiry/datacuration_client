"""
Configuration handling for the Data Curation API client.

This module provides functionality to load and manage configuration settings
from environment variables, .env files, and command-line arguments.
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Default API endpoints
DEFAULT_API_BASE_URL = "https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation"
DEFAULT_PRESIGN_ENDPOINT = f"{DEFAULT_API_BASE_URL}/presign"
DEFAULT_STATUS_ENDPOINT = f"{DEFAULT_API_BASE_URL}/status"
DEFAULT_AUTH_ENDPOINT = "https://auth.hyland.com/connect/token"

class Config:
    """Configuration manager for the Data Curation API client."""
    
    def __init__(self) -> None:
        """Initialize the configuration with default values."""
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        self.api_base_url: str = os.getenv("DATA_CURATION_API_URL", DEFAULT_API_BASE_URL)
        self.presign_endpoint: str = os.getenv("DATA_CURATION_PRESIGN_ENDPOINT", DEFAULT_PRESIGN_ENDPOINT)
        self.status_endpoint: str = os.getenv("DATA_CURATION_STATUS_ENDPOINT", DEFAULT_STATUS_ENDPOINT)
        self.auth_endpoint: str = os.getenv("DATA_CURATION_AUTH_ENDPOINT", DEFAULT_AUTH_ENDPOINT)
        self.client_id: Optional[str] = os.getenv("DATA_CURATION_CLIENT_ID")
        self.client_secret: Optional[str] = os.getenv("DATA_CURATION_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[int] = None
        
        # Log configuration (masking sensitive values)
        logger.info("Configuration initialized:")
        logger.info(f"API Base URL: {self.api_base_url}")
        logger.info(f"Presign Endpoint: {self.presign_endpoint}")
        logger.info(f"Status Endpoint: {self.status_endpoint}")
        logger.info(f"Auth Endpoint: {self.auth_endpoint}")
        logger.info(f"Client ID: {'*' * 5 if self.client_id else 'not set'}")
        logger.info(f"Client Secret: {'*' * 5 if self.client_secret else 'not set'}")
    
    def update(self, **kwargs: Any) -> None:
        """
        Update configuration with provided values.
        
        Args:
            **kwargs: Configuration key-value pairs to update.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                logger.info(f"Updating config: {key} = {'*' * 5 if key in ['client_id', 'client_secret', 'access_token'] else value}")
                setattr(self, key, value)
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ValueError: If required configuration values are missing.
        """
        logger.info("Validating configuration...")
        
        missing = []
        if not self.client_id:
            missing.append("Client ID")
        if not self.client_secret:
            missing.append("Client Secret")
            
        if missing:
            error_msg = (
                f"Missing required configuration: {', '.join(missing)}. Set them using the "
                "DATA_CURATION_CLIENT_ID and DATA_CURATION_CLIENT_SECRET environment "
                "variables or provide them via command-line arguments."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation successful")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests with Bearer token authentication.
        
        Returns:
            Dict[str, str]: Headers including authorization and content type.
        """
        if not self.access_token:
            logger.error("No access token available. Call authenticate() first.")
            raise ValueError("No access token available. Call authenticate() first.")
        
        logger.debug("Creating auth headers with access token")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "text/json",
        }
    
    def get_token_request_data(self) -> Dict[str, str]:
        """
        Get the request data for token authentication.
        
        Returns:
            Dict[str, str]: Form data for token request.
            
        Raises:
            ValueError: If client_id or client_secret is not set.
        """
        logger.debug("Preparing token request data")
        
        missing = []
        if not self.client_id:
            missing.append("Client ID")
        if not self.client_secret:
            missing.append("Client Secret")
            
        if missing:
            error_msg = f"Missing required authentication credentials: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.debug("Token request data prepared successfully")
        return {
            "grant_type": "client_credentials",
            "scope": "environment_authorization",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }


# Global configuration instance
config = Config()
