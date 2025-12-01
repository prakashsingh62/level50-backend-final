
import base64, os, json
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import MODE, TEST_RECIPIENTS, PROD_RECIPIENTS

SCOPES=["https://www.googleapis.com/auth/gmail.send"]

def get_service():
    token_json=os.getenv("TOKEN_JSON")
    creds_data=json.loads(token_json)
    creds=Credentials.from_authorized_user_info(creds_data,SCOPES)
    return build("gmail","v1",credentials=creds)

def send_email(subject, body):
    service=get_service()

    recipients = TEST_RECIPIENTS if MODE=="TEST" else PROD_RECIPIENTS

    for to in recipients:
        msg=MIMEText(body)
        msg["to"]=to
        msg["subject"]=subject
        raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw":raw}).execute()
