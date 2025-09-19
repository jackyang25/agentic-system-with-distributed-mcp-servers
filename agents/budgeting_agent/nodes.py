"""Nodes for the Budgeting Agent workflow."""

from .state import BudgetingState


async def budget_calculation_node(state: BudgetingState):
    """Calculate 30% budget from user income"""
    from mcp_kit.tools import calculate_budget
    
    # Call the tool directly to get the budget (async)
    budget_result = await calculate_budget.ainvoke({"income": state['income']})
    print(f"Budget calculation result: {budget_result}")
    
    # Store just the raw tool result
    state["budget_result"] = budget_result
    
    return state


async def loan_qualification_node(state: BudgetingState):
    """Calculate maximum loan amount based on income and credit score"""
    from mcp_kit.tools import loan_qualification
    
    # Call the loan qualification tool
    loan_result = await loan_qualification.ainvoke({
        "income": state['income'], 
        "credit_score": state['credit_score']
    })
    print(f"Loan qualification result: {loan_result}")
    
    # Store just the raw tool result
    state["loan_result"] = loan_result
    
    return state


