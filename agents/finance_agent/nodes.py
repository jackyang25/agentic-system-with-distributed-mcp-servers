from dotenv import load_dotenv
import asyncio

from langchain_core.tools import tool


from agents.finance_agent.state import FinanceState
from mcp_kit.clients.finance_client import FinanceClient
from mcp_kit.clients.supabase_client import SupabaseClient


# Load environment variables from .env file
load_dotenv()



@tool
def finance_analysis_tool(data: str) -> str:

"""Nodes for the Finance Agent workflow."""
# instantiate clients
finance_client = FinanceClient()
supabase_client = SupabaseClient()
# nodes 
def user_info_intake(state: FinanceState) -> FinanceState:
    user_info = {
        'name': None,
        'salary': None,
        'rent': None,
        'rent_monthly': None,
        'expenses_monthly': None,
        'credit_score': None,
        'savings': None
    }
    print('Hello, what is your name')
    user_info['name'] = input()
    print(f'Thanks {user_info['name']}, now lets gather some information about you. enter Y or Yes to continue')
    cont = input()
    print('What is your gross annual salary?')
    user_info['salary'] = input()
    print('How much do you pay for rent monthly?')
    user_info['rent_monthly'] = input()
    print('How much are your other expenses monthly (e.g.,Car Payments, Student loans, etc?')
    user_info['expenses_monthly'] = input()
    print('What is your credit score?')
    user_info['credit_score'] = input()
    print('How much do you have in saving?')
    user_info['savings'] = input()

    return{
        **state,
        'messages':state['messages'],
        'current_step':'Info gathered',
        'step_count': state['step_count']+1,
        'workflow_status': 'in progress',
        'user_financial_data': user_info,
          
    }
    


def get_results(state: FinanceState) -> FinanceState:
    results = {
        'max_home_price': None,
        'readiness score': None,
        'monthly_payment': None,
        'mortgage': None,
        'insurance': None,
        'taxes': None,
        'savings recommendation':None
           
    }

    

    pass

async def connect_to_finance_mcp(client: FinanceClient): 

    print('Connecting to Finance MCP...')

    await client.connect()

    return "connected to Finance MCP"
    

async def connect_to_superbase_mcp(client: SupabaseClient):
    print('Connecting to Supabase MCP...')
    
    
    await client.connect()

    return "connected to Supabase MCP"



asyncio.run(connect_to_finance_mcp(finance_client))
asyncio.run(connect_to_superbase_mcp(supabase_client))


