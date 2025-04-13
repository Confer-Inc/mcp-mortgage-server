import requests
import asyncio
from typing import Dict, Any

# Test 1: Direct API call
def test_direct_api():
    url = "http://localhost:8001/call"
    payload = {
        "tool": "hello",
        "input": {
            "name": "User"
        }
    }
    response = requests.post(url, json=payload)
    print("Direct API Response:", response.json())

# Test 2: CrewAI style wrapper
class MCPToolkit:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    async def hello(self, name: str = "World") -> Dict[str, Any]:
        import aiohttp
        payload = {
            "tool": "hello",
            "input": {"name": name}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/call", json=payload) as response:
                return await response.json()

async def test_crewai_style():
    toolkit = MCPToolkit()
    result = await toolkit.hello(name="CrewAI User")
    print("CrewAI Style Response:", result)

if __name__ == "__main__":
    # Run direct API test
    print("\nTesting direct API call:")
    test_direct_api()
    
    # Run CrewAI style test
    print("\nTesting CrewAI style call:")
    asyncio.run(test_crewai_style()) 