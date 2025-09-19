from langchain_openai import ChatOpenAI
from states.planner_state import PlannerState
from .prompts import PLANNER_PROMPT

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def assess_workflow(state: PlannerState):
    """Assess workflow state and determine what's needed next."""
    
    collected_data = state.get("collected_data", {})
    completed_agents = state.get("agents_completed", [])
    
    # Simple logic - no complex LLM needed
    next_agent, missing_fields, questions = determine_next_steps(collected_data, completed_agents)
    
    # Calculate progress
    progress = len(completed_agents) / 3.0
    
    return {
        "next_agent": next_agent,
        "missing_data_fields": missing_fields,
        "recommended_questions": questions,
        "workflow_progress": progress,
        "current_step": "assessment_complete",
        "step_count": state.get("step_count", 0) + 1
    }

def determine_next_steps(collected_data, completed_agents):
    """Pure function to determine next steps - no LLM needed."""
    
    # Check next agent in sequence
    if "finance" not in completed_agents:
        required = ["annual_income", "monthly_debt_payments", "credit_score"]
        missing = [f for f in required if not collected_data.get(f)]
        if missing:
            return "collect_data", missing, generate_questions(missing)
        return "finance", [], []
        
    elif "geo_scout" not in completed_agents:
        required = ["preferred_cities", "home_type_preference"]
        missing = [f for f in required if not collected_data.get(f)]
        if missing or not collected_data.get("finance_results"):
            return "collect_data", missing, generate_questions(missing)
        return "geo_scout", [], []
        
    elif "program_matcher" not in completed_agents:
        required = ["first_time_buyer", "military_veteran"]
        missing = [f for f in required if collected_data.get(f) is None]
        if missing or not collected_data.get("geo_scout_results"):
            return "collect_data", missing, generate_questions(missing)
        return "program_matcher", [], []
        
    else:
        return "complete", [], []

def generate_questions(missing_fields):
    """Generate questions for missing fields."""
    question_map = {
        "annual_income": "What's your annual gross income?",
        "monthly_debt_payments": "What are your monthly debt payments?", 
        "credit_score": "What's your credit score?",
        "preferred_cities": "Which cities interest you?",
        "home_type_preference": "House or condo preference?",
        "first_time_buyer": "Are you a first-time buyer?",
        "military_veteran": "Are you a veteran?"
    }
    return [question_map.get(field, f"Please provide {field}") for field in missing_fields[:2]]