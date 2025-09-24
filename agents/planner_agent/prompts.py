"""Prompts for the Planner Agent workflow."""

from typing import Any


def get_comprehensive_analysis_prompt(state: dict) -> str:
    """Generate comprehensive LLM prompt for data formatting and analysis"""
    # Extract all values from planner state
    budgeting_results: dict[str, Any] = state.get("budgeting_agent_results", {})
    program_results: str = state.get("program_agent_results", {}).get(
        "filtered_programs", None
    )
    geoscout_results: str = state.get("geoscout_agent_results", {}).get(
        "total_summary", None
    )
    price_data: dict[str, Any] = state.get("price_data", {})

    # Build the comprehensive prompt
    prompt: str = f"""
    You are a financial advisor helping someone with home buying. Based on their profile below, provide a comprehensive analysis:

    USER PROFILE
    - Income: ${state.get("income", 0.0):,.2f}
    - Credit Score: {state.get("credit_score", "N/A")}
    - Current Debt: ${state.get("current_debt", 0.0):,.2f}
    - Location: {state.get("zip_code", "N/A")} (State: {state.get("state", "N/A")})
    - Property Type: {state.get("building_class", "N/A")} with {state.get("residential_units", "N/A")} units
    - Identity/Status: {", ".join(state.get("who_i_am", [])) if state.get("who_i_am") else "Not specified"}
    - Looking For: {", ".join(state.get("what_looking_for", [])) if state.get("what_looking_for") else "Not specified"}

    FINANCIAL CONTEXT
    - Monthly Budget (30% of income): ${budgeting_results.get("monthly_budget", 0.0):,.2f}
    - Maximum Loan Qualification: ${budgeting_results.get("max_loan", 0.0):,.2f}
    - Market Data: Avg Price: ${price_data.get("average_sale_price", 0.0):,.2f} | Min: ${price_data.get("min_sale_price", 0.0):,.2f} | Max: ${price_data.get("max_sale_price", 0.0):,.2f} | Properties: {price_data.get("total_properties", "N/A")}
    """

    # Add program information if available
    if program_results:
        prompt += f"""

    ELIGIBLE GOVERNMENT PROGRAMS:
    {program_results}

    Note: Each program includes a source link for more information and application details. Include ALL program details provided - do not omit any information.
    """

    if geoscout_results:
        prompt += f"""

    SUMMARY OF NEIGHBORHOOD DATA:
    {geoscout_results}

    Note: This includes transit and crime information relevant to the property search.
    """

    prompt += """

    Please provide a concise analysis (max 500 words) that includes:

    1. FINANCIAL SUMMARY: Key metrics clearly (take into consideration current debt)
    2. NEIGHBORHOOD: Provide context of neighborhood, transit, and crime data
    2. READINESS: Financial readiness assessment
    3. GOVERNMENT PROGRAMS: List ALL eligible programs with complete details including name, jurisdiction, assistance type, benefits, source links, and eligibility reasoning
    4. RECOMMENDATIONS: 2-3 specific, actionable steps
    5. CONCERNS: Main issues to consider
    6. NEXT STEPS: Clear action items including program application links

    Keep it practical, actionable, and concise. Use bullet points where helpful.
    """

    return prompt
