"""
Data Curation CLI Tool.

This package provides a command-line interface for interacting with the
Hyland Data Curation API through the datacuration_api library.
"""

__version__ = "0.1.0"

# Import main entry point for easy access
from .cli import main

# Export main entry point
__all__ = ["main"]
