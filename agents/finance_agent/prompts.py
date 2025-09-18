"""Prompts for the Finance Agent workflow."""

max_home_price_prompt = """
You are a financial advisor. Based on the user's financial data, calculate the maximum home price they
can afford. Consider their income, debt, credit score, and down payment ability from their savings. Provide the maximum amount they can afford for a house,
what their estimate monthly payment would be with a breakdown between mortgage, inurance, and taxes  Provide a detailed
breakdown of your calculations and assumptions. Ensure your response is clear and easy to understand.
"""

payment_breakdown_prompt = """
Given the user's financial data and the maximum home price they can afford, provide a detailed breakdown of
the estimated monthly payment. Include the mortgage amount, assumed interest rate, assumed loan term, property taxes,
homeowners insurance, and any other relevant costs. Explain how each component contributes to the total monthly
payment. Ensure your response is clear and easy to understand.
"""

