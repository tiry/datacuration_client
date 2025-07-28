"""
Configuration handling for the Data Curation API client.

This module provides functionality to load and manage configuration settings
from environment variables, .env files, and command-line arguments.
"""

import os
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Default API endpoint
DEFAULT_API_BASE_URL = "https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation"
DEFAULT_PRESIGN_ENDPOINT = f"{DEFAULT_API_BASE_URL}/presign"

class Config:
    """Configuration manager for the Data Curation API client."""
    
    def __init__(self) -> None:
        """Initialize the configuration with default values."""
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        self.api_base_url: str = os.getenv("DATA_CURATION_API_URL", DEFAULT_API_BASE_URL)
        self.presign_endpoint: str = os.getenv("DATA_CURATION_PRESIGN_ENDPOINT", DEFAULT_PRESIGN_ENDPOINT)
        self.api_token: Optional[str] = os.getenv("DATA_CURATION_API_TOKEN")
    
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
        if not self.api_token:
            raise ValueError(
                "API token is required. Set it using the DATA_CURATION_API_TOKEN "
                "environment variable or provide it via command-line arguments."
            )
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Returns:
            Dict[str, str]: Headers including authorization and content type.
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "text/json",
        }


# Global configuration instance
config = Config()
