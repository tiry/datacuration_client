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

from .api import DataCurationAPIClient
from .config import config


@click.group()
@click.option(
    "--api-token", 
    envvar="DATA_CURATION_API_TOKEN",
    help="API token for authentication. Can also be set via DATA_CURATION_API_TOKEN environment variable."
)
@click.option(
    "--api-url", 
    envvar="DATA_CURATION_API_URL",
    help="Base URL for the Data Curation API. Can also be set via DATA_CURATION_API_URL environment variable."
)
@click.version_option()
def cli(api_token: Optional[str], api_url: Optional[str]) -> None:
    """
    Data Curation API Client
    
    A command-line tool for processing files through the Hyland Data Curation API.
    """
    if api_token:
        config.update(api_token=api_token)
    if api_url:
        config.update(api_base_url=api_url)
        config.update(presign_endpoint=f"{api_url}/presign")


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
    "--embedding/--no-embedding",
    default=None,
    help="Enable/disable content embedding."
)
@click.option(
    "--normalization",
    type=str,
    help="Normalization type (MDAST, FULL, PIPELINE)."
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
    embedding: Optional[bool],
    normalization: Optional[str],
    no_wait: bool,
    max_retries: int,
    retry_delay: int,
) -> None:
    """
    Process a file through the Data Curation API.
    
    FILE_PATH is the path to the file to process.
    """
    # Build options dictionary from provided flags
    options: Dict[str, Any] = {}
    
    if chunking is not None:
        options["chunking"] = chunking
    
    if embedding is not None:
        options["embedding"] = embedding
    
    if normalization:
        options["normalization"] = normalization
    
    try:
        client = DataCurationAPIClient()
        result = client.process_file(
            file_path,
            options=options,
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
