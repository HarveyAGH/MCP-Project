from mcp.server import FastMCP

mcp = FastMCP("file-server")

@mcp.resource("resume://main")
def get_resume()-> str:
    """Exposes Resume content as readable resource"""
    with open("resume.txt", "r") as f:
        return f.read()
    
if __name__ == "__main__":
    mcp.run("stdio")