import asyncio
from logging import Logger
from pathlib import Path
from typing import Any, Literal

import gradio as gr
from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI

from agents.planner_agent.graph import run_planner_agent
from utils.convenience import get_logger, get_openai_model

logger: Logger = get_logger(name=__name__)

openai_model: str = get_openai_model()

local_dir: Path = Path(__file__).parent


def format_planner_results(result: Any) -> Any:
    # Return only the generated analysis from the agents
    analysis: Any = result.get("final_analysis", "No analysis available")
    if analysis and analysis != "No analysis available":
        return analysis
    else:
        return "Analysis unavailable - please try again."


# Chatbot function that uses analysis context
async def chatbot_response(
    message: str, history: list[tuple[str, str]], analysis_context: Any
):
    """Generate chatbot response using the analysis context"""
    if not analysis_context or analysis_context == "No analysis available":
        return "I don't have access to your analysis results yet. Please run the analysis first."

    try:
        model = ChatOpenAI(model=openai_model, timeout=30, max_retries=2)

        # Create a prompt that includes the analysis context
        system_prompt: str = f"""You are a helpful real estate assistant. The user has just received an analysis with the following information:

{analysis_context}

Please answer their questions about this analysis, provide clarifications, or help them understand their options. Be helpful, accurate, and refer to the specific details from their analysis when relevant."""

        # Format the conversation history
        conversation_history: list[Any] = []
        for user_msg, bot_msg in history:
            conversation_history.append({"role": "user", "content": user_msg})
            conversation_history.append({"role": "assistant", "content": bot_msg})

        # Add the current user message
        conversation_history.append({"role": "user", "content": message})

        # Create the messages for the API
        messages = [{"role": "system", "content": system_prompt}] + conversation_history

        response: BaseMessage = await model.ainvoke(input=messages)
        return response.content

    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."


async def run_planner_with_ui(
    income: int,
    credit_score: int,
    who_i_am: list[str],
    state: str,
    what_looking_for: list[str],
    zip_code: str,
    building_class: str,
    current_debt: int,
) -> Any:
    residential_units = 1
    try:
        if income is None or income == "":
            return "Error: Gross Annual Income is required"
        if credit_score is None or credit_score == "":
            return "Error: Credit Score is required"
        if zip_code is None or zip_code == "":
            return "Error: Zip Code is required"
        if building_class is None or building_class == "":
            return "Error: Building Class is required"
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
            return "Error: Annual Income must be greater than 0"
        if credit_score_val < 300 or credit_score_val > 850:
            return "Error: Credit Score must be between 300 and 850"
        if current_debt_val < 0:
            return "Error: Current Debt must be 0 or greater"

        # Prepare data for the planner agent
        user_data: dict[str, Any] = {
            "income": income_val,
            "credit_score": credit_score_val,
            "who_i_am": who_i_am if who_i_am else [],
            "state": state if state != "ANY" else None,
            "what_looking_for": what_looking_for if what_looking_for else [],
            "zip_code": str(zip_code),
            "building_class": str(building_class),
            "residential_units": residential_units_val,
            "current_debt": current_debt_val,
        }

        logger.info(f"[MAREA] User input received: {user_data}")

        # ENTRY POINT: Call the main planner agent logic
        result: Any = await run_planner_agent(user_data=user_data)
        formatted_result: Any = format_planner_results(result=result)

        # Store analysis context for chatbot
        global analysis_context
        analysis_context = formatted_result

        logger.info("Analysis complete. Chatbot is now available in the 'Chat' tab.")

        # Return the formatted result
        return formatted_result
    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error: {str(e)}"


def handle_chatbot(
    message: str, history: list[dict[str, str]]
) -> tuple[list[dict[str, str]], Literal[""]]:
    """Handle chatbot interactions with analysis context"""
    global analysis_context

    if not message.strip():
        return history, ""

    if not analysis_context or analysis_context == "No analysis available":
        history.append({"role": "user", "content": message})
        history.append(
            {
                "role": "assistant",
                "content": "I don't have access to your analysis results yet. Please run the analysis first.",
            }
        )
        return history, ""

    # Add user message to history
    history.append({"role": "user", "content": message})

    # Get bot response
    try:
        # Convert history to old format for the chatbot_response function
        old_format_history: list[tuple[str, str]] = []
        for msg in history[:-1]:  # Exclude the current user message
            if msg["role"] == "user":
                old_format_history.append((msg["content"], ""))
            elif msg["role"] == "assistant" and old_format_history:
                old_format_history[-1] = (
                    old_format_history[-1][0],
                    msg["content"],
                )

        response: Any = asyncio.run(
            main=chatbot_response(
                message=message,
                history=old_format_history,
                analysis_context=analysis_context,
            )
        )
        history.append({"role": "assistant", "content": response})
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})

    return history, ""


