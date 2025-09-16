import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv(".env")
os.environ["OPENAI_API_KEY"] = os.getenv(key="OPENAI_API_KEY")

# Force LangSmith tracing (in case not loaded from .env)
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "civic-assistant-team-5")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Make a simple call
response = llm.invoke("Hello, are you connected to LangSmith?")
print("LLM Response:", response)