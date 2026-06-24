import asyncio
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages  import HumanMessage, SystemMessage
from groq import Groq
from langchain_aws import ChatBedrockConverse

load_dotenv()


BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

async def run_research(job_url: str):
    with open("resume.txt", "r") as f:
        resume_text =  f.read()
        
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
        model=llm, tools= tools
    )
        
    result = await agent.ainvoke({"messages": 
        [SystemMessage(content=f"You are a career coach. Here is the candidate's resume:\n\n{resume_text}"),
        HumanMessage(content=f"Research this job listing and save the gap analysis: {job_url}")]})
    
    print(result["messages"][-1].content)
        
        # scrape_tool = next(t for t in tools if t.name == "scrape_job_listing")
        # skills_tool = next(t for t in tools if t.name == "extract_skills")
        # save_tool =  next(t for t in tools if t.name == "save_research")
        
        
        # print(f"🔍 Scraping: {job_url}")
        # job_text = scrape_tool.ainvoke({"url": job_url})
        
        # print("🔎 Extracting skills...")
        # skills_text = skills_tool.ainvoke({"job_text": str(job_text)})
        
        
        # print("🤖 Running gap analysis...")
        # response = groq_client.chat.completions.create(
        #     model=("llama-3.3-70b-versatile"),
        #     messages= [{"role": "system", "content": "You are a career coach, be direct, concise and honest to get the maximum impact possible when it comes to returning back the user an honest review"},
        #                {"role": "user", "content": f"""
        #                 Resume: {resume_text}
        #                 Job Description: {str(job_text)[:2000]}
        #                 Skills Detected: {skills_text}
                        
                        
        #                 Return:
        #                 - Match score.
        #                 - Top 3 gaps with fixes ONLY when absoulutely necessary
        #                 - One sentence pitch
                        
                        
        #                 """}        
                       
        #                ]
        # )
        # analysis = response.choices[0].message.content
        
        # print("💾 Saving...")
        # company = job_url.split("/")[2]
        # await save_tool.ainvoke({"company": company, "role": "Scraped from URL", "notes": f"URL: {job_url}\n\n{analysis}"})
 
        # print("=" * 50)
        # print(analysis)
        # print("=" * 50)
        
        
        


if __name__ == "__main__":
    url = input("Paste job listing URL: ").strip()
    asyncio.run(run_research(url))