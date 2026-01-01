import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"DEBUG: Background Task Started for {spreadsheet_id}") # Ye logs mein aana chahiye
    sys.stdout.flush() # Logs ko force update karne ke liye
    
    try:
        # Check if file exists
        if not os.path.exists("service_account.json"):
            print("ERROR: service_account.json NOT FOUND in root!")
            return

        gc = gspread.service_account(filename="service_account.json")
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        data = worksheet.get_all_records()
        print(f"SUCCESS: Found {len(data)} rows")
        sys.stdout.flush()

        # ... baki logic ...
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
