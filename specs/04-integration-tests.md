# Integration Tests for Data Curation Client

## Overview

This specification outlines the implementation of integration tests for the Data Curation Client. These tests will verify that the client can successfully interact with the actual Data Curation API endpoints.

## Requirements

1. Create integration tests that use the actual Data Curation API endpoints
2. Use a real PDF file for testing
3. Configure the tests to use environment variables for authentication
4. Mark the tests as integration tests that are not run by default
5. Create a GitHub Actions workflow to run the integration tests

## Implementation Details

### Test Data

- Add a PDF file to the `tests/data` directory for use in integration tests
- The file should be small enough to be included in the repository but representative of real-world usage

### Integration Test

- Create a new test file `test_integration.py` in the `datacuration_cli/tests` directory
- Implement a test that:
  - Loads environment variables from a `.env` file if present
  - Uses the CLI to process a PDF file
  - Captures the CLI output and verifies it contains the expected data
  - Tests the end-to-end flow from CLI to API and back

### Test Configuration

- Mark the integration tests with a pytest marker: `@pytest.mark.integration`
- Configure pytest to skip integration tests by default
- Add documentation on how to run the integration tests

### GitHub Actions Workflow

- Create a new workflow file `.github/workflows/integration.yml`
- Configure the workflow to:
  - Run on push to the main branch and pull requests
  - Use the repository secrets for authentication
  - Run only the integration tests

## Success Criteria

- Integration tests successfully authenticate with the Data Curation API
- Tests process a PDF file and verify the response
- Tests are skipped by default when running the regular test suite
- GitHub Actions workflow successfully runs the integration tests using repository secrets

## References

- [Data Curation API Documentation](https://example.com/api-docs)
- [pytest Documentation on Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
