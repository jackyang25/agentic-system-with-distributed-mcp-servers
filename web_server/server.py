# Core imports
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from logging import Logger
from typing import Any

from fastapi import FastAPI

from agents.planner_agent.graph import run_planner_agent
from mcp_kit.tools import mcp_adapter
from utils.convenience import get_logger

logger: Logger = get_logger(name=__name__)


# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI) -> _AsyncGeneratorContextManager[Any, Any, Any]:
    # Startup
    await mcp_adapter.connect_all()
    logger.info(await mcp_adapter.check_running())
    logger.info("MCP connections established")
    yield
    # Shutdown (if needed)
    pass


# FastAPI app setup
app = FastAPI(title="MAREA API", lifespan=lifespan)


# API endpoint for external access
@app.post(path="/analyze")
async def analyze_endpoint(
    income: float, credit_score: int, zip_code: str
) -> dict[str, str]:
    try:
        user_data: dict[str, Any] = {
            "income": income,
            "credit_score": credit_score,
            "zip_code": zip_code,
        }
        result: Any = await run_planner_agent(user_data=user_data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
