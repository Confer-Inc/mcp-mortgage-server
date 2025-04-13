# MCP Server (Mortgage Comparison Platform)

A FastAPI-based server that provides mortgage document parsing and comparison tools through a standardized API. The server is designed to be easily integrated with various AI frameworks including CrewAI, AutoGen, and LangChain.

Currently implements a basic "hello" tool as a proof of concept, with mortgage document parsing tools coming soon.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/confersolutions/mcp-mortgage-server/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Website](https://img.shields.io/badge/Website-confersolutions.ai-blue)](https://confersolutions.ai)

## Status

This is a beta release (v0.1.0) that provides:
- Core server infrastructure with security features
- Basic "hello" tool for testing framework integrations
- Example integrations with CrewAI, AutoGen, and LangChain

Future versions will add mortgage document parsing and comparison tools.

## Features

- FastAPI server with production-ready features:
  - API key authentication
  - Rate limiting support
  - CORS middleware configuration
- Framework integrations for AI agents:
  - CrewAI
  - AutoGen
  - LangChain
- Extensible architecture for adding mortgage parsing tools
- Open source for transparency and community contributions

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/confersolutions/mcp-mortgage-server.git
   cd mcp-mortgage-server
   ```

## Roadmap

- ✅ Core server infrastructure with security and rate limiting
- ✅ Framework integrations (CrewAI, AutoGen, LangChain)
- ✅ Basic tool implementation ("hello" endpoint)
- 🚧 Loan Estimate (LE) parsing to MISMO format
- 🚧 Closing Disclosure (CD) parsing
- 🚧 Mortgage comparison tools
- 🚧 Additional mortgage document analysis features

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn slowapi python-dotenv
   pip install crewai autogen langchain langchain-openai
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
API_KEY=your_api_key_here
RATE_LIMIT_PER_MINUTE=120
ALLOWED_ORIGINS=http://localhost:3000
HOST=0.0.0.0
PORT=8001
WORKERS=1
```

## Running the Server

```bash
python server.py
```

The server will start on http://localhost:8001 by default.

## API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy"}
```

### List Available Tools
```
GET /tools
Headers: X-API-Key: your_api_key_here
Response: List of available tools and their configurations
```

### Call Tool
```
POST /call
Headers: X-API-Key: your_api_key_here
Body: {
    "tool": "hello",
    "input": {
        "name": "World"  // Optional
    }
}
Response: {
    "output": "Hello, World!"
}
```

## Framework Integration Examples

See `examples/test_all_integrations.py` for examples of how to use the server with:
- CrewAI
- AutoGen
- LangChain

### CrewAI Example
```python
from crewai import Agent, Task, Crew
from mcp_toolkit import MCPToolkitCrewAI

toolkit = MCPToolkitCrewAI()
tools = await toolkit.get_tools()

agent = Agent(
    role="Greeter",
    goal="Say hello to the user",
    tools=tools
)

task = Task(
    description="Say hello to the user",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = await crew.kickoff()
```

### AutoGen Example
```python
from autogen import AssistantAgent, UserProxyAgent
from mcp_toolkit import MCPToolkitAutoGen

toolkit = MCPToolkitAutoGen()
tools = await toolkit.get_tools()

assistant = AssistantAgent(
    name="assistant",
    llm_config={"tools": tools}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"use_docker": False}
)

await user_proxy.initiate_chat(assistant, message="Please say hello to Alice")
```

### LangChain Example
```python
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from mcp_toolkit import MCPToolkitLangChain

toolkit = MCPToolkitLangChain()
tools = [
    Tool(
        name="hello",
        func=lambda x: asyncio.get_event_loop().run_until_complete(toolkit.hello(name=x)),
        description="A tool that says hello to someone",
        return_direct=True
    )
]

llm = ChatOpenAI(temperature=0)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

result = await agent_executor.ainvoke({"input": "Please say hello to Bob"})
```

## Rate Limiting

The server implements rate limiting using `slowapi`. By default, it's set to 120 requests per minute per IP address. This can be configured using the `RATE_LIMIT_PER_MINUTE` environment variable.

## Security

- API key authentication is required for all endpoints except `/health`
- CORS is configured to allow specific origins (set via `ALLOWED_ORIGINS` environment variable)
- All exceptions are caught and returned with appropriate error messages

## Contributing

Feel free to open issues or submit pull requests for improvements.

## About

This project is maintained by [Confer Solutions](https://confersolutions.ai). For questions or support, contact us at info@confersolutions.ai.

## License

MIT License - see [LICENSE](LICENSE) file for details.
