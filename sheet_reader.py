from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from logger import logger


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")

credentials_json = os.getenv("CLIENT_SECRET_JSON")
creds = None

if credentials_json:
    try:
        creds = Credentials.from_service_account_info(
            eval(credentials_json), scopes=SCOPES
        )
    except Exception as e:
        logger.error(f"Failed to load credentials: {str(e)}")
        creds = None


def fetch_rows():
    """
    Reads all rows from the Google Sheet.
    Returns: list of rows (2D list)
    """
    try:
        if creds is None:
            raise Exception("No service account credentials loaded.")

        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        range_name = f"{TAB_NAME}!A:Z"
        result = sheet.values().get(
            spreadsheetId=SHEET_ID, range=range_name
        ).execute()

        rows = result.get("values", [])
        if not rows:
            logger.warning("Sheet is empty!")
            return []

        logger.info(f"Fetched {len(rows)} rows from sheet.")
        return rows

    except Exception as e:
        logger.error(f"Error in fetch_rows(): {str(e)}")
        return []
