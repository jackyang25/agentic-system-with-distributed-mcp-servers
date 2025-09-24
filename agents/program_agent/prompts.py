"""Prompts for the Program Agent workflow."""


def format_user_profile(state) -> str:
    """Format user profile for LLM filtering"""
    who_i_am = state.get("who_i_am", [])
    state_location = state.get("state", "")
    income = state.get("income")
    credit_score = state.get("credit_score")
    zip_code = state.get("zip_code")
    building_class = state.get("building_class")
    current_debt = state.get("current_debt")
    residential_units = state.get("residential_units")

    return f"""
    User Profile:
    - Identity/Status: {", ".join(who_i_am) if who_i_am else "Not specified"}
    - State: {state_location if state_location else "Not specified"}
    - Income: ${income:,.0f} annually
    - Credit Score: {credit_score}
    - Zip Code: {zip_code}
    - Building Class: {building_class}
    - Current Debt: ${current_debt:,.0f}
    - Residential Units: {residential_units}
    """


def format_program_summary(program) -> str:
    """Format program details for LLM filtering"""
    return f"""
    Program: {program.get("program_name", "")}
    Eligibility: {program.get("eligibility", "")}
    Assistance Type: {program.get("assistance_type", "")}
    Jurisdiction: {program.get("jurisdiction", "")}
    Benefits: {program.get("max_benefit", "")}
    """


def create_batch_eligibility_prompt(user_profile, programs_text) -> str:
    """Create the LLM prompt for batch program eligibility filtering"""

    return f"""
    You are an expert in government assistance programs. Evaluate the programs below for user eligibility.
    
    {user_profile}
    
    {programs_text}
    
    For each program, determine if the user is eligible based on:
    - Identity/status requirements (veteran, first-time buyer, senior, etc.)
    - Location requirements (state-specific vs national programs)
    - Income requirements (if mentioned in eligibility criteria)
    - Credit score requirements (if mentioned in eligibility criteria)
    - Property type requirements (single-family, multi-family, etc.)
    - Debt-to-income considerations
    - Any other eligibility criteria mentioned
    
    Respond with a JSON array containing ONLY the programs the user is eligible for. Each element should have:
    {{"program_name": "Program Name", "jurisdiction": "State/National", "assistance_type": "Type of assistance", "max_benefit": "Benefit amount", "source": "URL", "reason": "concise explanation with key eligibility details"}}
    
    Example:
    [
        {{"program_name": "FHA Loan", "jurisdiction": "National", "assistance_type": "Mortgage Insurance", "max_benefit": "Up to $500,000", "source": "https://hud.gov/fha", "reason": "Credit score 650 meets 580+ requirement, income $75k sufficient"}},
        {{"program_name": "NYS First-Time Homebuyer", "jurisdiction": "New York State", "assistance_type": "Down Payment Assistance", "max_benefit": "Up to $15,000", "source": "https://nyshcr.org", "reason": "First-time buyer in NY with income within limits"}}
    ]
    """
