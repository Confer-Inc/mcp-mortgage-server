# MCP Mortgage Server

[![CI](https://github.com/confersolutions/mcp-mortgage-server/actions/workflows/ci.yml/badge.svg)](https://github.com/confersolutions/mcp-mortgage-server/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/confersolutions/mcp-mortgage-server/branch/main/graph/badge.svg)](https://codecov.io/gh/confersolutions/mcp-mortgage-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A FastAPI-based MCP (Machine Control Protocol) server for parsing mortgage documents (Loan Estimates and Closing Disclosures) into MISMO-compliant JSON format.

## Features

- Parse Loan Estimate (LE) PDFs into MISMO-compliant JSON
- Parse Closing Disclosure (CD) PDFs into MISMO-compliant JSON
- Built-in LLM context generation for compliance checks
- FastAPI-based REST API with OpenAPI documentation
- Docker support for easy deployment
- Render.com deployment configuration

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/confersolutions/mcp-mortgage-server.git
cd mcp-mortgage-server
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the server:
```bash
uvicorn main:app --reload
```

### Testing

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py

# Run tests in verbose mode
pytest -v
```

Test coverage reports are generated in HTML format and can be found in the `htmlcov` directory.

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t mcp-mortgage-server .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here mcp-mortgage-server
```

## API Documentation

Once the server is running, visit:
- OpenAPI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

### Available Endpoints

- `GET /health`: Health check endpoint
- `GET /tools`: List available tools and their schemas
- `POST /call`: Call a specific tool

### Example API Call

```python
import requests

url = "http://localhost:8000/call"
payload = {
    "tool": "parse_le_to_mismo_json",
    "input": {
        "pdf_url": "https://example.com/loan-estimate.pdf"
    }
}
response = requests.post(url, json=payload)
print(response.json())
```

## Deployment

### Render.com

This repository includes a `render.yaml` configuration file for easy deployment to Render.com. Simply:

1. Fork this repository
2. Connect it to your Render account
3. Add required environment variables
4. Deploy!

## Development

### Project Structure

```
mcp-mortgage-server/
├── main.py                 # FastAPI server entrypoint
├── mcp_config.json        # Tool configurations
├── requirements.txt       # Python dependencies
├── tools/                # Tool implementations
├── utils/                # Utility functions
├── tests/                # Test files
│   ├── conftest.py      # Test fixtures and configuration
│   └── test_api.py      # API endpoint tests
└── examples/             # Usage examples
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
