import sqlite3
from mcp.server import FastMCP
import os
from datetime import datetime

mcp = FastMCP("database-server")

DB_PATH = "data/research.db"
os.makedirs("data", exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS research(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            notes TEXT,
            created_at TEXT
        )
        
        """
        
    )
    
    conn.commit()
    return conn


@mcp.tool()
def save_research(company: str, role: str, notes: str) -> str:
    """Save job research notes into the database"""
    conn = get_db()
    conn.execute(
        "INSERT INTO research(company, role, notes, created_at) VALUES (?, ?, ?, ?)",
        (company, role, notes, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return f"Saved {role} at {company}"


@mcp.tool()
def get_all_research():
    """Retrieve all saved jobs research"""
    conn = get_db()
    rows = conn.execute(
        "SELECT company, role, notes, created_at FROM research ORDER BY created_at DESC").fetchall()
    conn.close()
    if not rows:
        return ("no research saved at the moment")    
    result = []
    for row in rows:
        result.append(f"[{row[3]}] {row[1]} at {row[0]}\n{row[2]}")
    return "\n\n---\n\n".join(result)


if __name__ == "__main__":
    mcp.run("stdio")
    
    
