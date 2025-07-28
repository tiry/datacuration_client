# Data Curation API CLI Client Implementation

## Overview

This specification outlines the implementation of a Python CLI client for the Hyland Data Curation API. The client will allow users to upload files to the API and retrieve the curated text.

## Requirements

1. Create a Python CLI client that can:
   - Upload files to the Data Curation API
   - Retrieve the curated text from the API
   - Configure processing options like normalization, chunking, and embedding

2. Follow Python best practices:
   - Use a virtual environment
   - Define dependencies in pyproject.toml
   - Include proper documentation and type hinting
   - Implement unit tests with pytest

## API Workflow

Based on the Data Curation API documentation, the workflow is:

1. Get an access token (JWT Bearer Token)
2. Call the presign endpoint to get:
   - job_id
   - put_url
   - get_url
3. Upload the file to the put_url
4. (Optional) Check job status using job_id
5. Retrieve the results from the get_url once processing is complete

## Implementation Plan

### 1. Project Structure

```
data_curation_client/
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

### 2. Configuration Module

The `config.py` module will:
- Load configuration from environment variables and .env files
- Store API endpoints and authentication tokens
- Provide methods to validate configuration and generate request headers

### 3. API Client Module

The `api.py` module will:
- Implement the DataCurationAPIClient class
- Provide methods to interact with the API:
  - presign: Call the presign endpoint to get URLs
  - upload_file: Upload a file to the put_url
  - get_results: Retrieve results from the get_url
  - process_file: Combine the above steps into a single method

### 4. CLI Module

The `cli.py` module will:
- Use the Click library to create a command-line interface
- Provide commands to process files and configure options
- Handle errors and display appropriate messages

### 5. Testing

The tests will:
- Use pytest for unit testing
- Mock API responses to test functionality without making actual API calls
- Test both the API client and CLI interface

## CLI Usage Examples

```bash
# Process a file and retrieve curated text
data-curation process path/to/file.pdf

# Specify output file
data-curation process path/to/file.pdf --output curated_text.txt

# Enable specific processing options
data-curation process path/to/file.pdf --chunking --embedding

# Specify normalization type
data-curation process path/to/file.pdf --normalization FULL
```

## Future Enhancements

Potential future enhancements include:
- Support for batch processing multiple files
- Progress indicators for long-running operations
- Interactive mode for exploring API options
- Support for additional API endpoints as they become available
