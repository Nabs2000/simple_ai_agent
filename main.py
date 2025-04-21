from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

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
    You must have EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, and optionally EMAIL_SENDER_NAME set as environment variables.
    """
    sender_email = os.environ.get("EMAIL_ADDRESS")
    sender_name = os.environ.get("EMAIL_SENDER_NAME", "")
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
    smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", 587))

    if not all([sender_email, password, smtp_server, smtp_port]):
        return "Missing one or more required environment variables for email."

    if sender_name:
        from_header = f"{sender_name} <{sender_email}>"
    else:
        from_header = sender_email

    msg = MIMEMultipart()
    msg["From"] = from_header
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

tools = [send_email]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that can send emails. Your name is Nabeel Sabzwari."),
        ("placeholder", "{messages}"),
    ]
)

agent = create_react_agent(model, tools, prompt=prompt)

query = input("Enter your email query: ")

messages = agent.invoke({"messages": [("human", query)]})
print(messages["messages"][-1].content)
