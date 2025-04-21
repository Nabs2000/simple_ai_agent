from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
import getpass
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to the specified recipient with the given subject and body.
    You must have EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, and EMAIL_SMTP_PORT set as environment variables.
    """
    sender_email = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
    smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", 587))

    if not all([sender_email, password, smtp_server, smtp_port]):
        return "Missing one or more required environment variables for email."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, msg.as_string())
        return f"Email sent to {recipient}."
    except Exception as e:
        return f"Failed to send email: {e}"

tools = [search, send_email]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("placeholder", "{messages}"),
    ]
)

agent = create_react_agent(model, tools, prompt=prompt)

query = input("Enter your query: ")

messages = agent.invoke({"messages": [("human", query)]})
print(messages["messages"][-1].content)
