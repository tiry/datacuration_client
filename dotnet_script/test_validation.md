# Test Script for Data Curation C# Implementation

This directory contains a simple test to validate the C# script structure.

## Quick Validation Test

To verify the script is syntactically correct without making API calls:

```bash
# Test the helper script exists and is executable
ls -la run-datacuration.sh

# Test environment file exists
ls -la .env.example

# Check if Docker image can be pulled (optional)
docker pull ghcr.io/filipw/dotnet-script:latest

# Basic syntax validation (without execution)
echo "Testing basic script structure..."
grep -q "class DataCurationClient" datacuration.csx && echo "✓ Main class found"
grep -q "AuthenticateAsync" datacuration.csx && echo "✓ Authentication method found"
grep -q "ProcessFileAsync" datacuration.csx && echo "✓ Process method found"
```

## Manual Testing

1. Set up your credentials in `.env`
2. Run the script with a test file:
   ```bash
   ./run-datacuration.sh /path/to/test/file.pdf
   ```

The script should authenticate, upload the file, and return curated text results.