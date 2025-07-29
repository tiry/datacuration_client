# Adding GitHub Actions CI Workflow

## Overview

This specification outlines the plan to add a GitHub Actions workflow for continuous integration (CI) to the datacuration_client repository. The workflow will automate the build and testing process, ensuring that code changes maintain quality and functionality.

## Objectives

1. Create a GitHub Actions workflow that:
   - Runs on push to main branch and pull requests
   - Tests the code on multiple Python versions
   - Runs linting and type checking
   - Reports test coverage

2. Update the README.md to display build status badges

## Implementation Plan

### 1. Create GitHub Actions Workflow File

Create a new file at `.github/workflows/ci.yml` with the following configuration:

```yaml
name: CI

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 datacuration_api datacuration_cli --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 datacuration_api datacuration_cli --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    - name: Type check with mypy
      run: |
        mypy datacuration_api datacuration_cli
    - name: Test with pytest
      run: |
        pytest --cov=datacuration_api --cov=datacuration_cli --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

### 2. Update Dependencies

Add pytest-cov to the development dependencies in pyproject.toml:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
]
```

### 3. Update README.md

Add build status badges to the README.md:

```markdown
# Hyland Data Curation Tools

[![CI](https://github.com/tiry/datacuration_client/actions/workflows/ci.yml/badge.svg)](https://github.com/tiry/datacuration_client/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tiry/datacuration_client/branch/master/graph/badge.svg)](https://codecov.io/gh/tiry/datacuration_client)

This repository contains two Python packages for interacting with the Hyland Data Curation API:
...
```

## Success Criteria

1. GitHub Actions workflow runs successfully on push and pull requests
2. Tests run on multiple Python versions
3. Linting and type checking are performed
4. Test coverage is reported
5. README.md displays build status badges

## Timeline

- Create GitHub Actions workflow file: 30 minutes
- Update dependencies: 10 minutes
- Update README.md: 10 minutes
- Test and verify: 20 minutes

Total estimated time: 1-2 hours
