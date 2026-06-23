from mcp.server import FastMCP
import requests
from bs4 import BeautifulSoup

mcp = FastMCP("search-server")

@mcp.tool()
def scrape_job_listing(url: str) -> str:
    """Scrape a job listing URL and return cleaned text"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return text[:5000]  # keep it within LLM context

@mcp.tool()
def extract_skills(job_text: str) -> str:
    """Pull known tech skills from job text"""
    keywords = [
        "Python", "JavaScript", "TypeScript", "React", "Node.js",
        "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
        "AWS", "GCP", "Azure", "FastAPI", "Django", "Flask",
        "LLM", "RAG", "MCP", "REST", "GraphQL", "Redis", "Groq"
    ]
    found = [kw for kw in keywords if kw.lower() in job_text.lower()]
    return f"Detected skills: {', '.join(found) if found else 'None matched'}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")