def create_interface() -> gr.Blocks:
    with open(file=local_dir / "css.txt", mode="r", encoding="utf-8") as f:
        custom_css: str = f.read()
    with gr.Blocks(
        title="MAREA",
        theme=gr.themes.Monochrome(),
        css=custom_css,
    ) as demo:
        gr.Markdown(
            value="# <div style='display: inline-flex; align-items: baseline;'><svg width='20' height='20' viewBox='0 0 20 20' fill='none' xmlns='http://www.w3.org/2000/svg' style='display: inline; vertical-align: text-bottom; margin-right: 8px;'><path d='M10 0C4.477 0 0 4.477 0 10 0 14.418 2.865 18.167 6.839 19.489c.5.092.661-.217.661-.482v-1.862c-2.785.606-3.361-1.18-3.361-1.18-.455-1.156-1.111-1.463-1.111-1.463-.908-.62.069-.608.069-.608 1.005.07 1.533 1.031 1.533 1.031.892 1.529 2.341 1.087 2.91.831.089-.646.35-1.087.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.092.39-1.984 1.03-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.293 2.747-1.025 2.747-1.025.546 1.379.203 2.398.1 2.647.64.699 1.025 1.591 1.025 2.683 0 3.842-2.339 4.687-4.566 4.943.358.309.683.919.683 1.856v2.75c0 .266.18.572.681.475C17.138 18.167 20 14.418 20 10c0-5.523-4.477-10-10-10z' fill='#6B7280'/></svg>MAREA</div>"
        )
        gr.Markdown(
            value="<hr style='border: none; border-top: 1px solid #6B7280; margin: 3px 0 2px 0; width: 40%;'>"
        )
        gr.Markdown(
            value="<span style='color: #6B7280;'>Secure Your Dream Home, Powered by AI.</span>"
        )

        # Create tabs
        with gr.Tabs():
            with gr.Tab(label="Analysis"):
                with gr.Row():
                    with gr.Column(elem_id="left-panel"):
                        # Financial Information
                        income = gr.Number(
                            label="Gross Annual Income ($)",
                            value=75000,
                            minimum=0,
                            step=1000,
                        )
                        current_debt = gr.Number(
                            label="Current Debt ($)", value=0, minimum=0, step=1000
                        )
                        credit_score = gr.Number(
                            label="Credit Score",
                            value=720,
                            minimum=300,
                            maximum=850,
                            step=10,
                        )

                        # Location Information
                        state = gr.Dropdown(
                            label="State",
                            choices=[
                                "ANY",
                                "New York",
                                "New Jersey",
                                "Connecticut",
                                "Pennsylvania",
                            ],
                            value="New York",
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
                                "Disabled",
                            ],
                            value=["First Time Home Buyer"],
                        )

                        # What I'm Looking For - Multi-select
                        what_looking_for = gr.CheckboxGroup(
                            label="What I'm Looking For (check all that apply)",
                            choices=[
                                "Down Payment Assistance",
                                "Low Interest Rate",
                                "Mortgage Assistance",
                                "Renovation Programs",
                                "Affordable Housing",
                            ],
                            value=["Down Payment Assistance"],
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
                                "O9 - Office building (9+ stories)",
                            ],
                            value="Any - All building types",
                        )

                        analyze_btn = gr.Button("Analyze", variant="primary", size="lg")

                    with gr.Column(elem_id="outer-panel"):
                        output = gr.Markdown(
                            value="<div style='text-align: center; padding: 20px;'><div class='rotating-squares'><div class='square1'></div><div class='square2'></div></div><div style='color: #6b7280; font-size: 14px; font-family: Courier New, monospace;'>Enter your information to get started.</div></div>",
                            elem_classes=["output-markdown"],
                        )

                    # Connect the analyze button to the main handler
                    analyze_btn.click(
                        fn=run_planner_with_ui,
                        inputs=[
                            income,
                            credit_score,
                            who_i_am,
                            state,
                            what_looking_for,
                            zip_code,
                            building_class,
                            current_debt,
                        ],
                        outputs=output,
                    )

            with gr.Tab(label="Chat"):
                chatbot: gr.Chatbot = gr.Chatbot(
                    label="Chat with Assistant", height=400, type="messages"
                )
                chatbot_input: gr.Textbox = gr.Textbox(
                    label="Your question",
                    placeholder="Ask me anything about your analysis...",
                    lines=2,
                )
                chatbot_send: gr.Button = gr.Button(value="Send", variant="primary")

                # Connect chatbot send button
                # RemotePdb(host="localhost", port=4444).set_trace()
                chatbot_send.click(
                    fn=handle_chatbot,
                    inputs=[chatbot_input, chatbot],
                    outputs=[chatbot, chatbot_input],
                )

                # Allow Enter key to send message
                chatbot_input.submit(
                    fn=handle_chatbot,
                    inputs=[chatbot_input, chatbot],
                    outputs=[chatbot, chatbot_input],
                )
    return demo
