# Core imports
import asyncio
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mcp_kit.tools import mcp_adapter
from agents.planner_agent.graph import run_planner_agent  # Main logic entry point

# Utility function for money formatting
def _fmt_money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "N/A"

# Formats the planner agent results for display
def format_planner_results(result):
    lines = []

    if result.get("budgeting_agent_results"):
        budget = result["budgeting_agent_results"]
        lines.append("<strong>Profile:</strong> " + f"Income: {_fmt_money(budget.get('income'))} | " + 
                    f"Credit: {budget.get('credit_score', 'N/A')} | " + 
                    f"Home ID: {budget.get('target_home_id', 'N/A')} | " + 
                    f"Location: {budget.get('zip_code', 'N/A')}")
        lines.append("─" * 60)
        lines.append("")

        budget_result = (budget.get('budget_result') or {}).get('budget') or {}
        loan_result = (budget.get('loan_result') or {}).get('max_loan') or {}
        
        financial_info = []
        if budget_result.get('budget'):
            financial_info.append(f"Yearly Budget: {_fmt_money(budget_result.get('budget'))}")
        if loan_result.get('max_loan'):
            financial_info.append(f"Max Loan: {_fmt_money(loan_result.get('max_loan'))}")
        
        if financial_info:
            lines.append("<strong>Financial:</strong> " + " | ".join(financial_info))
            lines.append("─" * 60)
            lines.append("")

    analysis = result.get('final_analysis', 'No analysis available')
    if analysis and analysis != 'No analysis available':
        lines.append("<strong>Analysis:</strong>")
        lines.append(analysis)
    else:
        lines.append("<strong>Status:</strong> Analysis unavailable - please try again.")

    return "\n".join(lines)

