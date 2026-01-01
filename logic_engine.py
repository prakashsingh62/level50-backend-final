import os
from datetime import datetime
# Directly importing from your handler to bypass 'sheet_reader' error
from google_sheets_handler import SheetsHandler 

def run_level50(spreadsheet_id, sheet_name="Production", debug=False):
    handler = SheetsHandler(spreadsheet_id)
    all_rows = handler.get_all_rows(sheet_name)
    
    today = datetime.now()
    actions_taken = 0
    
    if debug:
        print(f"Starting Level 80 Scan. Rows found: {len(all_rows)}")

    for index, row in enumerate(all_rows, start=2):
        try:
            # Date extract karo (format: 25/12/2025)
            rfq_date_str = row.get('Date', '')
            if not rfq_date_str: continue
            
            # YAHAN CHANGE KIYA HAI: DD/MM/YYYY format ke liye
            rfq_date = datetime.strptime(rfq_date_str, "%d/%m/%Y")
            diff = (today - rfq_date).days
            
            # Phase 17 Logic: 10 din se zyada aur Status 'Closed' nahi hai
            if diff >= 10 and row.get('Status') != 'Closed':
                if debug:
                    print(f"Row {index} is OVERDUE ({diff} days). RFQ Date: {rfq_date_str}")
                
                # Yahan tera AI mailing function call hoga
                # Example: handler.update_cell(index, "Status", "AI Overdue Follow-up")
                actions_taken += 1
                
        except Exception as e:
            if debug: print(f"Error in Row {index} with date {rfq_date_str}: {e}")
            continue

    return {"status": "Complete", "actions_taken": actions_taken}
