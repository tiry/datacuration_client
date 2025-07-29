# Splitting Data Curation Client into Library and CLI

## Overview

This specification outlines the plan to refactor the existing Data Curation Client into two separate components:

1. **datacuration_api**: A Python library that encapsulates the API functionality
2. **datacuration_cli**: A CLI tool that uses the datacuration_api library

This separation follows good software design principles by:
- Creating a clear separation of concerns
- Making the API library reusable in other projects
- Allowing independent versioning and development of the API client and CLI tool

## Current Structure

```
datacuration_client/
├── data_curation_client/     # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── api.py                # API client implementation
│   ├── cli.py                # Command-line interface
│   └── config.py             # Configuration handling
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── test_api.py           # API tests
│   └── test_cli.py           # CLI tests
├── pyproject.toml            # Project dependencies and metadata
├── README.md                 # Project documentation
└── .env.example              # Example environment variables
```

## New Structure

```
datacuration_client/
├── datacuration_api/         # API library package
│   ├── __init__.py           # Package initialization with version and exports
│   ├── client.py             # API client implementation (from current api.py)
│   └── config.py             # Configuration handling (from current config.py)
├── datacuration_cli/         # CLI package
│   ├── __init__.py           # Package initialization
│   └── cli.py                # CLI implementation (from current cli.py)
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── test_api.py           # API tests (updated imports)
│   └── test_cli.py           # CLI tests (updated imports)
├── pyproject.toml            # Updated project configuration
├── README.md                 # Updated documentation
└── .env.example              # Example environment variables
```

## Implementation Plan

### 1. Create the API Library Package

- Create the `datacuration_api` directory and files
- Move the API client code from `api.py` to `datacuration_api/client.py`
- Move the configuration code from `config.py` to `datacuration_api/config.py`
- Update imports and references
- Create a proper `__init__.py` that exports the main classes and functions

### 2. Create the CLI Package

- Create the `datacuration_cli` directory and files
- Move the CLI code from `cli.py` to `datacuration_cli/cli.py`
- Update imports to use the new API library
- Create a proper `__init__.py`

### 3. Update Project Configuration

- Update `pyproject.toml` to define both packages
- Define dependencies correctly (CLI depends on API)
- Update entry points for the CLI tool

### 4. Update Tests

- Update test imports to use the new package structure
- Ensure tests still work with the new structure

### 5. Update Documentation

- Update the README to reflect the new structure and usage
- Document how to use the API library separately from the CLI

## API Library Interface

The API library will expose the following main components:

```python
# Main client class
from datacuration_api import DataCurationClient

# Configuration
from datacuration_api import config

# Create a client
client = DataCurationClient(client_id="your_id", client_secret="your_secret")

# Process a file
result = client.process_file("path/to/file.pdf", options={"chunking": True})
```

## CLI Usage

The CLI usage will remain the same:

```bash
# Process a file
datacuration process path/to/file.pdf --chunking --embedding
```

## Migration Notes

- The API library will be backward compatible with the current API
- The CLI will maintain the same interface and functionality
- Existing scripts using the API directly will need to update their imports
