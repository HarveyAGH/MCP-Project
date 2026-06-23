import asyncio
import os
from dotenv import load_dotenv
from mcp.server import Client
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def run_research(job_url: str):
    async with (
        Client("python servers/file_server.py") as file_client,
        Client("python servers/notes_server.py") as notes_client,
        Client("http://localhost:800/mcp") as search_client,
    ):
        # --- Resource read (not a tool call) ---
        print("📄 Reading resume resource...")
        resume_data = await file_client.read_resource("resume://main")
        resume_text = resume_data[0].text

        # --- Tool calls on search server ---
        print(f"🔍 Scraping: {job_url}")
        job_result = await search_client.call_tool(
            "scrape_job_listing", {"url": job_url}
        )
        job_text = job_result[0].text

        print("🔎 Extracting skills...")
        skills_result = await search_client.call_tool(
            "extract_skills", {"job_text": job_text}
        )
        skills_text = skills_result[0].text

        # --- LLM analysis via Groq ---
        print("🤖 Running gap analysis...")
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a career coach. Be direct and concise."
                },
                {
                    "role": "user",
                    "content": f"""
Resume:
{resume_text}

Job Description (excerpt):
{job_text[:2000]}

Skills detected in job: {skills_text}

Return exactly:
1. Match score (0-100)
2. Top 3 skill gaps with one-line fix for each
3. A one-sentence pitch tailored to this role
"""
                }
            ]
        )
        analysis = response.choices[0].message.content

        # --- Persist to SQLite via notes server ---
        print("💾 Saving to database...")
        company = job_url.split("/")[2]  # crude but works for demo
        await notes_client.call_tool("save_research", {
            "company": company,
            "role": "Scraped from URL",
            "notes": f"URL: {job_url}\n\n{analysis}"
        })

        print("\n" + "=" * 50)
        print(analysis)
        print("=" * 50)

if __name__ == "__main__":
    url = input("Paste job listing URL: ").strip()
    asyncio.run(run_research(url))