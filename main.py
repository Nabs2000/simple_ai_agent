import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain_openai import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for answering questions about current events."
    )
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

response = agent.run("Who is the current president of the United States?")
print(response)
