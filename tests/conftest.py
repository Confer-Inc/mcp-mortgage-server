import pytest
from fastapi.testclient import TestClient
from main import app
import json
import os

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_le_pdf_url():
    return "https://example.com/sample-le.pdf"

@pytest.fixture
def sample_cd_pdf_url():
    return "https://example.com/sample-cd.pdf"

@pytest.fixture
def mock_mcp_config():
    return {
        "tools": [
            {
                "name": "parse_le_to_mismo_json",
                "description": "Parses LE PDF and returns MISMO-compliant JSON with LLM metadata.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pdf_url": {"type": "string"}
                    },
                    "required": ["pdf_url"]
                },
                "output_schema": {
                    "type": "object"
                }
            },
            {
                "name": "parse_cd_to_mismo_json",
                "description": "Parses CD PDF and returns MISMO-compliant JSON with LLM metadata.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pdf_url": {"type": "string"}
                    },
                    "required": ["pdf_url"]
                },
                "output_schema": {
                    "type": "object"
                }
            }
        ]
    }

@pytest.fixture
def mock_mismo_response():
    return {
        "GFEOriginationCharges": {
            "value": 2500,
            "description": "Charges by lender for originating the loan",
            "flags": ["Above typical range for 1% origination cap"],
            "tolerance_bucket": "Limited Increase",
            "source_location": "Page 2, Section A"
        },
        "APRDelta": 0.31,
        "DeliveryTimeline": {
            "received_by_borrower": "2024-03-01",
            "days_to_close": 12,
            "compliance_check": "Pass"
        }
    } 