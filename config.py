
import os

MODE = os.getenv("MODE","TEST")

TEST_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TEST_TAB = "RFQ TEST SHEET"

PROD_SHEET_ID = os.getenv("PROD_SHEET_ID","")
PROD_TAB = "DOMESTIC REGISTER 2025-26"

TEST_RECIPIENTS = ["sales@ventilengineering.com"]

PROD_RECIPIENTS = [
    "sales@ventilengineering.com",
    "info@ventilengineering.com",
    "sales-support@ventilengineering.com",
    "core@ventilengineering.com",
    "insidesales.vepl@gmail.com",
    "sales-domestic@ventilengineering.com",
    "hiren@ventilengineering.com"
]
