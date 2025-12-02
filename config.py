import os

# Always use environment variables for Level-50
MODE = os.getenv("MODE", "PROD")

# Read sheet + tab from Railway variables
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID", "")
PROD_TAB = os.getenv("PROD_TAB", "")

# No test mode sheets inside code (test = prod when sheet id is test sheet)
TEST_SHEET_ID = PROD_SHEET_ID
TEST_TAB = PROD_TAB

# Email recipients
TEST_RECIPIENTS = ["sales@ventilengineering.com"]

# TEMPORARY: send only to sales while testing
PROD_RECIPIENTS = [
    "sales@ventilengineering.com"
]
