# MCP Job Research Agent

Paste a job URL. Get a match score, skill gaps, and a tailored pitch.

## Architecture
- `servers/search_server.py` — scrapes job listings (deployed on Railway)
- `servers/notes_server.py`  — persists research to SQLite
- `client.py`               — LangGraph agent orchestrating both via MCP

## Setup
cp .env.example .env
# fill in your AWS Bedrock credentials

uv sync
uv run python client.py