import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    try:
        # 1. Setup Google Credentials (Make sure RENDER_G_CREDS secret is set)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        # Hum Environment Variable use karenge security ke liye
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
        gc = gspread.service_account(filename=creds_path)
        
        # 2. Open the Sheet
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        print(f"--- Processing {len(data)} rows from {sheet_name} ---")
        
        today = datetime.now()
        overdue_count = 0

        for i, row in enumerate(data, start=2):
            # Date format 25/12/2025 check
            rfq_date_str = row.get('Date') # Apne column ka exact naam yahan likho
            status = row.get('Status')
            
            if rfq_date_str and status != 'Closed':
                rfq_date = datetime.strptime(rfq_date_str, "%d/%m/%Y")
                diff = (today - rfq_date).days
                
                if diff >= 10:
                    print(f"Row {i}: OVERDUE by {diff} days!")
                    overdue_count += 1
                    # Yahan update logic aayega
        
        return {"status": "Complete", "overdue_found": overdue_count}

    except Exception as e:
        print(f"Error in Logic Engine: {e}")
        return {"status": "Error", "message": str(e)}
