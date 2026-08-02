from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load variables from .env into the environment
load_dotenv()

# One shared LLM client, reused by every agent node
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)