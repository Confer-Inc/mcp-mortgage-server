import requests
from typing import Dict, Any, List
import json

class MCPToolBase:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self._tools_cache = None

    def _get_tools(self) -> List[Dict[str, Any]]:
        if self._tools_cache is None:
            response = requests.get(f"{self.base_url}/tools")
            self._tools_cache = response.json()["tools"]
        return self._tools_cache

    def _call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        payload = {
            "tool": tool_name,
            "input": kwargs
        }
        response = requests.post(f"{self.base_url}/call", json=payload)
        return response.json()

# AutoGen Integration
class MCPToolkitAutoGen(MCPToolBase):
    def get_functions(self) -> List[Dict[str, Any]]:
        """Get tools in AutoGen function format"""
        tools = self._get_tools()
        return [{
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        } for tool in tools]

    def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Execute function in AutoGen format"""
        return self._call_tool(function_name, **kwargs)

# LangChain Integration
class MCPToolkitLangChain(MCPToolBase):
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tools in LangChain format"""
        tools = self._get_tools()
        return [tool["function"] for tool in tools]

    def run_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute tool in LangChain format"""
        # LangChain passes input as a string, so we parse it
        try:
            input_dict = json.loads(tool_input)
        except json.JSONDecodeError:
            input_dict = {"input": tool_input}
        
        result = self._call_tool(tool_name, **input_dict)
        return json.dumps(result)

def test_autogen():
    print("\nTesting AutoGen Integration:")
    toolkit = MCPToolkitAutoGen()
    
    # Get available functions
    functions = toolkit.get_functions()
    print("Available functions:", json.dumps(functions, indent=2))
    
    # Execute hello function
    result = toolkit.execute_function("hello", name="AutoGen User")
    print("Function result:", result)

def test_langchain():
    print("\nTesting LangChain Integration:")
    toolkit = MCPToolkitLangChain()
    
    # Get available tools
    tools = toolkit.get_tools()
    print("Available tools:", json.dumps(tools, indent=2))
    
    # Execute hello tool
    result = toolkit.run_tool("hello", '{"name": "LangChain User"}')
    print("Tool result:", result)

if __name__ == "__main__":
    test_autogen()
    test_langchain() 