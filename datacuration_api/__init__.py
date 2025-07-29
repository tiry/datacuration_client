"""
Hyland Data Curation API Client Library.

This package provides a Python client for interacting with the Hyland Data Curation API,
allowing for file processing, text extraction, and data enrichment.
"""

__version__ = "0.1.0"

# Import main components for easy access
from .client import DataCurationClient
from .config import config

# Export main components
__all__ = ["DataCurationClient", "config"]
