from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.text import MIMEText
import base64
import os
from pydantic import BaseModel
from pydantic_core import CoreSchema, core_schema
from typing import List, Any, Callable
import logfire
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

# Initialize Logfire
logfire.configure()

class EmailMessage(BaseModel):
    to: str
    subject: str
    body: str

    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }

class GMailAgent:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
        logfire.info('GMailAgent initialized', scopes=SCOPES)

    def send_email(self, email_message: EmailMessage) -> dict:
        try:
            # Create MIME message from the email message data
            mime_message = MIMEText(email_message.body)
            mime_message['to'] = email_message.to
            mime_message['subject'] = email_message.subject
            raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
            message_body = {'raw': raw_message}
            sent_message = self.service.users().messages().send(userId='me', body=message_body).execute()
            
            logfire.info('Email sent successfully', 
                to=email_message.to,
                subject=email_message.subject,
                message_id=sent_message.get('id')
            )
            
            return sent_message
        except Exception as e:
            logfire.error('Failed to send email',
                to=email_message.to,
                subject=email_message.subject,
                error=str(e)
            )
            raise

    def list_emails(self, max_results: int = 10) -> List[dict]:
        try:
            response = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = response.get('messages', [])
            
            logfire.info('Listed emails',
                count=len(messages),
                max_results=max_results
            )
            
            return messages
        except Exception as e:
            logfire.error('Failed to list emails',
                max_results=max_results,
                error=str(e)
            )
            raise

    def read_email(self, message_id: str) -> dict:
        try:
            email = self.service.users().messages().get(userId='me', id=message_id).execute()
            
            logfire.info('Read email',
                message_id=message_id
            )
            
            return email
        except Exception as e:
            logfire.error('Failed to read email',
                message_id=message_id,
                error=str(e)
            )
            raise

    def search_emails(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Search emails using Gmail's search query syntax.
        Args:
            query: Search query using Gmail's search operators (e.g., 'from:example@email.com', 'subject:meeting')
            max_results: Maximum number of results to return
        Returns:
            List of message objects matching the search criteria
        """
        try:
            response = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            messages = response.get('messages', [])
            
            # Fetch full message details for each result
            detailed_messages = []
            for msg in messages:
                email = self.read_email(msg['id'])
                detailed_messages.append(email)
            
            logfire.info('Searched emails',
                query=query,
                max_results=max_results,
                found_count=len(detailed_messages)
            )
            
            return detailed_messages
        except Exception as e:
            logfire.error('Failed to search emails',
                query=query,
                max_results=max_results,
                error=str(e)
            )
            raise

def authenticate():
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logfire.info('Refreshed expired credentials')
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                logfire.info('Generated new credentials through OAuth flow')
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                logfire.info('Saved credentials to token.json')
        return creds
    except Exception as e:
        logfire.error('Authentication failed', error=str(e))
        raise

if __name__ == "__main__":
    creds = authenticate()
    agent = GMailAgent(creds)
    print("Listing the first 10 emails:")
    emails = agent.list_emails(10)
    print(emails) 