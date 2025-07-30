#!/bin/bash

# Helper script to run the Data Curation C# script using Docker
# Usage: ./run-datacuration.sh <file_path> [output_file]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_info "Please copy .env.example to .env and configure your API credentials:"
    print_info "  cp .env.example .env"
    print_info "  # Edit .env with your actual credentials"
    exit 1
fi

# Check if file argument is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <file_path> [output_file]"
    print_info ""
    print_info "Examples:"
    print_info "  $0 document.pdf"
    print_info "  $0 document.pdf output.txt"
    print_info "  $0 ../tests/data/2412.05958v1.pdf curated_output.txt"
    exit 1
fi

FILE_PATH="$1"
OUTPUT_FILE="${2:-}"

# Check if input file exists
if [ ! -f "$FILE_PATH" ]; then
    print_error "Input file not found: $FILE_PATH"
    exit 1
fi

# Get absolute path of the input file and its directory
FILE_ABSOLUTE=$(realpath "$FILE_PATH")
FILE_DIR=$(dirname "$FILE_ABSOLUTE")
FILE_NAME=$(basename "$FILE_ABSOLUTE")

print_info "Starting Data Curation processing..."
print_info "Input file: $FILE_PATH"
print_info "Resolved to: $FILE_ABSOLUTE"
if [ -n "$OUTPUT_FILE" ]; then
    print_info "Output file: $OUTPUT_FILE"
else
    print_info "Output: Console"
fi

# Build docker command with two volume mounts:
# 1. Current directory to /workspace (for scripts and output files)
# 2. File directory to /input (for input file access)
DOCKER_CMD="docker run --rm \
  --env-file .env \
  -v \"$(pwd):/workspace\" \
  -v \"$FILE_DIR:/input\" \
  -w /workspace \
  ghcr.io/filipw/dotnet-script:latest \
  datacuration.csx"

# Add arguments - use /input/filename for the input file path inside container
if [ -n "$OUTPUT_FILE" ]; then
    DOCKER_CMD="$DOCKER_CMD \"/input/$FILE_NAME\" \"$OUTPUT_FILE\""
else
    DOCKER_CMD="$DOCKER_CMD \"/input/$FILE_NAME\""
fi

print_info "Running Docker command..."

# Execute the command
eval $DOCKER_CMD

# Check if output file was created
if [ -n "$OUTPUT_FILE" ] && [ -f "$OUTPUT_FILE" ]; then
    print_info "✅ Processing completed successfully!"
    print_info "Results saved to: $OUTPUT_FILE"
    print_info "File size: $(wc -c < "$OUTPUT_FILE") bytes"
else
    print_info "✅ Processing completed successfully!"
fi