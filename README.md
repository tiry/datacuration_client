# Hyland Data Curation Tools

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
├── tests/                    # Legacy test directory
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
        "chunking": True,
        "embedding": True,
        "normalization": "FULL"
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

## Development

### Build and Test

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy datacuration_api datacuration_cli

# Format code
black datacuration_api datacuration_cli
```

## License

MIT
