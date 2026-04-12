import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_recent_emails(max_results=5, query=None):
    service = get_gmail_service()

    # Step 1: collect message IDs using pagination
    message_ids = []
    next_page_token = None

    while len(message_ids) < max_results:
        batch_size = min(max_results - len(message_ids), 500)

        kwargs = {
            "userId": "me",
            "maxResults": batch_size,
        }
        if query:
            kwargs["q"] = query
        else:
            kwargs["labelIds"] = ["INBOX"]
        if next_page_token:
            kwargs["pageToken"] = next_page_token

        result = service.users().messages().list(**kwargs).execute()

        message_ids.extend(result.get("messages", []))
        next_page_token = result.get("nextPageToken")

        if not next_page_token:
            break

    # Step 2: fetch full details for each message ID
    emails = []
    for message in message_ids:
        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        headers = msg["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "")

        if " -" in date:
            date = date.split(" -")[0]
        if " +" in date:
            date = date.split(" +")[0]

        body = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "sender": sender,
            "body": body[:500],
            "date": date
        })

    return emails
