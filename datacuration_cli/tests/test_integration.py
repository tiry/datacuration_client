"""
Integration tests for the Data Curation CLI.

These tests use the actual Data Curation API endpoints and require valid credentials.
They are marked as integration tests and are not run by default.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from datacuration_cli.cli import cli


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def runner() -> CliRunner:
    """Fixture to create a CLI runner."""
    return CliRunner(env=os.environ)


@pytest.fixture
def pdf_file() -> str:
    """Fixture to get the path to the test PDF file."""
    # The PDF file is in the tests/data directory
    pdf_path = Path(__file__).parent.parent.parent / "tests" / "data" / "2412.05958v1.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test PDF file not found at {pdf_path}")
    return str(pdf_path)


@pytest.fixture
def load_env() -> dict:
    """Fixture to load environment variables from .env file if present."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        # Use python-dotenv to load the .env file
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
    
    # Check if required environment variables are set
    required_vars = [
        "DATA_CURATION_CLIENT_ID",
        "DATA_CURATION_CLIENT_SECRET",
        "DATA_CURATION_AUTH_ENDPOINT"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Return environment variables needed for the test
    return {
        "DATA_CURATION_CLIENT_ID": os.environ.get("DATA_CURATION_CLIENT_ID", ""),
        "DATA_CURATION_CLIENT_SECRET": os.environ.get("DATA_CURATION_CLIENT_SECRET", ""),
        "DATA_CURATION_AUTH_ENDPOINT": os.environ.get("DATA_CURATION_AUTH_ENDPOINT", ""),
        "DATA_CURATION_API_URL": os.environ.get("DATA_CURATION_API_URL", "")
    }


@pytest.mark.integration
def test_process_pdf_file(runner: CliRunner, pdf_file: str, load_env: dict) -> None:
    """Test processing a PDF file with the actual API."""
    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        # Run the CLI command to process the PDF file with environment variables
        result = runner.invoke(
            cli, 
            [
                "--client-id", load_env["DATA_CURATION_CLIENT_ID"],
                "--client-secret", load_env["DATA_CURATION_CLIENT_SECRET"],
                "--auth-url", load_env["DATA_CURATION_AUTH_ENDPOINT"],
                "--api-url", load_env["DATA_CURATION_API_URL"] or "https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation",
                "process",
                pdf_file,
                "--output", output_path
            ]
        )
        
        # Check that the command executed successfully
        assert result.exit_code == 0, f"Command failed with output: {result.output}"
        
        # Check that the output file was created
        assert Path(output_path).exists(), "Output file was not created"
        
        # Load the output file and check its content
        with open(output_path, "r") as f:
            output_content = f.read()
        
        # Verify that the output contains some expected content
        # This will depend on the actual PDF content and API behavior
        assert output_content, "Output file is empty"
        
        # Try to parse the output as JSON to verify it's valid
        try:
            output_json = json.loads(output_content)
            # Check for some expected keys in the JSON response
            assert isinstance(output_json, dict), "Output is not a valid JSON object"
        except json.JSONDecodeError:
            # If it's not JSON, it should be text content
            assert len(output_content) > 0, "Output content is empty"
    
    finally:
        # Clean up the temporary file
        if Path(output_path).exists():
            Path(output_path).unlink()
