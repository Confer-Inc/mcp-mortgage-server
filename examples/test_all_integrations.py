import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Callable, Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import nest_asyncio
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Enable nested asyncio to handle async calls in sync contexts
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Base MCP Tool class
class MCPToolBase:
    def __init__(self, base_url: str = "http://localhost:8001", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("API_KEY", "your_api_key_here")
        self.headers = {"X-API-Key": self.api_key}

    async def _call_api(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        payload = {
            "tool": tool_name,
            "input": kwargs
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.base_url}/call", json=payload) as response:
                return await response.json()

# 1. CrewAI Integration
class HelloTool(BaseTool):
    name: str = "hello"
    description: str = "Say hello to someone"

    def _run(self, name: str = "World") -> str:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._arun(name))

    async def _arun(self, name: str = "World") -> str:
        toolkit = MCPToolkitCrewAI()
        return await toolkit.hello(name)

class MCPToolkitCrewAI(MCPToolBase):
    async def hello(self, name: str = "World") -> str:
        """Say hello to someone"""
        result = await self._call_api("hello", name=name)
        return result["output"]

async def test_crewai():
    print("\n=== Testing CrewAI Integration ===")
    hello_tool = HelloTool()
    
    # Create an agent with our tool
    agent = Agent(
        role="Greeter",
        goal="Greet people politely",
        backstory="I am a polite greeting agent that says hello to people.",
        tools=[hello_tool],
        verbose=True
    )
    
    # Create a task
    task = Task(
        description="Say hello to the user",
        expected_output="A friendly greeting message",
        agent=agent
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    print("CrewAI Result:", result)

# 2. AutoGen Integration
import autogen
from autogen import AssistantAgent, UserProxyAgent

class MCPToolkitAutoGen(MCPToolBase):
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools in AutoGen format"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/tools") as response:
                data = await response.json()
                return [{
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name to greet"
                                }
                            },
                            "required": ["name"]
                        }
                    }
                } for tool in data["tools"]]

async def test_autogen():
    print("\n=== Testing AutoGen Integration ===")
    
    config_list = [{"model": "gpt-3.5-turbo"}]
    assistant = AssistantAgent(
        name="assistant",
        llm_config={"config_list": config_list},
        system_message="""You are a helpful AI assistant. When asked to use a tool, use it directly instead of writing code.
For the hello tool, use it with a JSON object containing the 'name' parameter."""
    )
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config={"work_dir": "coding", "use_docker": False},
        llm_config={"config_list": config_list},
        system_message="Reply TERMINATE if the task is done."
    )
    
    toolkit = MCPToolkitAutoGen()
    tools = await toolkit.get_tools()
    assistant.register_function(tools[0])
    
    await user_proxy.a_initiate_chat(
        assistant,
        message="Please use the hello tool to greet Alice. TERMINATE"
    )

# 3. LangChain Integration
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish

class HelloInput(BaseModel):
    name: str = Field(description="The name of the person to greet", default="World")

class MCPToolkitLangChain(MCPToolBase):
    async def hello(self, name: str = "World") -> str:
        """Say hello to someone using the MCP server"""
        result = await self._call_api("hello", name=name)
        return result["output"]

async def test_langchain():
    print("\n=== Testing LangChain Integration ===")
    
    toolkit = MCPToolkitLangChain()
    tools = [
        Tool(
            name="hello",
            func=lambda x: asyncio.get_event_loop().run_until_complete(toolkit.hello(name=x)),
            description="A tool that says hello to someone. Input should be a name string.",
            return_direct=True
        )
    ]
    
    llm = ChatOpenAI(temperature=0)
    agent = create_react_agent(llm, tools, PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""))
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    # Test the agent with a simple request
    result = await agent_executor.ainvoke({"input": "Please say hello to Bob."})
    print("LangChain Result:", result)

async def main():
    # Start the tests
    print("Starting integration tests...")
    
    try:
        # Test CrewAI
        await test_crewai()
    except Exception as e:
        print("CrewAI test failed:", str(e))
    
    try:
        # Test AutoGen
        await test_autogen()
    except Exception as e:
        print("AutoGen test failed:", str(e))
    
    try:
        # Test LangChain
        await test_langchain()
    except Exception as e:
        print("LangChain test failed:", str(e))
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 