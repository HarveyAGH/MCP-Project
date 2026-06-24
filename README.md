# Job Research Agent

You paste a job URL. It scrapes the listing, compares it against 
your resume, and tells you your match score, what's missing, 
and which roles actually suit you better — then saves everything 
to a local database so you can review it later.

Built with LangGraph, MCP, and Claude Haiku on AWS Bedrock.

---

## What it actually does

1. You paste your resume at startup (nothing is stored or sent anywhere)
2. You paste a job URL
3. The agent scrapes the listing, extracts required skills, 
   runs a gap analysis, and saves the result to SQLite
4. You get a structured breakdown: match score, specific gaps, 
   a one-sentence pitch, and roles that would suit you better
5. You can keep asking follow-up questions — it remembers 
   the whole session

---

## Architecture

Two MCP servers, one LangGraph agent:
servers/

search_server.py   → scrapes job listings, extracts skills

runs on Railway (streamable HTTP)

notes_server.py    → saves research to SQLite

runs locally (stdio subprocess)
client.py            → LangGraph agent orchestrating both servers

Claude Haiku via AWS Bedrock

InMemorySaver for session persistence

Pydantic structured output on final result

The agent decides which tools to call and in what order. 
You don't hardcode the sequence — it reasons through it.

---

## Setup

**Prerequisites:** Python 3.12+, `uv`, AWS account with Bedrock access

**Install:**
```bash
git clone https://github.com/HarveyAGH/MCP-Project.git
cd MCP-Project
uv sync
```

**Environment:**
```bash
cp .env.example .env
# fill in your values
```

```bash
# .env.example
BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0
BEDROCK_REGION=us-east-1
AWS_BEARER_TOKEN_BEDROCK=your_token_here
LANGSMITH_API_KEY=your_key_here        # optional but recommended
LANGSMITH_TRACING=true
```

---

## Running it

Terminal 1 — start the search server:
```bash
uv run python servers/search_server.py
```

Terminal 2 — start the agent:
```bash
uv run python client.py
```

Paste your resume when prompted, then start sending job URLs.

**Example session:**
You: https://jobs.lever.co/anthropic/ai-engineer

You: what are my biggest gaps for this role?

You: what roles would suit me better right now?

You: compare this to the last job i researched

---

## Running evals

```bash
uv run python evals/run_evals.py
```

5 test cases covering: tool routing, structured output validity, 
match score ranges, prompt injection resistance, and memory 
behavior. Uses a synthetic resume in `evals/fixtures/` — 
your personal resume is never committed to the repo.

Current baseline: **5/5 passed (100%)**

---

## LangSmith tracing

Every run is traced automatically when `LANGSMITH_TRACING=true`. 
You can inspect tool calls, token usage, and latency 
in your LangSmith dashboard.

---

## Stack

| Layer | Tool |
|---|---|
| Agent orchestration | LangGraph |
| MCP servers | FastMCP |
| LLM | Claude Haiku via AWS Bedrock |
| MCP client | langchain-mcp-adapters |
| Structured output | Pydantic + `with_structured_output` |
| Persistence | SQLite (notes), InMemorySaver (session) |
| Observability | LangSmith |
| Search server deploy | Railway |