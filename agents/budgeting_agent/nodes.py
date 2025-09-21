"""Nodes for the Budgeting Agent workflow."""

from .state import BudgetingState


async def budget_calculation_node(state: BudgetingState):
    """Calculate 30% budget from user income"""
    from mcp_kit.tools import calculate_budget
    
    # Call the tool directly to get the budget (async)
    budget_result = await calculate_budget.ainvoke({"income": state['income']})
    print(f"Budget calculation result: {budget_result}")
    
    # Extract specific values
    state["monthly_budget"] = budget_result.get('budget', 0)
    state["budget_result"] = budget_result  # Keep full result for compatibility
    
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
    
    # Extract specific values
    state["max_loan"] = loan_result.get('max_loan', 0)
    state["loan_result"] = loan_result  # Keep full result for compatibility
    
    return state


async def price_data_query_node(state: BudgetingState):
    """Query comprehensive price data by zip code and residential units"""
    from mcp_kit.tools import query_price_data_by_zip_and_units
    
    # Call the price data query tool
    price_data_result = await query_price_data_by_zip_and_units.ainvoke({
        "zip_code": state['zip_code'],
        "residential_units": state['residential_units']
    })
    print(f"Price data query result: {price_data_result}")
    
    # Store just the raw tool result
    state["price_data"] = price_data_result
    
    return state


