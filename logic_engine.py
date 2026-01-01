import os
from datetime import datetime
# Fix: Tere repo mein file ka naam 'gsheet_handler' hai
from gsheet_handler import GSheetHandler 

def run_level50(spreadsheet_id, sheet_name="Production", debug=False):
    # Tere gsheet_handler mein class ka naam 'GSheetHandler' hai
    handler = GSheetHandler(spreadsheet_id)
    all_rows = handler.get_all_rows(sheet_name)
    
    today = datetime.now()
    actions_taken = 0
    
    if debug:
        print(f"Starting Level 80 Scan. Rows found: {len(all_rows)}")

    for index, row in enumerate(all_rows, start=2):
        try:
            # Date format: 25/12/2025
            rfq_date_str = row.get('Date', '')
            if not rfq_date_str: continue
            
            rfq_date = datetime.strptime(rfq_date_str, "%d/%m/%Y")
            diff = (today - rfq_date).days
            
            # Phase 17 Logic: 10 din overdue
            if diff >= 10 and row.get('Status') != 'Closed':
                if debug:
                    print(f"Row {index} is OVERDUE ({diff} days).")
                actions_taken += 1
                
        except Exception as e:
            continue

    return {"status": "Complete", "actions_taken": actions_taken}
