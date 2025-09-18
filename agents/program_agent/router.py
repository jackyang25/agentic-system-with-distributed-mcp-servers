from .nodes import fetch_government_programs
from .state import ProgramState

async def route_program_agent(state: ProgramState) -> ProgramState:
    """Router for program agent tasks."""
    return await fetch_government_programs(state)