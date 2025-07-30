# Helper script to run the Data Curation C# script using Docker on Windows
# Usage: .\run-datacuration.ps1 <file_path> [output_file]

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = ""
)

# Function to write colored output
function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found!"
    Write-Info "Please copy .env.example to .env and configure your API credentials:"
    Write-Info "  Copy-Item .env.example .env"
    Write-Info "  # Edit .env with your actual credentials"
    exit 1
}

# Check if input file exists
if (-not (Test-Path $FilePath)) {
    Write-Error "Input file not found: $FilePath"
    exit 1
}

Write-Info "Starting Data Curation processing..."
Write-Info "Input file: $FilePath"
if ($OutputFile) {
    Write-Info "Output file: $OutputFile"
} else {
    Write-Info "Output: Console"
}

# Build docker command
$dockerArgs = @(
    "run", "--rm",
    "--env-file", ".env",
    "-v", "${PWD}:/workspace",
    "-w", "/workspace",
    "ghcr.io/filipw/dotnet-script:latest",
    "datacuration.csx",
    $FilePath
)

if ($OutputFile) {
    $dockerArgs += $OutputFile
}

Write-Info "Running Docker command..."

# Execute the command
try {
    & docker $dockerArgs
    
    # Check if output file was created
    if ($OutputFile -and (Test-Path $OutputFile)) {
        Write-Info "✅ Processing completed successfully!"
        Write-Info "Results saved to: $OutputFile"
        $fileSize = (Get-Item $OutputFile).Length
        Write-Info "File size: $fileSize bytes"
    } else {
        Write-Info "✅ Processing completed successfully!"
    }
} catch {
    Write-Error "Docker execution failed: $_"
    exit 1
}