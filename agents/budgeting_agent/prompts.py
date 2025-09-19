"""Prompts for the Planner Agent workflow."""


def get_budget_calculation_prompt(income: float, budget_result: dict) -> str:
    """Prompt for budget calculation node"""
    # Extract the actual budget value from the nested structure
    budget_value = budget_result['budget']['budget']
    
    return f"""
    User income: ${income:,.0f}
    Budget: ${budget_value:,.0f} (30% of income)
    
    Provide a concise summary of what this budget means for property search.
    """


def get_property_query_prompt(target_home_id: int) -> str:
    """Prompt for property query node"""
    return f"""
    I need to get property details for HOME_ID {target_home_id}.
    Please use the query_home_by_id tool to fetch the property information.
    """


def get_analysis_prompt(budget_result: dict, property_result: dict) -> str:
    """Prompt for analysis node"""
    return f"""
    I have the following data to analyze:
    
    Budget Information:
    - Budget: ${budget_result.get('budget', 0):,.0f}
    - Income: ${budget_result.get('income', 0):,.0f}
    - Percentage: {budget_result.get('percentage', 0)*100}%
    
    Property Information:
    - Address: {property_result.get('address', 'N/A')}
    - Neighborhood: {property_result.get('neighborhood', 'N/A')}
    - Sale Price: ${property_result.get('sale_price', 0):,.0f}
    - Zip Code: {property_result.get('zip_code', 'N/A')}
    
    Please analyze the affordability and provide recommendations.
    Consider:
    1. Is the property within budget?
    2. What percentage of budget would be used?
    3. What are the key recommendations?
    
    Return a structured analysis with affordability status and recommendations.
    """


def get_synthesis_prompt(analysis: dict) -> str:
    """Prompt for synthesis node"""
    return f"""
    I have completed the analysis with the following results:
    {analysis}
    
    Please format this into a clean, final output that includes:
    1. Budget analysis summary
    2. Property details summary
    3. Affordability assessment
    4. Key recommendations
    
    Make it user-friendly and actionable.
    """
