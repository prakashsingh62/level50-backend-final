import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"DEBUG: Task Started for Sheet ID: {spreadsheet_id}")
    sys.stdout.flush()
    
    try:
        # 1. Render ke Environment Variable se JSON uthao
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        if not info_json:
            print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON variable not found in Render Environment!")
            return

        # 2. JSON String ko Python Dictionary mein badlo
        info = json.loads(info_json)
        
        # 3. Credentials set karo
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        
        # 4. Gspread connect karo
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        # 5. Data read karo
        data = worksheet.get_all_records()
        print(f"SUCCESS: Connected to Google Sheets. Found {len(data)} rows.")
        sys.stdout.flush()

        today = datetime.now()
        overdue_count = 0

        for i, row in enumerate(data, start=2):
            rfq_date_str = row.get('Date')
            status = row.get('Status')
            
            if rfq_date_str and status != 'Closed':
                # Date format: 25/12/2025
                rfq_date = datetime.strptime(rfq_date_str, "%d/%m/%Y")
                diff = (today - rfq_date).days
                
                if diff >= 10:
                    print(f"ROW {i}: RFQ is {diff} days old. Sending alert...")
                    overdue_count += 1
        
        print(f"FINISH: Processed {len(data)} rows. Total Overdue: {overdue_count}")
        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
