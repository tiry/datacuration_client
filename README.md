# Hyland Data Curation Tools

[![CI](https://github.com/tiry/datacuration_client/actions/workflows/ci.yml/badge.svg)](https://github.com/tiry/datacuration_client/actions/workflows/ci.yml)
[![Integration Tests](https://github.com/tiry/datacuration_client/actions/workflows/integration.yml/badge.svg)](https://github.com/tiry/datacuration_client/actions/workflows/integration.yml)
[![Documentation](https://github.com/tiry/datacuration_client/actions/workflows/docs.yml/badge.svg)](https://tiry.github.io/datacuration_client/)
[![codecov](https://codecov.io/gh/tiry/datacuration_client/branch/master/graph/badge.svg)](https://codecov.io/gh/tiry/datacuration_client)

This repository contains two Python packages for interacting with the Hyland Data Curation API:

1. **datacuration_api**: A Python library that encapsulates the API functionality
2. **datacuration_cli**: A CLI tool that uses the datacuration_api library

The Data Curation API transforms raw, unstructured content into structured data suitable for AI and machine learning applications.

## Project Description

This project provides tools to interact with the Hyland Data Curation API:

- The **datacuration_api** library allows developers to integrate the Data Curation API into their Python applications
- The **datacuration_cli** tool provides a simple command-line interface for end users

These tools enable you to:

1. Upload files to the Data Curation API
2. Retrieve the curated text from the API
3. Configure processing options like normalization, chunking, and embedding

The Data Curation API streamlines the extraction, enrichment, and structuring of content from a wide range of file types, including documents, images, and audio files.

## Project Structure

```
datacuration_client/
├── datacuration_api/         # API library package
│   ├── __init__.py           # Package initialization with version and exports
│   ├── client.py             # API client implementation
│   └── config.py             # Configuration handling
├── datacuration_cli/         # CLI package
│   ├── __init__.py           # Package initialization
│   └── cli.py                # CLI implementation
│   └── tests/                # CLI tests
│       ├── test_cli.py       # Unit tests for CLI
│       └── test_integration.py # Integration tests
├── tests/                    # Test data directory
│   └── data/                 # Test files
│       └── 2412.05958v1.pdf  # Sample PDF for testing
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── .env.example              # Example environment variables
```

## Installation

### Prerequisites

- Python 3.8 or higher
- A valid Hyland Data Curation API token

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd datacuration_client
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```
   pip install -e .
   ```

4. Create a `.env` file with your API token:
   ```
   cp .env.example .env
   # Edit .env to add your API token
   ```

## Usage

### Using the CLI Tool

```bash
# Process a file and retrieve curated text
datacuration process path/to/file.pdf

# Specify output file
datacuration process path/to/file.pdf --output curated_text.txt

# Enable specific processing options
datacuration process path/to/file.pdf --chunking --embedding

# Process with advanced options (using JSON)
datacuration process path/to/file.pdf --options '{"normalization": {"quotations": true, "dashes": true}, "chunking": true, "chunk_size": 1000, "embedding": true}'
```

### Using the API Library

```python
from datacuration_api import DataCurationClient

# Create a client
client = DataCurationClient(client_id="your_id", client_secret="your_secret")

# Process a file with options
result = client.process_file(
    "path/to/file.pdf",
    options={
        "normalization": {
            "quotations": True,
            "dashes": True
        },
        "chunking": True,
        "chunk_size": 1000,
        "embedding": True,
        "json_schema": False
    }
)

# Print or save the result
print(result)
```

### Configuration

You can configure the API endpoint and authentication token using:

1. Environment variables
2. A `.env` file in the current directory
3. Command-line options (for the CLI tool)
4. Direct parameters (for the API library)

## API Processing Options

The Data Curation API supports the following processing options:

### Normalization Options

Control how text is normalized during processing:

```json
"normalization": {
  "quotations": true,  // Normalize different types of quotation marks
  "dashes": true       // Normalize different types of dashes
}
```

### Chunking Options

Control how the document is split into smaller chunks:

```json
"chunking": true,      // Enable document chunking
"chunk_size": 1000     // Target size in characters for each chunk
```

### Embedding Options

Control vector embedding generation:

```json
"embedding": true      // Generate vector embeddings for the document or chunks
```

### Output Format Options

Control the output format:

```json
"json_schema": false   // Return output in a structured JSON format
```

For more detailed information about the API options, see the [API Options Documentation](docs/api_options.md).

## Documentation

API documentation is automatically generated and available at [https://tiry.github.io/datacuration_client/](https://tiry.github.io/datacuration_client/).

## Development

### Build and Test

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests (excluding integration tests)
pytest

# Run integration tests (requires API credentials)
pytest -m integration

# Run specific integration test file
pytest datacuration_cli/tests/test_integration.py

# Run type checking
mypy datacuration_api datacuration_cli

# Format code
black datacuration_api datacuration_cli
```

### Integration Tests

The project includes integration tests that verify the functionality against the actual Data Curation API. These tests:

1. Are marked with `@pytest.mark.integration`
2. Are skipped by default when running `pytest`
3. Require valid API credentials to run
4. Use a real PDF file to test the end-to-end flow

To run integration tests:

1. Ensure you have valid API credentials in your environment or `.env` file
2. Run `pytest -m integration`

The GitHub Actions workflow runs these integration tests automatically using repository secrets for authentication.

## License

MIT
