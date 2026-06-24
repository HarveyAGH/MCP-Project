import asyncio
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages  import HumanMessage
from pydantic import BaseModel
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import InMemorySaver


class GapAnalysis(BaseModel):
    match_score:int
    top_gaps: list[str]
    pitch: str
    recommend_roles: list[str]

load_dotenv()


BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")




async def run_research():
    print("Paste your resume below. Press Enter twice when done:\n")
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
        lines.append(line)
    resume_text = "\n".join(lines).strip()
        
    mcp_client = MultiServerMCPClient(
        {
            "notes": {
                "command": "python",
                "args":['servers/notes_server.py'],
                "transport": "stdio",
            },
            
            "search": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http"   
                },
        })
    tools = await mcp_client.get_tools()
    llm = ChatBedrockConverse(model=BEDROCK_MODEL_ID, region_name=BEDROCK_REGION)
    agent = create_agent(
        model=llm,
        tools= tools,
        checkpointer=InMemorySaver(),
        system_prompt=f"You are a professional career coach.\n\nResume:\n{resume_text}"
        
    )
    
    
    # thread_id keeps the conversation continuous
    config = {"configurable": {"thread_id": "job-research-session"}}
    print("Agent ready. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
            
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        
        agent_text = result["messages"][-1].content
        print(f"\nAgent: {agent_text}\n")
        
        # structured output only when it's a gap analysis request
        if "gap" in user_input.lower() or "http" in user_input.lower():
            structured_output = llm.with_structured_output(GapAnalysis)
            parsed = structured_output.invoke(
                f"Extract a structured gap analysis from this:\n\n{agent_text}"
            )
            print("=" * 50)
            print(f"Match Score: {parsed.match_score}/100")
            for gap in parsed.top_gaps:
                print(f"  • {gap}")
            print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_research())