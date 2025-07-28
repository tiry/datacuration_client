# Data Curation API Client

A Python CLI client for the Hyland Data Curation API that transforms raw, unstructured content into structured data suitable for AI and machine learning applications.

## Project Description

This client provides a simple command-line interface to interact with the Hyland Data Curation API. It allows users to:

1. Upload files to the Data Curation API
2. Retrieve the curated text from the API
3. Configure processing options like normalization, chunking, and embedding

The Data Curation API streamlines the extraction, enrichment, and structuring of content from a wide range of file types, including documents, images, and audio files.

## Project Structure

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
   cd data_curation_client
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

### Basic Usage

```bash
# Process a file and retrieve curated text
data-curation process path/to/file.pdf

# Specify output file
data-curation process path/to/file.pdf --output curated_text.txt

# Enable specific processing options
data-curation process path/to/file.pdf --chunking --embedding
```

### Configuration

You can configure the API endpoint and authentication token using:

1. Environment variables
2. A `.env` file in the current directory
3. Command-line options

## Development

### Build and Test

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy data_curation_client

# Format code
black data_curation_client tests
```

## License

MIT
