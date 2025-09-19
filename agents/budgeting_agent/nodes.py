"""Nodes for the Budgeting Agent workflow."""

from .state import BudgetingState
from .prompts import get_budget_calculation_prompt


async def budget_calculation_node(state: BudgetingState):
    """Calculate 30% budget from user income"""
    from langchain_openai import ChatOpenAI
    from mcp_kit.tools import calculate_budget
    
    # Call the tool directly to get the budget (async)
    budget_result = await calculate_budget.ainvoke({"income": state['income']})
    print(f"Budget calculation result: {budget_result}")
    
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Use the existing prompt from prompts.py with the budget result
    prompt = get_budget_calculation_prompt(state['income'], budget_result)
    
    response = await model.ainvoke(prompt)
    print(f"Model response: {response.content}")
    
    # Store both the tool result and the model's explanation
    state["budget_result"] = {
        "tool_result": budget_result,
        "explanation": response.content
    }
    
    return state
