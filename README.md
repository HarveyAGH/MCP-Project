# 🔍 Job Research Agent

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-orange?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
[![Evals](https://img.shields.io/badge/Evals-5%2F5%20passing-yellow?style=flat-square)]()
[![AWS Bedrock](https://img.shields.io/badge/LLM-Claude%20Haiku-yellow?style=flat-square)](https://aws.amazon.com/bedrock/)

> Paste a job URL. Get an honest match score, specific skill gaps, and roles that actually suit you — saved automatically to a local database.

---

## What it does

You paste your resume once at startup. Then you talk to it like a career coach that actually knows your background.

It scrapes the job listing, cross-references it against your resume, and gives you back a structured breakdown — match score, what you're missing, a one-sentence pitch, and smarter alternatives to consider. Every analysis gets saved to SQLite so you can review your research later.

It remembers the full conversation. You can ask follow-ups, compare two roles, or ask what you should apply to instead.

---

## Demo

```
$ uv run python client.py

[connecting to servers...]

Paste your resume below. Type END on a new line when done:

Ahmed Gamal
AI Engineer | LangGraph / LangChain / Agentic AI Systems
...
END

Ready. Paste a job URL or ask anything.

You: https://jobs.lever.co/anthropic/ai-engineer

Agent: Strong alignment with your background. Your LangGraph
       and eval infrastructure experience directly maps to what
       they're looking for. Main gap is formal ML research...

══════════════════════════════════════════════════
Match Score:  72/100

Top Gaps:
  • Formal ML research background — consider Arxiv paper reading
  • Distributed systems at scale — not demonstrated in portfolio
  • PhD or equivalent research depth — common at Anthropic

Pitch:
  Strong agentic systems builder with production eval
  infrastructure — unusual combination for this stage.

Recommended Roles:
  • AI Engineer at early-stage AI startups
  • Solutions Engineer at LLM platform companies
  • MLOps Engineer at companies scaling LLM products
══════════════════════════════════════════════════

You: what was my match score for that role?
Agent: 72/100 for the Anthropic AI Engineer role.

You: find me something more realistic to apply to right now
Agent: Given your current profile, here's what I'd target...
```

---

## How to use it

**Step 1 — Start both servers**

Terminal 1:
```bash
uv run python servers/search_server.py
```

Terminal 2:
```bash
uv run python client.py
```

**Step 2 — Paste your resume**

When prompted, paste your full resume directly into the terminal. It can be any format — plain text works best. When you're done, type `END` on a new line and press Enter.

```
Paste your resume below. Type END on a new line when done:

[paste your resume here]
[it can be as long as you want]
[blank lines are fine]
END
```

> ⚠️ Your resume is never stored or committed to the repo. It lives only in memory for the duration of your session.

**Step 3 — Start researching**

Paste any job URL and the agent handles the rest:

```
You: https://jobs.lever.co/binance/95ef7f26-27a2-488c-a51b-6596fd461539
You: what are my top 3 gaps for this role?
You: compare this to the last job I sent you
You: what should I actually be applying to right now?
```

Type `exit`, `quit`, or `end` to end the session.

---

## Architecture

Two MCP servers, one LangGraph agent, one session.

```
┌─────────────────────────────────────────┐
│              client.py                  │
│         LangGraph Agent                 │
│       (Claude Haiku via Bedrock)        │
│       InMemorySaver checkpointer        │
└────────────┬──────────────┬─────────────┘
             │              │
    stdio    │              │  streamable HTTP
             ▼              ▼
  ┌──────────────┐   ┌──────────────────┐
  │ notes_server │   │  search_server   │
  │              │   │                  │
  │ save_research│   │ scrape_job_listing│
  │ get_research │   │ extract_skills   │
  │              │   │                  │
  │   SQLite     │   │  Deployed on     │
  │  (local)     │   │    Render        │
  └──────────────┘   └──────────────────┘
```

The agent decides which tools to call and in what order. You don't script the sequence — it reasons through the task.

---

## Setup

**Requirements:** Python 3.12+, `uv`, AWS account with Bedrock access

```bash
git clone https://github.com/HarveyAGH/MCP-Project.git
cd MCP-Project
uv sync
cp .env.example .env
# fill in your credentials
```

```bash
# .env
BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0
BEDROCK_REGION=us-east-1
AWS_BEARER_TOKEN_BEDROCK=your_token_here
LANGSMITH_API_KEY=your_key_here       # optional — enables tracing
LANGSMITH_TRACING=true
SEARCH_SERVER_URL=http://127.0.0.1:8000/mcp   # or your Render URL if using the deployed server
```

---

## Evals

```bash
uv run python evals/run_evals.py
```

Tests run against a synthetic resume in `evals/fixtures/` — your personal resume is never committed to the repo.

> ⚠️ Make sure `servers/search_server.py` is running on port 8000 before running evals.

```
Current baseline: 5/5 passed (100.0%)  |  threshold: 80%

Graders:
  ✓ no_error          — agent completed without crashing
  ✓ tools_called      — correct tools were invoked
  ✓ structured_valid  — Pydantic output fields are populated and typed correctly
  ✓ score_range       — match scores are sensible for the role type
  ✓ gaps_count        — minimum gap count returned
  ✓ llm_judge         — quality scored by Claude against rubric
```

---

## LangSmith tracing

Every run is traced automatically when `LANGSMITH_TRACING=true`.
You can inspect tool calls, token usage, and latency in your LangSmith dashboard.

---

## Stack

| Layer | Tool |
|---|---|
| Agent orchestration | LangGraph |
| MCP servers | FastMCP |
| LLM | Claude Haiku via AWS Bedrock |
| MCP client | langchain-mcp-adapters |
| Structured output | Pydantic + `with_structured_output` |
| Session memory | LangGraph InMemorySaver |
| Persistence | SQLite via notes server |
| Observability | LangSmith |
| Search server hosting | Render |

---

## Project structure

```
├── client.py                  # entry point — agent + resume input + while loop
├── servers/
│   ├── search_server.py       # scrapes jobs, extracts skills (HTTP, Render)
│   └── notes_server.py        # saves research to SQLite (stdio subprocess)
├── evals/
│   ├── golden_dataset.py      # 5 test cases
│   ├── graders.py             # 6 grader functions including LLM-as-judge
│   ├── run_evals.py           # eval runner
│   └── fixtures/
│       └── test_resume.txt    # synthetic resume for testing only
├── data/                      # SQLite database (git-ignored)
├── .env.example
└── pyproject.toml
```
