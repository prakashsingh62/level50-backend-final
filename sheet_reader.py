from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from logger import get_logger
from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB

logger = get_logger()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load credentials safely from config (already parsed dict)
creds = Credentials.from_service_account_info(
    CLIENT_SECRET_JSON,
    scopes=SCOPES
)

def fetch_rows():
    """
    Reads all rows from the Google Sheet.
    Returns a 2D list of rows.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        range_name = f"{PROD_TAB}!A:Z"
        result = sheet.values().get(
            spreadsheetId=PROD_SHEET_ID, range=range_name
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
