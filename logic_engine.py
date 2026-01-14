import os
import gspread
import json
import sys
import re
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    """
    LEVEL 80 AUTOMATION - REAL VERSION
    Google Sheet se hi vendor email content fetch karta hai
    """
    print(f"🚀 Automation Started: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. GOOGLE SHEETS CONNECT
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(
            info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        
        # 2. OPEN SHEET
        ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
        headers = ws.row_values(1)
        all_data = ws.get_all_values()
        
        if len(all_data) <= 1:
            print("ℹ️ No data to process")
            return
        
        # 3. RULES_CONFIG.PY KE RULES
        rules = {
            "status_rules": {
                "keywords": {
                    "won": ["order confirmed", "po attached", "po released"],
                    "lost": ["not approved", "rejected", "lost", "not considered"],
                    "submitted": ["attached quotation", "sending offer", "quotation attached"],
                    "query": ["clarification", "discount", "revise", "revision", "gad", "final price"]
                },
                "default": "submitted"
            },
            "column_map": {
                "vendor_status": 33,      # Column AH (1-based: 34)
                "quotation_date": 19,     # Column T (1-based: 20)
                "remarks": 34,            # Column AI (1-based: 35)
                "followup_date": 35       # Column AJ (1-based: 36)
            }
        }
        
        # 4. HEADER POSITIONS FIND KARO
        header_positions = {}
        for idx, header in enumerate(headers):
            header_positions[header.strip().upper()] = idx
        
        # 5. VENDOR EMAIL COLUMN IDENTIFY KARO
        vendor_email_col = None
        possible_names = ["VENDOR EMAIL", "VENDOR_EMAIL", "EMAIL", "VENDOR MAIL", "VENDOR_MAIL"]
        for name in possible_names:
            if name in header_positions:
                vendor_email_col = header_positions[name]
                break
        
        # 6. VENDOR NOTES/RESPONSE COLUMN IDENTIFY KARO
        vendor_notes_col = None
        possible_notes = ["VENDOR NOTES", "VENDOR_NOTES", "RESPONSE", "COMMENTS", "REMARKS", "VENDOR RESPONSE"]
        for name in possible_notes:
            if name in header_positions:
                vendor_notes_col = header_positions[name]
                break
        
        print(f"📊 Found columns: VENDOR_EMAIL at {vendor_email_col}, VENDOR_NOTES at {vendor_notes_col}")
        
        # 7. PROCESS EACH ROW
        processed_count = 0
        for row_idx, row in enumerate(all_data[1:], start=2):
            try:
                # RFQ NO check karo (Column D - index 3)
                rfq_no = row[3] if len(row) > 3 else ""
                if not rfq_no or not rfq_no.strip():
                    if debug:
                        print(f"⏭️ Row {row_idx}: Skipped (No RFQ NO)")
                    continue
                
                # 8. REAL VENDOR EMAIL CONTENT FETCH KARO
                vendor_email_content = ""
                
                # Pehle: Vendor notes column check karo
                if vendor_notes_col is not None and vendor_notes_col < len(row):
                    vendor_notes = row[vendor_notes_col]
                    if vendor_notes and vendor_notes.strip():
                        vendor_email_content = vendor_notes
                        source = "VENDOR_NOTES column"
                
                # Agar notes nahi hai, toh vendor email column check karo
                if not vendor_email_content and vendor_email_col is not None and vendor_email_col < len(row):
                    vendor_email = row[vendor_email_col]
                    if vendor_email and vendor_email.strip():
                        vendor_email_content = f"Vendor email: {vendor_email}"
                        source = "VENDOR_EMAIL column"
                
                # Agar kuch bhi nahi mila, toh remarks/description columns check karo
                if not vendor_email_content:
                    other_cols = ["DESCRIPTION", "PRODUCT DETAILS", "NOTES", "COMMENTS"]
                    for col_name in other_cols:
                        if col_name in header_positions:
                            col_idx = header_positions[col_name]
                            if col_idx < len(row) and row[col_idx] and row[col_idx].strip():
                                vendor_email_content = row[col_idx]
                                source = f"{col_name} column"
                                break
                
                # Agar abhi bhi kuch nahi mila
                if not vendor_email_content:
                    if debug:
                        print(f"ℹ️ Row {row_idx} ({rfq_no}): No vendor content found")
                    continue
                
                if debug:
                    print(f"📧 Row {row_idx} ({rfq_no}): Content from {source}")
                
                # 9. STATUS DETECT KARO (rules_config.py ke hisaab se)
                detected_status = rules["status_rules"]["default"]
                email_lower = vendor_email_content.lower()
                
                status_keywords = rules["status_rules"]["keywords"]
                for status, keywords in status_keywords.items():
                    for keyword in keywords:
                        if keyword in email_lower:
                            detected_status = status
                            break
                    if detected_status != rules["status_rules"]["default"]:
                        break
                
                # 10. AUTO COLUMNS UPDATE KARO
                col_map = rules["column_map"]
                updates_made = 0
                
                # VENDOR STATUS update (Column AH/34)
                if "vendor_status" in col_map:
                    status_col = col_map["vendor_status"] + 1  # 0-based to 1-based
                    if status_col <= len(headers):
                        current_value = ws.cell(row_idx, status_col).value
                        if not current_value or current_value.strip() == "":
                            ws.update_cell(row_idx, status_col, detected_status.upper())
                            updates_made += 1
                
                # QUOTATION DATE update (Column T/20)
                if "quotation_date" in col_map and detected_status in ["submitted", "won"]:
                    date_col = col_map["quotation_date"] + 1
                    if date_col <= len(headers):
                        current_value = ws.cell(row_idx, date_col).value
                        if not current_value or current_value.strip() == "":
                            ws.update_cell(row_idx, date_col, datetime.now().strftime("%Y-%m-%d"))
                            updates_made += 1
                
                # REMARKS update (Column AI/35)
                if "remarks" in col_map:
                    remarks_col = col_map["remarks"] + 1
                    if remarks_col <= len(headers):
                        current_remarks = ws.cell(row_idx, remarks_col).value or ""
                        new_remark = f"Auto: {detected_status} @ {datetime.now().strftime('%H:%M')}"
                        
                        if current_remarks:
                            updated_remarks = f"{current_remarks} | {new_remark}"
                        else:
                            updated_remarks = new_remark
                        
                        ws.update_cell(row_idx, remarks_col, updated_remarks)
                        updates_made += 1
                
                # FOLLOWUP DATE calculate (Column AJ/36)
                if "followup_date" in col_map:
                    followup_col = col_map["followup_date"] + 1
                    if followup_col <= len(headers):
                        current_value = ws.cell(row_idx, followup_col).value
                        if not current_value or current_value.strip() == "":
                            # Follow-up logic based on status
                            followup_days = 2  # Default
                            if detected_status == "query":
                                followup_days = 1
                            elif detected_status == "won":
                                followup_days = 0  # No follow-up needed
                            elif detected_status == "lost":
                                followup_days = 0  # No follow-up needed
                            
                            if followup_days > 0:
                                followup_date = datetime.now() + timedelta(days=followup_days)
                                ws.update_cell(row_idx, followup_col, followup_date.strftime("%Y-%m-%d"))
                                updates_made += 1
                
                if updates_made > 0:
                    print(f"✅ Row {row_idx} ({rfq_no}): {detected_status} [{updates_made} updates]")
                    processed_count += 1
                else:
                    if debug:
                        print(f"ℹ️ Row {row_idx} ({rfq_no}): No updates needed")
                
            except Exception as row_error:
                print(f"⚠️ Row {row_idx} error: {str(row_error)}")
                continue
        
        print(f"🎯 Automation Complete: {processed_count}/{len(all_data)-1} rows updated")
        
    except Exception as e:
        print(f"❌ System Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        sys.stdout.flush()
