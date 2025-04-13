import pytest
from fastapi.testclient import TestClient
import responses
import json
from unittest.mock import patch

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_tools(test_client, mock_mcp_config):
    """Test the tools listing endpoint"""
    with patch("main.MCP_CONFIG", mock_mcp_config):
        response = test_client.get("/tools")
        assert response.status_code == 200
        assert response.json() == {"tools": mock_mcp_config["tools"]}

@pytest.mark.parametrize("tool_name,pdf_url_fixture", [
    ("parse_le_to_mismo_json", "sample_le_pdf_url"),
    ("parse_cd_to_mismo_json", "sample_cd_pdf_url")
])
def test_call_tool_success(test_client, mock_mcp_config, mock_mismo_response, tool_name, pdf_url_fixture, request):
    """Test successful tool calls"""
    pdf_url = request.getfixturevalue(pdf_url_fixture)
    
    with patch("main.MCP_CONFIG", mock_mcp_config), \
         patch(f"tools.parse_le_to_mismo.parse_le_to_mismo" if "le" in tool_name else f"tools.parse_cd_to_mismo.parse_cd_to_mismo", 
               return_value=mock_mismo_response):
        
        payload = {
            "tool": tool_name,
            "input": {
                "pdf_url": pdf_url
            }
        }
        response = test_client.post("/call", json=payload)
        assert response.status_code == 200
        assert response.json() == {"output": mock_mismo_response}

def test_call_unknown_tool(test_client, mock_mcp_config):
    """Test calling an unknown tool"""
    with patch("main.MCP_CONFIG", mock_mcp_config):
        payload = {
            "tool": "unknown_tool",
            "input": {
                "pdf_url": "https://example.com/doc.pdf"
            }
        }
        response = test_client.post("/call", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

def test_call_tool_invalid_input(test_client, mock_mcp_config):
    """Test calling a tool with invalid input"""
    with patch("main.MCP_CONFIG", mock_mcp_config):
        payload = {
            "tool": "parse_le_to_mismo_json",
            "input": {}  # Missing required pdf_url
        }
        response = test_client.post("/call", json=payload)
        assert response.status_code == 500  # Since validation happens in the tool

@responses.activate
def test_call_tool_with_network_error(test_client, mock_mcp_config, sample_le_pdf_url):
    """Test handling of network errors when downloading PDFs"""
    responses.add(
        responses.GET,
        sample_le_pdf_url,
        status=404
    )
    
    with patch("main.MCP_CONFIG", mock_mcp_config):
        payload = {
            "tool": "parse_le_to_mismo_json",
            "input": {
                "pdf_url": sample_le_pdf_url
            }
        }
        response = test_client.post("/call", json=payload)
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

def test_cors_headers(test_client):
    """Test CORS headers are properly set"""
    response = test_client.options("/call", headers={
        "origin": "http://localhost:3000",
        "access-control-request-method": "POST",
        "access-control-request-headers": "content-type",
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers 