"""
Configuration handling for the Data Curation API client.

This module provides functionality to load and manage configuration settings
from environment variables, .env files, and command-line arguments.
"""

import os
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

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
    
    def update(self, **kwargs: Any) -> None:
        """
        Update configuration with provided values.
        
        Args:
            **kwargs: Configuration key-value pairs to update.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
    
    def validate(self) -> None:
        """
        Validate the configuration.
        
        Raises:
            ValueError: If required configuration values are missing.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Client ID and Client Secret are required. Set them using the "
                "DATA_CURATION_CLIENT_ID and DATA_CURATION_CLIENT_SECRET environment "
                "variables or provide them via command-line arguments."
            )
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests with Bearer token authentication.
        
        Returns:
            Dict[str, str]: Headers including authorization and content type.
        """
        if not self.access_token:
            raise ValueError("No access token available. Call authenticate() first.")
            
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
        """
        return {
            "grant_type": "client_credentials",
            "scope": "environment_authorization",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }


# Global configuration instance
config = Config()
