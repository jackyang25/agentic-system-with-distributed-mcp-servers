# Core imports
import asyncio
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mcp_kit.tools import mcp_adapter
from agents.planner_agent.graph import run_planner_agent  # Main logic entry point
from langchain_openai import ChatOpenAI
import threading
import webbrowser
import time

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
                    f"Location: {budget.get('zip_code', 'N/A')}")
        lines.append("─" * 60)
        lines.append("")

        # Collect all computed data
        computed_data = []
        
        # Financial data - use primitive values from result
        if result.get('monthly_budget'):
            computed_data.append(f"Monthly Budget: {_fmt_money(result.get('monthly_budget'))}")
        if result.get('max_loan'):
            computed_data.append(f"Max Loan: {_fmt_money(result.get('max_loan'))}")
        
        # Market data - use dictionary from result
        price_data = result.get('price_data', {})
        if price_data and isinstance(price_data, dict):
            if price_data.get('average_sale_price'):
                computed_data.append(f"Avg Price: {_fmt_money(price_data.get('average_sale_price'))}")
            if price_data.get('min_sale_price'):
                computed_data.append(f"Min Price: {_fmt_money(price_data.get('min_sale_price'))}")
            if price_data.get('max_sale_price'):
                computed_data.append(f"Max Price: {_fmt_money(price_data.get('max_sale_price'))}")
            if price_data.get('total_properties'):
                computed_data.append(f"Properties: {price_data.get('total_properties')}")
            if price_data.get('residential_units'):
                computed_data.append(f"Unit Type: {price_data.get('residential_units')}-unit")
        
        if computed_data:
            lines.append("<strong>Computed Data:</strong> " + " | ".join(computed_data))
            lines.append("─" * 60)
            lines.append("")

    analysis = result.get('final_analysis', 'No analysis available')
    if analysis and analysis != 'No analysis available':
        lines.append("<strong>Analysis:</strong>")
        lines.append(analysis)
    else:
        lines.append("<strong>Status:</strong> Analysis unavailable - please try again.")

    return "\n".join(lines)

# Chatbot function that uses analysis context
async def chatbot_response(message, history, analysis_context):
    """Generate chatbot response using the analysis context"""
    if not analysis_context or analysis_context == "No analysis available":
        return "I don't have access to your analysis results yet. Please run the analysis first."
    
    try:
        model = ChatOpenAI(
            model="gpt-4o-mini",
            timeout=30,
            max_retries=2
        )
        
        # Create a prompt that includes the analysis context
        system_prompt = f"""You are a helpful real estate assistant. The user has just received an analysis with the following information:

{analysis_context}

Please answer their questions about this analysis, provide clarifications, or help them understand their options. Be helpful, accurate, and refer to the specific details from their analysis when relevant."""

        # Format the conversation history
        conversation_history = []
        for user_msg, bot_msg in history:
            conversation_history.append({"role": "user", "content": user_msg})
            conversation_history.append({"role": "assistant", "content": bot_msg})
        
        # Add the current user message
        conversation_history.append({"role": "user", "content": message})
        
        # Create the messages for the API
        messages = [{"role": "system", "content": system_prompt}] + conversation_history
        
        response = await model.ainvoke(messages)
        return response.content
        
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."

# Global variable to store analysis context for chatbot
analysis_context = None

