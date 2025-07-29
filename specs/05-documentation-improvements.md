# Documentation Improvements

## Overview

This specification outlines improvements to the documentation for the Data Curation API client library. The improvements include:

1. Enhanced documentation for the presign endpoint parameters
2. Adding a GitHub Actions workflow to automatically generate Python documentation

## 1. Presign Endpoint Parameters Documentation

The presign endpoint accepts several parameters that control how the data is processed. These parameters need to be better documented in the client library.

### Parameters

The presign endpoint accepts the following parameters:

```json
{
  "normalization": {
    "quotations": true,
    "dashes": true
  },
  "chunking": true,
  "chunk_size": 1000,
  "embedding": true,
  "json_schema": false
}
```

#### Parameter Details

- **normalization**: Controls text normalization options
  - **quotations**: When true, normalizes different types of quotation marks to standard ones
  - **dashes**: When true, normalizes different types of dashes to standard ones

- **chunking**: When true, splits the document into smaller chunks for processing
  - **chunk_size**: The target size (in characters) for each chunk when chunking is enabled

- **embedding**: When true, generates vector embeddings for the document or chunks
  
- **json_schema**: When true, returns the output in a structured JSON format according to a predefined schema

### Implementation Plan

1. Update the docstrings in the `client.py` file to include detailed parameter descriptions
2. Add examples of parameter usage in the README.md
3. Create a separate documentation file with more detailed explanations and examples
4. Update the CLI to support all processing options

## 2. CLI Enhancements

Update the CLI to support all the processing options available in the API.

### Requirements

- Add support for all normalization options (quotations, dashes)
- Add support for chunk_size option
- Add support for json_schema option
- Add support for passing all options as a JSON string
- Update tests to cover the new options

### Implementation Plan

1. Update the CLI to add new options
2. Add support for parsing JSON options
3. Update the tests to cover the new options

## 3. GitHub Actions Workflow for Documentation Generation

Add a GitHub Actions workflow to automatically generate Python documentation using Sphinx or pdoc3.

### Requirements

- Generate HTML documentation from docstrings
- Deploy the documentation to GitHub Pages
- Run the documentation generation on each push to the main branch
- Include a badge in the README.md to link to the documentation

### Implementation Plan

1. Add necessary dependencies to pyproject.toml (Sphinx or pdoc3)
2. Create a documentation configuration file
3. Create a GitHub Actions workflow file
4. Update the README.md with a badge linking to the documentation

## Success Criteria

- Comprehensive documentation for the presign endpoint parameters
- Enhanced CLI with support for all processing options
- Automatically generated API documentation available on GitHub Pages
- Clear examples of how to use the parameters in the README.md
- All tests passing with the new options
