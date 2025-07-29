"""
Command-line interface for the Data Curation API client.

This module provides a CLI for interacting with the Hyland Data Curation API,
allowing users to process files and retrieve curated text.
"""

import sys
import json
from typing import Optional, Dict, Any
import click
from pathlib import Path

from datacuration_api import DataCurationClient
from datacuration_api import config
from datacuration_cli import __version__


@click.group()
@click.option(
    "--client-id", 
    envvar="DATA_CURATION_CLIENT_ID",
    help="Client ID for authentication. Can also be set via DATA_CURATION_CLIENT_ID environment variable."
)
@click.option(
    "--client-secret", 
    envvar="DATA_CURATION_CLIENT_SECRET",
    help="Client Secret for authentication. Can also be set via DATA_CURATION_CLIENT_SECRET environment variable."
)
@click.option(
    "--api-url", 
    envvar="DATA_CURATION_API_URL",
    help="Base URL for the Data Curation API. Can also be set via DATA_CURATION_API_URL environment variable."
)
@click.option(
    "--auth-url", 
    envvar="DATA_CURATION_AUTH_ENDPOINT",
    help="Authentication endpoint URL. Can also be set via DATA_CURATION_AUTH_ENDPOINT environment variable."
)
@click.version_option(version=__version__, package_name="datacuration")
def cli(client_id: Optional[str], client_secret: Optional[str], api_url: Optional[str], auth_url: Optional[str]) -> None:
    """
    Data Curation API Client
    
    A command-line tool for processing files through the Hyland Data Curation API.
    """
    if client_id:
        config.update(client_id=client_id)
    if client_secret:
        config.update(client_secret=client_secret)
    if api_url:
        config.update(api_base_url=api_url)
        config.update(presign_endpoint=f"{api_url}/presign")
        config.update(status_endpoint=f"{api_url}/status")
    if auth_url:
        config.update(auth_endpoint=auth_url)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path. If not provided, output will be printed to stdout."
)
@click.option(
    "--chunking/--no-chunking",
    default=None,
    help="Enable/disable content chunking."
)
@click.option(
    "--chunk-size",
    type=int,
    default=None,
    help="Target size in characters for each chunk when chunking is enabled."
)
@click.option(
    "--embedding/--no-embedding",
    default=None,
    help="Enable/disable content embedding."
)
@click.option(
    "--normalize-quotations/--no-normalize-quotations",
    default=None,
    help="Enable/disable normalization of quotation marks."
)
@click.option(
    "--normalize-dashes/--no-normalize-dashes",
    default=None,
    help="Enable/disable normalization of dashes."
)
@click.option(
    "--json-schema/--no-json-schema",
    default=None,
    help="Enable/disable structured JSON output format."
)
@click.option(
    "--options",
    type=str,
    help="JSON string with all processing options. Overrides individual option flags."
)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Don't wait for processing to complete, just return the job details."
)
@click.option(
    "--max-retries",
    type=int,
    default=10,
    help="Maximum number of retries when waiting for results."
)
@click.option(
    "--retry-delay",
    type=int,
    default=2,
    help="Delay between retries in seconds."
)
def process(
    file_path: str,
    output: Optional[str],
    chunking: Optional[bool],
    chunk_size: Optional[int],
    embedding: Optional[bool],
    normalize_quotations: Optional[bool],
    normalize_dashes: Optional[bool],
    json_schema: Optional[bool],
    options: Optional[str],
    no_wait: bool,
    max_retries: int,
    retry_delay: int,
) -> None:
    """
    Process a file through the Data Curation API.
    
    FILE_PATH is the path to the file to process.
    
    Use individual option flags for basic configuration or the --options flag
    with a JSON string for advanced configuration. The --options flag overrides
    individual option flags.
    """
    # Parse options from JSON string if provided
    if options:
        try:
            options_dict: Dict[str, Any] = json.loads(options)
            click.echo(f"Using options from JSON: {json.dumps(options_dict, indent=2)}")
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing options JSON: {str(e)}", err=True)
            sys.exit(1)
    else:
        # Build options dictionary from provided flags
        options_dict = {}
        
        # Handle normalization options
        if normalize_quotations is not None or normalize_dashes is not None:
            options_dict["normalization"] = {}
            
            if normalize_quotations is not None:
                options_dict["normalization"]["quotations"] = normalize_quotations
                
            if normalize_dashes is not None:
                options_dict["normalization"]["dashes"] = normalize_dashes
        
        # Handle chunking options
        if chunking is not None:
            options_dict["chunking"] = chunking
            
        if chunk_size is not None:
            options_dict["chunk_size"] = chunk_size
        
        # Handle embedding options
        if embedding is not None:
            options_dict["embedding"] = embedding
        
        # Handle output format options
        if json_schema is not None:
            options_dict["json_schema"] = json_schema
    
    try:
        client = DataCurationClient()
        result = client.process_file(
            file_path,
            options=options_dict,
            wait=not no_wait,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        if output:
            with open(output, "w") as f:
                f.write(result)
            click.echo(f"Results saved to {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