# Main UI handler - validates inputs and calls the planner agent
async def run_planner_with_ui(income, credit_score, who_i_am, state, what_looking_for, zip_code, building_class, residential_units, current_debt):
    try:
        if income is None or income == "":
            return "Error: Net Annual Income is required"
        if credit_score is None or credit_score == "":
            return "Error: Credit Score is required"
        if zip_code is None or zip_code == "":
            return "Error: Zip Code is required"
        if building_class is None or building_class == "":
            return "Error: Building Class is required"
        if residential_units is None or residential_units == "":
            return "Error: Residential Units is required"
        if current_debt is None or current_debt == "":
            return "Error: Current Debt is required"
        
        try:
            income_val = float(income)
            credit_score_val = int(credit_score)
            residential_units_val = int(residential_units)
            current_debt_val = float(current_debt)
        except (ValueError, TypeError):
            return "Error: Invalid numeric values provided"
        
        if income_val <= 0:
            return "Error: Net Annual Income must be greater than 0"
        if credit_score_val < 300 or credit_score_val > 850:
            return "Error: Credit Score must be between 300 and 850"
        if residential_units_val <= 0:
            return "Error: Residential Units must be greater than 0"
        if current_debt_val < 0:
            return "Error: Current Debt must be 0 or greater"
        
        # Convert selections to RAG keywords
        rag_parts = []
        if who_i_am:
            rag_parts.extend(who_i_am)
        if state and state != "ANY":
            rag_parts.append(state)
        if what_looking_for:
            rag_parts.extend(what_looking_for)
        
        rag_keywords = ", ".join(rag_parts) if rag_parts else ""
        
        # Prepare data for the planner agent
        user_data = {
            "income": income_val,
            "credit_score": credit_score_val,
            "rag_keywords": rag_keywords,
            "zip_code": str(zip_code),
            "building_class": str(building_class),
            "residential_units": residential_units_val,
            "current_debt": current_debt_val,
        }
        
        print(f"[MAREA] User input received: {user_data}")
        
        # ENTRY POINT: Call the main planner agent logic
        result = await run_planner_agent(user_data)
        formatted_result = format_planner_results(result)
        
        # Store analysis context for chatbot
        global analysis_context
        analysis_context = formatted_result
        
        print("Analysis complete. Chatbot is now available in the 'Chat' tab.")
        
        # Return the formatted result
        return formatted_result
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
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
            padding: 20px !important;
            border: 1px solid #333 !important;
            border-radius: 8px !important;
            height: 1200px !important;
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
            height: 1200px !important;
            overflow-y: auto !important;
            background-color: #1a1a1a !important;
            color: #6b7280 !important;
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
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
            max-height: 1200px !important;
            overflow-y: auto !important;
            height: 1000px !important;
            height: 1200px !important;
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
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
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
        
        /* GitHub logo alignment fix */
        .gradio-markdown h1 {
            line-height: 1.4 !important;
            margin: 0 !important;
            height: auto !important;
        }
        .gradio-markdown h1 span {
            display: inline-flex !important;
            align-items: center !important;
            vertical-align: middle !important;
        }
        .gradio-markdown h1 svg {
            width: 20px !important;
            height: 20px !important;
            margin-right: 8px !important;
            flex-shrink: 0 !important;
            vertical-align: middle !important;
            display: inline-block !important;
        }
    """) as demo:
        gr.Markdown("# <div style='display: inline-flex; align-items: baseline;'><svg width='20' height='20' viewBox='0 0 20 20' fill='none' xmlns='http://www.w3.org/2000/svg' style='display: inline; vertical-align: text-bottom; margin-right: 8px;'><path d='M10 0C4.477 0 0 4.477 0 10 0 14.418 2.865 18.167 6.839 19.489c.5.092.661-.217.661-.482v-1.862c-2.785.606-3.361-1.18-3.361-1.18-.455-1.156-1.111-1.463-1.111-1.463-.908-.62.069-.608.069-.608 1.005.07 1.533 1.031 1.533 1.031.892 1.529 2.341 1.087 2.91.831.089-.646.35-1.087.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.092.39-1.984 1.03-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.293 2.747-1.025 2.747-1.025.546 1.379.203 2.398.1 2.647.64.699 1.025 1.591 1.025 2.683 0 3.842-2.339 4.687-4.566 4.943.358.309.683.919.683 1.856v2.75c0 .266.18.572.681.475C17.138 18.167 20 14.418 20 10c0-5.523-4.477-10-10-10z' fill='#6B7280'/></svg>MAREA</div>")
        gr.Markdown("<hr style='border: none; border-top: 1px solid #6B7280; margin: 3px 0 2px 0; width: 40%;'>")
        gr.Markdown("<span style='color: #6B7280;'>Secure Your Dream Home, Powered by AI.</span>")
        
        # Create tabs
        with gr.Tabs():
            with gr.Tab("Analysis"):
                with gr.Row():
                    with gr.Column(elem_id="left-panel"):
                        # Financial Information
                        income = gr.Number(label="Net Annual Income ($)", value=75000, minimum=0, step=1000)
                        current_debt = gr.Number(label="Current Debt ($)", value=0, minimum=0, step=1000)
                        credit_score = gr.Number(label="Credit Score", value=720, minimum=300, maximum=850, step=10)
                        
                        # Location Information
                        state = gr.Dropdown(
                            label="State",
                            choices=[
                                "ANY",
                                "New York",
                                "New Jersey",
                                "Connecticut",
                                "Pennsylvania"
                            ],
                            value="New York"
                        )
                        zip_code = gr.Textbox(label="Zip Code", value="10009")
                        
                        # Who I Am - RAG Keywords
                        who_i_am = gr.CheckboxGroup(
                            label="Who I Am (check all that apply)",
                            choices=[
                                "Veteran",
                                "Recent Graduate", 
                                "First Time Home Buyer",
                                "Low Income",
                                "Senior Citizen",
                                "Disabled"
                            ],
                            value=["First Time Home Buyer"]
                        )
                        
                        # What I'm Looking For - Multi-select
                        what_looking_for = gr.CheckboxGroup(
                            label="What I'm Looking For (check all that apply)",
                            choices=[
                                "Down Payment Assistance",
                                "Low Interest Rate",
                                "Mortgage Assistance",
                                "Renovation Programs",
                                "Affordable Housing"
                            ],
                            value=["Down Payment Assistance"]
                        )
                        
                        # Property Information
                        building_class = gr.Dropdown(
                            label="Building Class",
                            choices=[
                                "Any - All building types",
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
                            value="Any - All building types"
                        )
                        
                        # Property Details
                        residential_units = gr.Number(label="Residential Units", value=1, minimum=1, step=1)
                        
                        analyze_btn = gr.Button("Analyze", variant="primary", size="lg")

                    with gr.Column(elem_id="outer-panel"):
                        output = gr.Markdown(
                            value="<div style='text-align: center; padding: 20px;'><div class='rotating-squares'><div class='square1'></div><div class='square2'></div></div><div style='color: #6b7280; font-size: 14px; font-family: Courier New, monospace;'>Enter your information to get started.</div></div>",
                            elem_classes=["output-markdown"]
                        )
                    
                    # Connect the analyze button to the main handler
                    analyze_btn.click(fn=run_planner_with_ui,
                                      inputs=[income, credit_score, who_i_am, state, what_looking_for, zip_code, building_class, residential_units, current_debt],
                                      outputs=output)

            with gr.Tab("Chat"):
                chatbot = gr.Chatbot(label="Chat with Assistant", height=400)
                chatbot_input = gr.Textbox(
                    label="Your question", 
                    placeholder="Ask me anything about your analysis...",
                    lines=2
                )
                chatbot_send = gr.Button("Send", variant="primary")
                
                def handle_chatbot(message, history):
                    """Handle chatbot interactions with analysis context"""
                    global analysis_context
                    
                    if not message.strip():
                        return history, ""
                    
                    if not analysis_context or analysis_context == "No analysis available":
                        history.append((message, "I don't have access to your analysis results yet. Please run the analysis first."))
                        return history, ""
                    
                    # Add user message to history
                    history.append((message, ""))
                    
                    # Get bot response
                    try:
                        response = asyncio.run(chatbot_response(message, history[:-1], analysis_context))
                        history[-1] = (message, response)
                    except Exception as e:
                        history[-1] = (message, f"Error: {str(e)}")
                    
                    return history, ""
                
                # Connect chatbot send button
                chatbot_send.click(
                    fn=handle_chatbot,
                    inputs=[chatbot_input, chatbot],
                    outputs=[chatbot, chatbot_input]
                )
                
                # Allow Enter key to send message
                chatbot_input.submit(
                    fn=handle_chatbot,
                    inputs=[chatbot_input, chatbot],
                    outputs=[chatbot, chatbot_input]
                )
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
async def analyze_endpoint(income: float, credit_score: int, zip_code: str):
    try:
        user_data = {
            "income": income,
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

# TODO: RAG program agent and PgVector table
# TODO: Chatbot after analysis with memory of planner state and conversation
