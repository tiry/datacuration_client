# Data Curation API Processing Options

This document provides detailed information about the processing options available in the Data Curation API.

## Overview

The Data Curation API allows you to customize how your documents are processed through various options. These options can be specified when calling the `presign` endpoint or when using the `process_file` method in the client library.

## Option Structure

The options are provided as a JSON object with the following structure:

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

## Detailed Options

### Normalization Options

Normalization options control how the text is standardized during processing.

#### `normalization.quotations` (boolean)

When set to `true`, different types of quotation marks are normalized to standard ones.

- **Default**: `true`
- **Example**: Converts curly quotes (`"example"`) and other quote variants to straight quotes (`"example"`)

#### `normalization.dashes` (boolean)

When set to `true`, different types of dashes are normalized to standard ones.

- **Default**: `true`
- **Example**: Converts em dashes (—), en dashes (–), and other dash variants to standard hyphens (-)

### Chunking Options

Chunking options control how the document is split into smaller pieces for processing.

#### `chunking` (boolean)

When set to `true`, the document is split into smaller chunks for processing.

- **Default**: `false`
- **Purpose**: Breaking large documents into smaller, more manageable pieces can improve processing efficiency and enable more granular analysis.

#### `chunk_size` (integer)

The target size (in characters) for each chunk when chunking is enabled.

- **Default**: `1000`
- **Range**: 100-5000
- **Note**: The actual chunk size may vary slightly as the system tries to break at natural boundaries like paragraphs or sentences.

### Embedding Options

Embedding options control the generation of vector embeddings for the document.

#### `embedding` (boolean)

When set to `true`, vector embeddings are generated for the document or chunks.

- **Default**: `false`
- **Purpose**: Vector embeddings enable semantic search, similarity comparisons, and other machine learning applications.

### Output Format Options

Output format options control how the processed data is returned.

#### `json_schema` (boolean)

When set to `true`, the output is returned in a structured JSON format according to a predefined schema.

- **Default**: `false`
- **Purpose**: Structured output is easier to parse and integrate into downstream applications.
- **Note**: When set to `false`, the output is returned as plain text.

## Usage Examples

### Basic Processing

```python
options = {
    "normalization": {
        "quotations": True,
        "dashes": True
    }
}
```

### Processing with Chunking

```python
options = {
    "normalization": {
        "quotations": True,
        "dashes": True
    },
    "chunking": True,
    "chunk_size": 1000
}
```

### Processing with Embeddings

```python
options = {
    "normalization": {
        "quotations": True,
        "dashes": True
    },
    "embedding": True
}
```

### Full Processing with JSON Output

```python
options = {
    "normalization": {
        "quotations": True,
        "dashes": True
    },
    "chunking": True,
    "chunk_size": 1000,
    "embedding": True,
    "json_schema": True
}
```

## CLI Usage

When using the CLI tool, you can specify these options using the `--options` flag with a JSON string:

```bash
datacuration process path/to/file.pdf --options '{"normalization": {"quotations": true, "dashes": true}, "chunking": true, "chunk_size": 1000, "embedding": true}'
```

Or use the individual flags for common options:

```bash
datacuration process path/to/file.pdf --chunking --embedding
```

## API Reference

For more details on the API endpoints and parameters, refer to the [official Hyland Knowledge Enrichment documentation](https://hyland.github.io/ContentIntelligence-Docs/KnowledgeEnrichment/DataCurationAPI/Tutorials/UsingTheAPI).
