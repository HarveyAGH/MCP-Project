from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

import asyncio
import os

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

async def main():
    Client = MultiServerMCPClient(
        {
             "Math": {
                "command": "python",
                "args": ['mathematics_server.py'],
                "transport": "stdio",
             },
             "Weather": {
                 "url": "http://127.0.0.1:8000/mcp",
                 "transport": "streamable-http"
                 
             }
        },
    )
    
    tools = await Client.get_tools()
    model = ChatGroq(model="qwen/qwen3-32b")
    agent = create_agent(
        model=model,
        tools=tools
    )
    
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "hey what is 5 * 3 - 14?"}]}
    )
    
  
    print("The math response:", math_response['messages'][-1].content)

asyncio.run(main())
    





    



