import os
import gspread
import json
import sys
from google.oauth2.service_account import Credentials
from datetime import datetime

# 🔒 RULE-0: In columns ko AI/Automation kabhi touch nahi karega
LOCKED_COLUMNS = ['SALES PERSON', 'CUSTOMER NAME', 'LOCATION', 'RFQ NO', 'RFQ DATE', 'PRODUCT', 'UID NO', 'UID DATE', 'DUE DATE', 'VENDOR', 'CONCERN PERSON']

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    print(f"🚀 CLEAN START | Trace: {trace_id} | BYPASSING GEMINI")
    sys.stdout.flush()
    
    try:
        # Auth Setup
        service_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(service_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # Open Sheet
        ws_prod = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
        headers = ws_prod.row_values(1)
        
        # 🛡️ Sirf un columns mein data dalna jo LOCKED nahi hain
        # Maan lo humein 'RFQ STATUS' (Column L) update karna hai
        target_col = "RFQ STATUS" 
        
        if target_col not in LOCKED_COLUMNS:
            # Test ke liye hum Row 2 par update karke dekhte hain
            col_idx = headers.index(target_col) + 1
            ws_prod.update_cell(2, col_idx, "BYPASS_SUCCESS")
            print(f"✅ Row 2, Column {target_col} updated successfully!")
        else:
            print(f"⚠️ Cannot update {target_col}, it is LOCKED!")
            
        sys.stdout.flush()
        
    except Exception as e:
        print(f"❌ LOGIC ERROR: {str(e)}")
        sys.stdout.flush()
