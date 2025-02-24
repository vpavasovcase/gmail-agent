import gradio as gr
from gmail_agentic import email_agent
import logfire
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Initialize Logfire
logfire.configure()

async def chat_with_agent(message, history):
    try:
        logfire.info('Processing chat message', message=message)
        # Run the agent and get response
        response = await email_agent.run(message)
        logfire.info('Chat response generated', response=response.data)
        return str(response.data)
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logfire.error('Chat error', message=message, error=str(e))
        return error_msg

# Create the Gradio interface
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="Gmail Agent Assistant",
    description="Chat with your Gmail assistant to send emails, search messages, and more.",
    examples=[
        "List my recent emails",
        "Search for emails from example@email.com",
        "Send an email to john@example.com with subject 'Hello' and body 'How are you?'"
    ],
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    logfire.info('Starting Gmail Agent UI')
    demo.launch(share=False) 