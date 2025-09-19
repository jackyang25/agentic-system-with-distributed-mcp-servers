"""Prompts for the Planner Agent workflow."""

def get_comprehensive_analysis_prompt(budgeting_results: dict) -> str:
    """Generate comprehensive LLM prompt for data formatting and analysis"""
    # Extract the actual values from the nested structure
    budget_value = budgeting_results.get('budget_result', {}).get('budget', {}).get('budget', 'N/A')
    loan_value = budgeting_results.get('loan_result', {}).get('max_loan', {}).get('max_loan', 'N/A')
    
    return f"""
    You are a financial advisor helping someone with home buying. Based on their financial data below, provide a comprehensive analysis:

    FINANCIAL DATA:
    - Income: ${budgeting_results.get('income', 'N/A'):,.2f}
    - Credit Score: {budgeting_results.get('credit_score', 'N/A')}
    - Monthly Budget (30% of income): ${budget_value:,.2f}
    - Maximum Loan Qualification: ${loan_value:,.2f}

    Please provide a concise analysis (max 300 words) that includes:

    1. FINANCIAL SUMMARY: Key metrics clearly
    2. READINESS: Financial readiness assessment
    3. RECOMMENDATIONS: 2-3 specific, actionable steps
    4. CONCERNS: Main issues to consider
    5. NEXT STEPS: Clear action items

    Keep it practical, actionable, and concise. Use bullet points where helpful.
    """
