from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API key:\n")

model = ChatOpenAI(model="gpt-4o")

@tool
def search(input: str) -> str:
    """
    Use this tool to search for information on the internet.
    """
    search = DuckDuckGoSearchRun()
    return search.run(input)

tools = [search]

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant."),
#     ("user", "{input}"),
#     ("placeholder", "{agent_scratchpad}"),
# ])

agent = create_react_agent(model, tools)

query = input("Enter your query: ")

messages = agent.invoke({"messages": [("human", query)]})
print(messages["messages"][-1].content)
