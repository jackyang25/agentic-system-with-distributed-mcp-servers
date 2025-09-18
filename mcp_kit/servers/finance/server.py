from fastmcp import FastMCP

server = FastMCP("Finance")

@server.tool()  # ← Registers tool, but server not running yet
def calculate_budget(income: float) -> float:
    return income * 0.30

if __name__ == "__main__":
    server.run(transport="stdio")  # ← THIS starts the server