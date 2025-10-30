from fastmcp import FastMCP

server: FastMCP = FastMCP(name="Finance")


@server.tool()
def calculate_budget(income: float) -> float:
    return income * 0.30


@server.tool()
def loan_qualification(income: float, credit_score: int) -> float:
    if credit_score >= 750:
        multiplier = 5.0
    elif credit_score >= 700:
        multiplier = 4.5
    elif credit_score >= 650:
        multiplier = 4.0
    elif credit_score >= 580:
        multiplier = 3.5
    else:
        multiplier = 2.5

    return income * multiplier


if __name__ == "__main__":
    server.run(transport="stdio")
