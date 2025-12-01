import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_gmail_service():
    client_secret = json.loads(os.environ["CLIENT_SECRET_JSON"])
    token_data = json.loads(os.environ["TOKEN_JSON"])

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=client_secret["client_id"],
        client_secret=client_secret["client_secret"],
        scopes=[
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.compose"
        ],
    )

    # Google automatically refreshes the token when needed
    return build("gmail", "v1", credentials=creds)
