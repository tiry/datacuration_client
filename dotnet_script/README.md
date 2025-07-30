# Hyland Data Curation API - C# .NET Script

This directory contains a C# script implementation of the Hyland Data Curation API client using [dotnet-script](https://github.com/filipw/dotnet-script). The script can authenticate with the API, upload files, and retrieve curated text results.

## Features

- **Authentication**: OAuth2 client credentials flow
- **File Upload**: Upload files to the Data Curation API
- **Processing**: Wait for file processing completion
- **Results Retrieval**: Download and display curated text
- **Docker Support**: Run without installing .NET Framework locally

## Prerequisites

- Docker (for containerized execution)
- Valid Hyland Data Curation API credentials (client ID and secret)

## Setup

1. **Configure Environment Variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API credentials:
   ```bash
   DATA_CURATION_CLIENT_ID=your_actual_client_id
   DATA_CURATION_CLIENT_SECRET=your_actual_client_secret
   ```

## Usage

### Using Docker (Recommended)

The script is designed to run in a Docker container using the `ghcr.io/filipw/dotnet-script:latest` image, which eliminates the need to install the .NET Framework locally.

#### Basic Usage

Process a file and display results:
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)":/workspace \
  -w /workspace \
  ghcr.io/filipw/dotnet-script:latest \
  datacuration.csx /path/to/your/file.pdf
```

#### Save Results to File

Process a file and save results to an output file:
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)":/workspace \
  -w /workspace \
  ghcr.io/filipw/dotnet-script:latest \
  datacuration.csx /path/to/your/file.pdf output.txt
```

#### Example with Test File

If you have a test PDF file in the repository:
```bash
# From the dotnet_script directory
docker run --rm \
  --env-file .env \
  -v "$(pwd)/..":/workspace \
  -w /workspace/dotnet_script \
  ghcr.io/filipw/dotnet-script:latest \
  datacuration.csx ../tests/data/2412.05958v1.pdf curated_output.txt
```

### Using PowerShell/Windows

For Windows users with PowerShell, you can use the provided PowerShell script:
```powershell
.\run-datacuration.ps1 C:\path\to\your\file.pdf
.\run-datacuration.ps1 C:\path\to\your\file.pdf output.txt
```

Or run Docker directly:
```powershell
docker run --rm `
  --env-file .env `
  -v "${PWD}:/workspace" `
  -w /workspace `
  ghcr.io/filipw/dotnet-script:latest `
  datacuration.csx C:\path\to\your\file.pdf
```

### Helper Scripts

You can also use the provided helper scripts to simplify usage:

**For Linux/macOS (`run-datacuration.sh`):**
```bash
chmod +x run-datacuration.sh
./run-datacuration.sh /path/to/file.pdf output.txt
```

**For Windows (`run-datacuration.ps1`):**
```powershell
.\run-datacuration.ps1 C:\path\to\file.pdf output.txt
```

Both scripts provide:
- Automatic .env file validation
- Input file existence checking
- Colored console output
- Error handling and user-friendly messages

## Script Options

The script currently uses these default processing options:
- **Normalization**: Enabled for quotations and dashes
- **Chunking**: Disabled
- **Embedding**: Disabled
- **JSON Schema**: Disabled (returns plain text)

To customize these options, modify the `options` dictionary in the `datacuration.csx` file.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATA_CURATION_CLIENT_ID` | Yes | - | Your API client ID |
| `DATA_CURATION_CLIENT_SECRET` | Yes | - | Your API client secret |
| `DATA_CURATION_AUTH_ENDPOINT` | No | `https://auth.hyland.com/connect/token` | OAuth2 token endpoint |
| `DATA_CURATION_API_URL` | No | `https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation` | API base URL |

## File Support

The script supports any file type that the Hyland Data Curation API can process, including:
- PDF documents
- Word documents
- Text files
- Images
- Audio files

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Verify your client ID and secret are correct
   - Check that environment variables are properly set
   - Ensure your credentials have the necessary permissions

2. **File Not Found**:
   - Ensure the file path is correct and accessible from within the Docker container
   - Use absolute paths or verify the volume mounting

3. **Network Issues**:
   - Check your internet connection
   - Verify API endpoints are accessible
   - Check for any corporate firewall restrictions

4. **Docker Container Timeout**:
   - Some environments may have slower startup times
   - If the script appears to hang, it might be downloading .NET packages
   - Try running with `--verbose` flag: `docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/filipw/dotnet-script:latest --verbosity debug datacuration.csx`

### Debug Mode

To see more detailed logging, you can modify the script to include additional console output or check the API response details.

### Docker Troubleshooting

Test the Docker image:
```bash
docker run --rm ghcr.io/filipw/dotnet-script:latest --version
```

Check volume mounting:
```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/filipw/dotnet-script:latest ls -la
```

### Testing Script Syntax

You can test if your script has syntax errors by running:
```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace ghcr.io/filipw/dotnet-script:latest --info
```

## API Implementation Details

### Core Functionality

The C# script implements the complete Data Curation API workflow:

1. **OAuth2 Authentication**:
   - Uses client credentials grant type
   - Stores access token for subsequent requests
   - Automatic token refresh when needed

2. **File Processing Pipeline**:
   - Calls `/presign` endpoint to get upload/download URLs
   - Uploads file via PUT request to signed URL
   - Polls `/status/{job_id}` endpoint until completion
   - Downloads results from signed GET URL

3. **Error Handling**:
   - Network timeout handling with retries
   - HTTP error code checking
   - Graceful handling of 404 responses during polling
   - User-friendly error messages

4. **JSON Processing**:
   - Custom lightweight JSON parser to avoid external dependencies
   - Regex-based extraction for simple values
   - Built-in processing options configuration

## API Flow

The script follows this workflow:

1. **Authenticate**: Get OAuth2 access token using client credentials
2. **Presign**: Call presign endpoint to get upload/download URLs
3. **Upload**: Upload file to the presigned PUT URL
4. **Monitor**: Poll status endpoint until processing is complete
5. **Download**: Retrieve results from the presigned GET URL

## Comparison with Python Client

This C# script provides equivalent functionality to the Python client:

| Feature | Python Client | C# Script | Notes |
|---------|---------------|-----------|-------|
| Authentication | ✅ | ✅ | OAuth2 client credentials |
| File Upload | ✅ | ✅ | Presigned URL upload |
| Processing Options | ✅ | ✅ (basic) | Default normalization settings |
| Status Monitoring | ✅ | ✅ | Polling with retry logic |
| Result Retrieval | ✅ | ✅ | From presigned GET URL |
| CLI Interface | ✅ | ✅ (simplified) | Command line arguments |
| Docker Support | - | ✅ | No .NET installation required |
| Error Handling | ✅ | ✅ | Network and API errors |
| Configuration | ✅ | ✅ | Environment variables |

### Key Differences

- **Dependencies**: C# script uses no external packages, Python client uses requests/click
- **JSON Handling**: C# uses custom regex parser, Python uses built-in json module
- **Deployment**: C# runs in Docker container, Python requires local installation
- **Options**: C# has fixed default options, Python supports full customization

## License

This script is part of the datacuration_client project and follows the same MIT license.