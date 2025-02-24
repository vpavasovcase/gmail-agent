from pydantic_ai import Agent, RunContext
import asyncio
from pydantic import BaseModel, Field
from agent import GMailAgent, authenticate, EmailMessage
from typing import Any, Dict
import logfire
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Logfire
logfire.configure()

class EmailResult(BaseModel):
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Details of the email operation")

    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }

# Create the PydanticAI agent instance
email_agent = Agent('google-gla:gemini-1.5-flash', system_prompt="You are an email assistant. Answer commands related to Gmail operations, such as reading and sending emails.")
logfire.info('Email agent initialized', model='google-gla:gemini-1.5-flash')

# Define an async tool to send an email
@email_agent.tool
async def send_email(ctx: RunContext, to: str, subject: str, body: str) -> EmailResult:
    try:
        logfire.info('Sending email', to=to, subject=subject)
        email_msg = EmailMessage(to=to, subject=subject, body=body)
        creds = authenticate()
        gmail_agent = GMailAgent(creds)
        result = gmail_agent.send_email(email_msg)
        logfire.info('Email sent via agent tool')
        return EmailResult(status="sent", message="Email sent successfully.", details=result)
    except Exception as e:
        logfire.error('Failed to send email via agent tool', error=str(e))
        raise

# Define an async tool to list emails
@email_agent.tool
async def list_emails(ctx: RunContext) -> EmailResult:
    try:
        logfire.info('Listing emails')
        creds = authenticate()
        gmail_agent = GMailAgent(creds)
        messages = gmail_agent.list_emails(10)
        logfire.info('Emails listed via agent tool', count=len(messages))
        return EmailResult(status="listed", message="Retrieved emails.", details={"messages": messages})
    except Exception as e:
        logfire.error('Failed to list emails via agent tool', error=str(e))
        raise

# Define an async tool to search emails
@email_agent.tool
async def search_emails(ctx: RunContext, query: str, max_results: int = 10) -> EmailResult:
    """
    Search emails using Gmail's search query syntax.
    Args:
        query: Search query (e.g., 'from:example@email.com', 'subject:meeting')
        max_results: Maximum number of results to return (default: 10)
    """
    try:
        logfire.info('Searching emails', query=query, max_results=max_results)
        creds = authenticate()
        gmail_agent = GMailAgent(creds)
        messages = gmail_agent.search_emails(query, max_results)
        logfire.info('Emails searched via agent tool', query=query, found_count=len(messages))
        return EmailResult(
            status="searched",
            message=f"Found {len(messages)} emails matching the search criteria.",
            details={"messages": messages}
        )
    except Exception as e:
        logfire.error('Failed to search emails via agent tool', query=query, error=str(e))
        raise

def main():
    try:
        logfire.info('Starting main function')
        query = "List my emails"
        response = email_agent.run_sync(query)
        logfire.info('Query executed', query=query, response=response.data)
        print(response.data)
    except Exception as e:
        logfire.error('Main function failed', error=str(e))
        raise

if __name__ == "__main__":
    main() 