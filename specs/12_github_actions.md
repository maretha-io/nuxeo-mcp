# GitHub Actions Workflows for Nuxeo MCP

This specification outlines the GitHub Actions workflows for the Nuxeo MCP project.

## Overview

We will create two GitHub Actions workflows:

1. **Build and Unit Tests**: This workflow will build the project and run unit tests.
2. **Integration Tests**: This workflow will start the Nuxeo Docker image and run integration tests.

## Build and Unit Tests Workflow

The Build and Unit Tests workflow will:

1. Check out the code
2. Set up Python
3. Install dependencies
4. Run the build process
5. Execute unit tests

This workflow will run on push to the main branch and on pull requests.

## Integration Tests Workflow

The Integration Tests workflow will:

1. Check out the code
2. Set up Python
3. Install dependencies
4. Authenticate with the Nuxeo Docker registry
5. Pull the Nuxeo Docker image
6. Run integration tests

This workflow will also run on push to the main branch and on pull requests.

## Authentication for Nuxeo Docker Registry

The Integration Tests workflow will need to authenticate with the Nuxeo Docker registry to pull the Nuxeo Docker image. The authentication credentials will be stored as GitHub secrets:

- `NUXEO_DOCKER_USERNAME`: The username for the Nuxeo Docker registry
- `NUXEO_DOCKER_PASSWORD`: The password for the Nuxeo Docker registry

## Docker Client Configuration

The `conftest.py` file will be updated to make the Docker client creation more generic, allowing for a switch between standard Docker and Rancher/Moby. This will be controlled by an environment variable or a command-line option.

## Implementation Details

### Build and Unit Tests Workflow

```yaml
name: Build and Unit Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        
    - name: Build
      run: |
        python -m build
        
    - name: Run unit tests
      run: |
        python -m pytest tests/ -v --no-integration
```

### Integration Tests Workflow

```yaml
name: Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        
    - name: Login to Nuxeo Docker Registry
      uses: docker/login-action@v2
      with:
        registry: docker-private.packages.nuxeo.com
        username: ${{ secrets.NUXEO_DOCKER_USERNAME }}
        password: ${{ secrets.NUXEO_DOCKER_PASSWORD }}
        
    - name: Pull Nuxeo Docker Image
      run: |
        docker pull docker-private.packages.nuxeo.com/nuxeo/nuxeo:2025
        
    - name: Run integration tests
      run: |
        python -m pytest tests/ -v --integration
```

### Updated conftest.py

The `conftest.py` file will be updated to make the Docker client creation more generic:

```python
import os
import pytest
import docker

def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that require external services like Nuxeo",
    )
    parser.addoption(
        "--rancher",
        action="store_true",
        default=False,
        help="Use Rancher Desktop Docker socket",
    )

@pytest.fixture(scope="session")
def docker_client(request):
    """Create a Docker client."""
    # Check if we should use Rancher Desktop Docker socket
    use_rancher = request.config.getoption("--rancher") or os.environ.get("USE_RANCHER", "").lower() in ("true", "1", "yes")
    
    if use_rancher:
        # Use the Docker socket location for Rancher Desktop
        return docker.DockerClient(base_url="unix:///Users/thierry.delprat/.rd/docker.sock")
    else:
        # Use the default Docker socket location
        return docker.DockerClient()
```

## Usage

### Running Unit Tests

```bash
python -m pytest tests/ -v --no-integration
```

### Running Integration Tests

```bash
python -m pytest tests/ -v --integration
```

### Running Integration Tests with Rancher Desktop

```bash
python -m pytest tests/ -v --integration --rancher
```

Or with environment variable:

```bash
USE_RANCHER=true python -m pytest tests/ -v --integration
