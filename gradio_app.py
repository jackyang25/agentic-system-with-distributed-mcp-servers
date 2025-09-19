import asyncio
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mcp_kit.tools import mcp_adapter
from agents.planner_agent.graph import run_planner_agent

def _fmt_money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "N/A"

def format_planner_results(result):
    lines = []
    lines.append("# Home Buying Analysis\n")
    lines.append("## Data\n")

    if result.get("budgeting_agent_results"):
        budget = result["budgeting_agent_results"]
        lines.append(f"**Income:** {_fmt_money(budget.get('income'))}")
        lines.append(f"**Credit Score:** {budget.get('credit_score', 'N/A')}")
        lines.append(f"**Target Home ID:** {budget.get('target_home_id', 'N/A')}")
        lines.append(f"**Zip Code:** {budget.get('zip_code', 'N/A')}\n")

        budget_result = (budget.get('budget_result') or {}).get('budget') or {}
        loan_result   = (budget.get('loan_result') or {}).get('max_loan') or {}

        lines.append(f"**Monthly Budget:** {_fmt_money(budget_result.get('budget'))}")
        lines.append(f"**Max Loan:** {_fmt_money(loan_result.get('max_loan'))}\n")
    else:
        lines.append("No budgeting data available\n")

    lines.append("## Analysis\n")
    lines.append(result.get('final_analysis', 'No analysis available'))
    return "\n".join(lines)

# Make this async and await the agent
async def run_planner_with_ui(income, target_home_id, credit_score, zip_code):
    try:
        user_data = {
            "income": float(income),
            "target_home_id": int(target_home_id),
            "credit_score": int(credit_score),
            "zip_code": str(zip_code),
        }
        result = await run_planner_agent(user_data)
        return format_planner_results(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        return f"Error: {str(e)}"

def create_interface():
    with gr.Blocks(title="MAREA", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# MAREA")
        with gr.Row():
            with gr.Column():
                income = gr.Number(label="Annual Income ($)", value=75000, minimum=0, step=1000)
                target_home_id = gr.Number(label="Target Home ID", value=7, minimum=1, step=1)
                credit_score = gr.Number(label="Credit Score", value=720, minimum=300, maximum=850, step=10)
                zip_code = gr.Textbox(label="Zip Code", value="10009")
                analyze_btn = gr.Button("Analyze", variant="primary")
            with gr.Column():
                output = gr.Markdown(value="Enter your information and click 'Analyze' to get started.")

        # Gradio supports async fns—no asyncio.run() here
        analyze_btn.click(fn=run_planner_with_ui,
                          inputs=[income, target_home_id, credit_score, zip_code],
                          outputs=output)

        gr.Examples([[75000, 7, 720, "10009"], [95000, 12, 780, "90210"], [60000, 3, 680, "60601"]],
                    inputs=[income, target_home_id, credit_score, zip_code])

    return demo

# Create FastAPI app
app = FastAPI(title="MAREA API")

# Initialize MCP connections once
@app.on_event("startup")
async def startup():
    await mcp_adapter.connect_all()
    print(await mcp_adapter.check_running())
    print("MCP connections established")

# API endpoint for the planner agent
@app.post("/analyze")
async def analyze_endpoint(income: float, target_home_id: int, credit_score: int, zip_code: str):
    """API endpoint for the planner agent"""
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

# Mount Gradio app
demo = create_interface()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)