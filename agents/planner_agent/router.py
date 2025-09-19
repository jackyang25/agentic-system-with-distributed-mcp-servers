"""Router for the Planner Agent workflow."""
from .nodes import plan_workflow
from states.planner_state import PlannerState

async def route_planner_agent(state: PlannerState) -> PlannerState:
    """Router for planner agent tasks."""
    return await plan_workflow(state)