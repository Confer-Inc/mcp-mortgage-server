import pytest
import json
from unittest.mock import patch
from examples.test_integrations import MCPToolkitAutoGen, MCPToolkitLangChain

@pytest.fixture
def mock_tools_response():
    return {
        "tools": [
            {
                "name": "hello",
                "description": "Returns a hello message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name to greet"}
                    }
                },
                "function": {
                    "name": "hello",
                    "description": "Returns a hello message",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name to greet"}
                        }
                    }
                }
            }
        ]
    }

@pytest.fixture
def mock_call_response():
    return {"output": "Hello, Test User!"}

class TestAutoGenIntegration:
    @pytest.fixture
    def autogen_toolkit(self):
        return MCPToolkitAutoGen(base_url="http://test-server")

    @pytest.mark.asyncio
    async def test_get_functions(self, autogen_toolkit, mock_tools_response, respx_mock):
        respx_mock.get("http://test-server/tools").mock(
            return_value=httpx.Response(200, json=mock_tools_response)
        )
        
        functions = autogen_toolkit.get_functions()
        assert len(functions) == 1
        assert functions[0]["name"] == "hello"
        assert "parameters" in functions[0]

    @pytest.mark.asyncio
    async def test_execute_function(self, autogen_toolkit, mock_call_response, respx_mock):
        respx_mock.post("http://test-server/call").mock(
            return_value=httpx.Response(200, json=mock_call_response)
        )
        
        result = autogen_toolkit.execute_function("hello", name="Test User")
        assert result == mock_call_response

class TestLangChainIntegration:
    @pytest.fixture
    def langchain_toolkit(self):
        return MCPToolkitLangChain(base_url="http://test-server")

    @pytest.mark.asyncio
    async def test_get_tools(self, langchain_toolkit, mock_tools_response, respx_mock):
        respx_mock.get("http://test-server/tools").mock(
            return_value=httpx.Response(200, json=mock_tools_response)
        )
        
        tools = langchain_toolkit.get_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "hello"
        assert "parameters" in tools[0]

    @pytest.mark.asyncio
    async def test_run_tool(self, langchain_toolkit, mock_call_response, respx_mock):
        respx_mock.post("http://test-server/call").mock(
            return_value=httpx.Response(200, json=mock_call_response)
        )
        
        result = langchain_toolkit.run_tool("hello", '{"name": "Test User"}')
        assert json.loads(result) == mock_call_response

    @pytest.mark.asyncio
    async def test_run_tool_invalid_json(self, langchain_toolkit, mock_call_response, respx_mock):
        respx_mock.post("http://test-server/call").mock(
            return_value=httpx.Response(200, json=mock_call_response)
        )
        
        result = langchain_toolkit.run_tool("hello", "Test User")
        assert json.loads(result) == mock_call_response 