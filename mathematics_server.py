from mcp.server import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def addition(a:int, b:int)-> int:
    """A mathematical operation tool to be called when adding 2 numbers.
    ARGS:
    a: first integer
    b: second integer to add the first integer with
    
    """
    return a + b

@mcp.tool()
def multiply(a:int, b:int)-> int:
    """A mathematical operation tool to be called when multiplying 2 numbers.
    ARGS:
    a: first integer
    b: second integer to add the first integer with
    
    """
    return a * b



@mcp.tool()
def subtract(a:int, b:int)-> int:
    """A mathematical operation tool to be called when subtracting 2 numbers.
    ARGS:
    a: first integer
    b: second integer to add the first integer with
    
    """
    return a - b


if __name__ == "__main__":
    mcp.run(transport="stdio")