The Challenge
"By the age of 30, only about 42 percent of millennials owned a home. That compares to 48 percent of Generation X and 51 percent of Baby Boomers."
Many first-time buyers face high costs, debt, and a maze of programs. This project helps check a basic budget, find affordable neighborhoods, and surface relevant assistance programs.

Quick Start
1) Create a .env file. See "Environment variables (.env)" below.  
2) Start services:  
   make start  
   or: docker compose up --build -d  
3) Open:  
   Web: http://localhost:8000  
   API docs: http://localhost:8000/docs  
4) Stop:  
   make stop  

Environment variables (.env)
Required  
  OPENAI_API_KEY=your_openai_api_key_here  
  OPENAI_MODEL=gpt-4o-mini  
  GEMINI_MODEL=gemini-2.5-flash  
  WALKSCORE_API_KEY=your_walkscore_api  
  SUPABASE_PROJECT_REF=your_supabase_project_ref  
  SUPABASE_ACCESS_TOKEN=your_supabase_access_token  

Services
planner_agent     - Orchestrates the workflow and combines final output  
budgeting_agent   - Calculates basic affordability and budget guidance  
program_agent     - Suggests assistance programs that may match the profile  
geoscout_agent    - Suggests neighborhoods within budget and simple quality signals  
mcp_kit           - Shared MCP adapter, tools, and clients used by agents  
  mcp_kit/servers/finance   - Budget/finance helper server  
  mcp_kit/servers/location  - Location and transit helper server  
  mcp_kit/servers/supabase  - Property data helper (via Supabase)  
web_server        - FastAPI + Gradio interface  
gradio_app.py     - App entry that wires API and UI  
tests             - Basic tests for tools and flows  
utils             - Helpers (embeddings, token tracking, etc.)  

Commands
make start        - Start the application  
make stop         - Stop the application  
make logs         - Show container logs  
make test-planner - Run planner agent test  
make clean        - Clean up files  

API
POST /analyze - Analyze user financial profile  
GET  /docs    - API documentation  

License
MIT