# Main UI handler - validates inputs and calls the planner agent
async def run_planner_with_ui(income, target_home_id, credit_score, zip_code, building_class, residential_units, gross_square_feet, year_built, current_debt):
    try:
        if income is None or income == "":
            return "Error: Net Annual Income is required"
        if target_home_id is None or target_home_id == "":
            return "Error: Target Home ID is required"
        if credit_score is None or credit_score == "":
            return "Error: Credit Score is required"
        if zip_code is None or zip_code == "":
            return "Error: Zip Code is required"
        if building_class is None or building_class == "":
            return "Error: Building Class is required"
        if residential_units is None or residential_units == "":
            return "Error: Residential Units is required"
        if gross_square_feet is None or gross_square_feet == "":
            return "Error: Gross Square Feet is required"
        if year_built is None or year_built == "":
            return "Error: Year Built is required"
        if current_debt is None or current_debt == "":
            return "Error: Current Debt is required"
        
        try:
            income_val = float(income)
            target_home_id_val = int(target_home_id)
            credit_score_val = int(credit_score)
            residential_units_val = int(residential_units)
            gross_square_feet_val = float(gross_square_feet)
            year_built_val = int(year_built)
            current_debt_val = float(current_debt)
        except (ValueError, TypeError):
            return "Error: Invalid numeric values provided"
        
        if income_val <= 0:
            return "Error: Net Annual Income must be greater than 0"
        if target_home_id_val <= 0:
            return "Error: Target Home ID must be greater than 0"
        if credit_score_val < 300 or credit_score_val > 850:
            return "Error: Credit Score must be between 300 and 850"
        if residential_units_val <= 0:
            return "Error: Residential Units must be greater than 0"
        if gross_square_feet_val <= 0:
            return "Error: Gross Square Feet must be greater than 0"
        if year_built_val < 1800 or year_built_val > 2024:
            return "Error: Year Built must be between 1800 and 2024"
        if current_debt_val < 0:
            return "Error: Current Debt must be 0 or greater"
        
        # Prepare data for the planner agent
        user_data = {
            "income": income_val,
            "target_home_id": target_home_id_val,
            "credit_score": credit_score_val,
            "zip_code": str(zip_code),
            "building_class": str(building_class),
            "residential_units": residential_units_val,
            "gross_square_feet": gross_square_feet_val,
            "year_built": year_built_val,
            "current_debt": current_debt_val,
        }
        
        print(f"[MAREA] User input received: {user_data}")
        
        # ENTRY POINT: Call the main planner agent logic
        result = await run_planner_agent(user_data)
        return format_planner_results(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return f"Error: {str(e)}"

# Creates the Gradio UI interface
def create_interface():
    with gr.Blocks(title="MAREA", theme=gr.themes.Monochrome(), css="""
        /* LEFT PANEL styling */
        #left-panel {
            background-color: #1a1a1a !important;
            color: #6b7280 !important;
            font-family: 'Courier New', monospace !important;
            padding: 20px !important;
            border: 1px solid #333 !important;
            border-radius: 8px !important;
        }

        /* remove grey background from default inner form containers */
        #left-panel .gr-box,
        #left-panel .gr-panel {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* RIGHT PANEL styling */
        #outer-panel {
            height: 100% !important;
            overflow-y: auto !important;
            background-color: #1a1a1a !important;
            color: #6b7280 !important;
            font-family: 'Courier New', monospace !important;
            padding: 20px !important;
            border: 1px solid #333 !important;
            border-radius: 8px !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }

        /* INNER OUTPUT: remove extra border */
        #outer-panel .output-markdown,
        #outer-panel .gradio-markdown,
        #outer-panel .gradio-markdown .markdown,
        #outer-panel .output-markdown .markdown,
        #outer-panel .output-markdown .gr-box,
        #outer-panel .output-markdown .gr-panel {
            border: none !important;
            box-shadow: none !important;
            background-color: #1a1a1a !important;
            color: #6b7280 !important;
        }

        /* Scroll and spacing for inner output */
        #outer-panel .output-markdown {
            max-height: 1000px !important;
            overflow-y: auto !important;
            height: 1000px !important;
            display: block !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }

        /* Tight text alignment inside */
        #outer-panel .output-markdown .markdown {
            padding: 0 !important;
            margin: 0 !important;
        }

        .gradio-row { align-items: flex-start !important; }
        .gradio-row input, .gradio-row select, .gradio-row textarea, .gradio-row label {
            font-family: 'Courier New', monospace !important;
        }
        .gradio-column:first-child input, .gradio-column:first-child select, .gradio-column:first-child textarea {
            border-radius: 6px !important;
        }

        /* Spinner */
        .rotating-squares { position: relative; width: 50px; height: 50px; margin: 200px auto 30px auto; }
        .square1, .square2 {
            position: absolute; top: 0; left: 0; width: 50px; height: 50px;
            border: 2px dashed #6b7280; background-color: transparent;
        }
        .square2 { transform: translate(5px, 5px); }
        .square1 { animation: rotate-clockwise 3s linear infinite; }
        .square2 { animation: rotate-counter-clockwise 3s linear infinite; }
        @keyframes rotate-clockwise { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
        @keyframes rotate-counter-clockwise { from { transform: rotate(0deg);} to { transform: rotate(-360deg);} }
    """) as demo:
        gr.Markdown("# <span style='display: inline-flex; align-items: center;'><svg width='20' height='20' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg' style='margin-right: 8px;'><path d='M12 0C5.374 0 0 5.373 0 12 0 17.302 3.438 21.8 8.207 23.387c.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z' fill='#6B7280'/></svg>MAREA</span>")
        gr.Markdown("<hr style='border: none; border-top: 1px solid #6B7280; margin: 3px 0 2px 0; width: 40%;'>")
        gr.Markdown("<span style='color: #6B7280;'>Smarter Home Buying, Powered by AI.</span>")
        
        with gr.Row():
            with gr.Column(elem_id="left-panel"):
                # Financial Information
                income = gr.Number(label="Net Annual Income ($)", value=75000, minimum=0, step=1000)
                current_debt = gr.Number(label="Current Debt ($)", value=0, minimum=0, step=1000)
                credit_score = gr.Number(label="Credit Score", value=720, minimum=300, maximum=850, step=10)
                
                # Property Information
                target_home_id = gr.Number(label="Target Home ID", value=7, minimum=1, step=1)
                zip_code = gr.Textbox(label="Zip Code", value="10009")
                building_class = gr.Dropdown(
                    label="Building Class",
                    choices=[
                        "A0 - Cape Cod one family home",
                        "A1 - One family attached home",
                        "A2 - One family semi-attached home", 
                        "A3 - One family detached home",
                        "A4 - One family attached home (2-3 stories)",
                        "A5 - One family semi-attached home (2-3 stories)",
                        "A6 - One family detached home (2-3 stories)",
                        "A7 - One family attached home (4+ stories)",
                        "A8 - One family semi-attached home (4+ stories)",
                        "A9 - One family detached home (4+ stories)",
                        "B1 - Two family home",
                        "B2 - Two family home (2-3 stories)",
                        "B3 - Two family home (4+ stories)",
                        "C0 - Walk-up apartment building",
                        "C1 - Walk-up apartment building (2-3 stories)",
                        "C2 - Walk-up apartment building (4+ stories)",
                        "C3 - Walk-up apartment building (5+ stories)",
                        "C4 - Walk-up apartment building (6+ stories)",
                        "C5 - Walk-up apartment building (7+ stories)",
                        "C6 - Walk-up apartment building (8+ stories)",
                        "C7 - Walk-up apartment building (9+ stories)",
                        "C8 - Walk-up apartment building (10+ stories)",
                        "C9 - Walk-up apartment building (11+ stories)",
                        "D0 - Elevator apartment building",
                        "D1 - Elevator apartment building (2-3 stories)",
                        "D2 - Elevator apartment building (4+ stories)",
                        "D3 - Elevator apartment building (5+ stories)",
                        "D4 - Elevator apartment building (6+ stories)",
                        "D5 - Elevator apartment building (7+ stories)",
                        "D6 - Elevator apartment building (8+ stories)",
                        "D7 - Elevator apartment building (9+ stories)",
                        "D8 - Elevator apartment building (10+ stories)",
                        "D9 - Elevator apartment building (11+ stories)",
                        "R0 - Condominium unit",
                        "R1 - Condominium unit (1 story)",
                        "R2 - Condominium unit (2-3 stories)",
                        "R3 - Condominium unit (4+ stories)",
                        "R4 - Condominium unit (5+ stories)",
                        "R5 - Commercial condominium unit",
                        "R6 - Condominium unit (6+ stories)",
                        "R7 - Condominium unit (7+ stories)",
                        "R8 - Condominium unit (8+ stories)",
                        "R9 - Condominium unit (9+ stories)",
                        "O0 - Office building",
                        "O1 - Office building (1 story)",
                        "O2 - Office building (2-3 stories)",
                        "O3 - Office building (4+ stories)",
                        "O4 - Office building (tower type)",
                        "O5 - Office building (5+ stories)",
                        "O6 - Office building (6+ stories)",
                        "O7 - Office building (7+ stories)",
                        "O8 - Office building (8+ stories)",
                        "O9 - Office building (9+ stories)"
                    ],
                    value="A0 - Cape Cod one family home"
                )
                
                # Property Details
                residential_units = gr.Number(label="Residential Units", value=1, minimum=1, step=1)
                gross_square_feet = gr.Number(label="Gross Square Feet", value=1200, minimum=1, step=100)
                year_built = gr.Number(label="Year Built", value=2000, minimum=1800, maximum=2024, step=1)
                
                analyze_btn = gr.Button("Analyze", variant="primary", size="lg")

            with gr.Column(elem_id="outer-panel"):
                output = gr.Markdown(
                    value="<div style='text-align: center; padding: 20px;'><div class='rotating-squares'><div class='square1'></div><div class='square2'></div></div><div style='color: #6b7280; font-size: 14px; font-family: Courier New, monospace;'>Enter your information to get started.</div></div>",
                    elem_classes=["output-markdown"]
                )

        # Connect the analyze button to the main handler
        analyze_btn.click(fn=run_planner_with_ui,
                          inputs=[income, target_home_id, credit_score, zip_code, building_class, residential_units, gross_square_feet, year_built, current_debt],
                          outputs=output)
    return demo

# FastAPI app setup
app = FastAPI(title="MAREA API")

# Initialize MCP connections on startup
@app.on_event("startup")
async def startup():
    await mcp_adapter.connect_all()
    print(await mcp_adapter.check_running())
    print("MCP connections established")

# API endpoint for external access
@app.post("/analyze")
async def analyze_endpoint(income: float, target_home_id: int, credit_score: int, zip_code: str):
    try:
        user_data = {
            "income": income,
            "target_home_id": target_home_id,
            "credit_score": credit_score,
            "zip_code": zip_code,
        }
        result = await run_planner_agent(user_data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Mount the Gradio interface to FastAPI
demo = create_interface()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)