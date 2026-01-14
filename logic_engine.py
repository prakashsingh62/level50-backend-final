import os
import gspread
import json
import sys
import re
import base64
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials as GmailCredentials
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional, Tuple

# ------------------------------------------------------------
# CONFIGURATION (TUMHARE RULES_CONFIG.PY SE IMPORT KARO YA DIRECT)
# ------------------------------------------------------------
try:
    from rules_config import rules
except ImportError:
    # Fallback: tumhare rules_config.py ka content yahaan direct define kiya hai
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
        "followup_rules": {
            "high_value_limit": 500000,
            "default_followup_offset": 2,
            "query_offset": 1,
            "submitted_offset": 2,
            "revised_offer_offset": 1
        },
        "matching_rules": {
            "skip_concern_person": ["NP"],
            "rfq_column": 4,
            "uid_column": 7
        },
        "vendor_query_rules": {
            "keywords": ["discount", "clarification", "revise", "revision", "gad", "final price"],
            "gad_keywords": ["gad", "drawing", "outline", "dimension"],
            "price_keywords": ["final price", "best price", "lowest", "discount"],
            "needs_vendor_mail": True
        },
        "column_map": {
            "vendor_status": 33,
            "quotation_date": 19,
            "remarks": 34,
            "followup_date": 35
        }
    }

# Tumhare bataye hue LOCKED columns
LOCKED_COLUMNS = [
    'SALES PERSON', 'CUSTOMER NAME', 'LOCATION', 'RFQ NO',
    'RFQ DATE', 'PRODUCT', 'UID NO', 'UID DATE',
    'DUE DATE', 'VENDOR', 'CONCERN PERSON'
]

# Column mappings from rules_config.py
COLUMN_MAP = rules.get("column_map", {})
STATUS_RULES = rules.get("status_rules", {})
FOLLOWUP_RULES = rules.get("followup_rules", {})
VENDOR_QUERY_RULES = rules.get("vendor_query_rules", {})
MATCHING_RULES = rules.get("matching_rules", {})

# ------------------------------------------------------------
# GMAIL API FUNCTIONS - REAL INTEGRATION
# ------------------------------------------------------------
def get_vendor_email_content(rfq_no: str, customer_name: str = None, max_results: int = 5) -> Optional[Dict[str, str]]:
    """
    REAL GMAIL API INTEGRATION
    RFQ NO ke hisaab se vendor ka latest email fetch karta hai
    Returns: {'subject': '', 'body': '', 'from': '', 'date': ''} ya None
    """
    try:
        # Gmail API ke liye credentials
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Tumhare Google Service Account credentials
        auth_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not auth_json:
            print(f"❌ Gmail API: GOOGLE_SERVICE_ACCOUNT_JSON missing for RFQ {rfq_no}")
            return None
        
        auth_info = json.loads(auth_json)
        
        # Email jismein vendor emails aate hain
        TARGET_EMAIL = os.environ.get("VENDOR_EMAIL_ACCOUNT", "your-vendor-email@company.com")
        
        # Gmail API service build karo
        creds = GmailCredentials.from_service_account_info(
            auth_info,
            scopes=SCOPES,
            subject=TARGET_EMAIL
        )
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Email search queries - multiple attempts
        search_queries = []
        
        # 1. RFQ NO se search
        search_queries.append(f'subject:"{rfq_no}" OR body:"{rfq_no}"')
        
        # 2. Customer name se search (agar available hai)
        if customer_name and customer_name.strip():
            search_queries.append(f'subject:"{customer_name}" OR body:"{customer_name}"')
        
        # 3. Generic RFQ search
        search_queries.append(f'subject:"RFQ" OR subject:"quotation" OR subject:"quote"')
        
        # Try each query until we find emails
        messages = []
        successful_query = ""
        
        for query in search_queries:
            try:
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()
                
                temp_messages = results.get('messages', [])
                if temp_messages:
                    messages = temp_messages
                    successful_query = query
                    break
                    
            except Exception as query_error:
                print(f"⚠️ Query failed '{query}': {str(query_error)}")
                continue
        
        if not messages:
            print(f"📭 No emails found for RFQ {rfq_no} (tried {len(search_queries)} queries)")
            return None
        
        # Latest email fetch karo
        latest_email_id = messages[0]['id']
        msg = service.users().messages().get(
            userId='me',
            id=latest_email_id,
            format='full'
        ).execute()
        
        # Email data extract karo
        email_data = extract_email_data(msg)
        email_data['rfq_no'] = rfq_no
        email_data['query_used'] = successful_query
        
        print(f"📧 Found email for RFQ {rfq_no} | Subject: {email_data.get('subject', 'No Subject')[:50]}...")
        return email_data
        
    except Exception as e:
        print(f"❌ Gmail API Error for RFQ {rfq_no}: {str(e)}")
        return None

def extract_email_data(msg) -> Dict[str, str]:
    """Gmail API response se email data extract karta hai"""
    payload = msg.get('payload', {})
    headers = payload.get('headers', [])
    
    email_data = {
        'subject': '',
        'body': '',
        'from': '',
        'date': '',
        'message_id': msg.get('id', '')
    }
    
    # Headers se subject, from, date nikaalo
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name == 'subject':
            email_data['subject'] = value
        elif name == 'from':
            email_data['from'] = value
        elif name == 'date':
            email_data['date'] = value
    
    # Email body extract karo
    def get_body_from_parts(parts):
        for part in parts:
            mime_type = part.get('mimeType', '')
            body_data = part.get('body', {}).get('data', '')
            
            # Recursive call for nested parts
            if 'parts' in part:
                nested_body = get_body_from_parts(part['parts'])
                if nested_body:
                    return nested_body
            
            if mime_type == 'text/plain' and body_data:
                try:
                    return base64.urlsafe_b64decode(body_data).decode('utf-8')
                except:
                    return ""
            elif mime_type == 'text/html' and body_data:
                try:
                    return base64.urlsafe_b64decode(body_data).decode('utf-8')
                except:
                    return ""
        return ""
    
    if 'parts' in payload:
        body = get_body_from_parts(payload['parts'])
        if body:
            email_data['body'] = body
    elif 'body' in payload and 'data' in payload['body']:
        body_data = payload['body']['data']
        if body_data:
            try:
                email_data['body'] = base64.urlsafe_b64decode(body_data).decode('utf-8')
            except:
                email_data['body'] = ""
    
    # Clean body text
    if email_data['body']:
        # Remove HTML tags
        email_data['body'] = re.sub(r'<[^>]+>', ' ', email_data['body'])
        # Remove extra whitespace
        email_data['body'] = re.sub(r'\s+', ' ', email_data['body']).strip()
    
    return email_data

def send_vendor_email(vendor_email: str, subject: str, body: str) -> bool:
    """
    Vendor ko email bhejne ke liye REAL FUNCTION
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        auth_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not auth_json:
            print("❌ GOOGLE_SERVICE_ACCOUNT_JSON missing for sending email")
            return False
        
        auth_info = json.loads(auth_json)
        SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "your-email@company.com")
        
        creds = GmailCredentials.from_service_account_info(
            auth_info,
            scopes=SCOPES,
            subject=SENDER_EMAIL
        )
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Email message create karo
        message = MIMEText(body, 'plain', 'utf-8')
        message['to'] = vendor_email
        message['subject'] = subject
        message['from'] = SENDER_EMAIL
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Email send karo
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ Email sent to {vendor_email} | Subject: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Email send failed to {vendor_email}: {str(e)}")
        return False

# ------------------------------------------------------------
# HELPER FUNCTIONS FOR AUTOMATION LOGIC
# ------------------------------------------------------------
def detect_status_from_text(text: str) -> str:
    """Email text se status detect karta hai"""
    if not text:
        return STATUS_RULES.get("default", "submitted")
    
    text_lower = text.lower()
    for status, keywords in STATUS_RULES.get("keywords", {}).items():
        for keyword in keywords:
            if keyword in text_lower:
                return status
    
    return STATUS_RULES.get("default", "submitted")

def calculate_followup_date(current_status: str, rfq_value: float = 0) -> Optional[datetime]:
    """Status ke hisaab se follow-up date calculate karta hai"""
    if current_status == "query":
        offset = FOLLOWUP_RULES.get("query_offset", 1)
    elif current_status == "submitted":
        offset = FOLLOWUP_RULES.get("submitted_offset", 2)
    elif current_status == "revised":
        offset = FOLLOWUP_RULES.get("revised_offer_offset", 1)
    else:
        offset = FOLLOWUP_RULES.get("default_followup_offset", 2)
    
    # High value RFQ ke liye alag rule
    if rfq_value > FOLLOWUP_RULES.get("high_value_limit", 500000):
        offset = max(1, offset - 1)  # 1 day earlier for high value
    
    return datetime.now() + timedelta(days=offset)

def should_process_row(row_data: Dict[str, str], headers: List[str]) -> Tuple[bool, str]:
    """Check karta hai ki row ko process karna chahiye ya nahi"""
    # Agar concern person "NP" hai toh skip karo
    concern_person = row_data.get("CONCERN PERSON", "")
    if concern_person.strip().upper() in MATCHING_RULES.get("skip_concern_person", ["NP"]):
        return False, "CONCERN PERSON is NP"
    
    # Agar RFQ NO nahi hai (empty) toh skip karo
    rfq_no = row_data.get("RFQ NO", "").strip()
    if not rfq_no:
        return False, "RFQ NO is empty"
    
    # Check if RFQ NO format is valid (basic check)
    if not re.match(r'^[A-Za-z0-9\-_]+$', rfq_no):
        return False, f"Invalid RFQ NO format: {rfq_no}"
    
    return True, ""

def get_column_index(header_name: str, headers: List[str]) -> Optional[int]:
    """Header name se column index find karta hai (1-based index for Google Sheets)"""
    try:
        return headers.index(header_name) + 1
    except ValueError:
        return None

def update_sheet_cell(worksheet, row_idx: int, col_idx: int, value: Any, max_retries: int = 3) -> bool:
    """Safe cell update with retry logic"""
    for attempt in range(max_retries):
        try:
            worksheet.update_cell(row_idx, col_idx, value)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Failed to update cell ({row_idx}, {col_idx}) after {max_retries} attempts: {str(e)}")
                return False
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
    return False

# ------------------------------------------------------------
# MAIN ENGINE - LEVEL 80 AUTOMATION
# ------------------------------------------------------------
def run_level50(spreadsheet_id: str, sheet_name: str = "RFQ TEST SHEET", debug: bool = False) -> Dict[str, Any]:
    """
    LEVEL 80 AUTOMATION - MAIN ENGINE
    Tumhare diye hue saare rules apply karta hai.
    """
    trace_id = f"L80-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"\n{'='*60}")
    print(f"🚀 LEVEL 80 AUTOMATION STARTED | Trace: {trace_id}")
    print(f"📊 Processing Sheet: {sheet_name} | Debug: {debug}")
    print(f"{'='*60}")
    
    start_time = datetime.now()
    
    try:
        # 1. GOOGLE SHEETS AUTHENTICATION
        auth_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not auth_json:
            error_msg = "❌ ERROR: GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set"
            print(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "trace_id": trace_id,
                "timestamp": datetime.now().isoformat()
            }
        
        auth_info = json.loads(auth_json)
        creds = Credentials.from_service_account_info(
            auth_info, 
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets", 
                "https://www.googleapis.com/auth/drive"
            ]
        )
        gc = gspread.authorize(creds)
        
        # 2. OPEN WORKSHEET
        worksheet = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
        headers = worksheet.row_values(1)
        
        # Debug info
        if debug:
            print(f"📋 Headers found ({len(headers)}): {headers}")
            print(f"🔒 Locked columns: {LOCKED_COLUMNS}")
            print(f"🗺️ Column map from rules: {COLUMN_MAP}")
        
        # 3. GET ALL DATA
        all_data = worksheet.get_all_values()
        if len(all_data) <= 1:
            print("ℹ️ No data rows to process")
            return {
                "status": "success",
                "message": "No data to process",
                "trace_id": trace_id,
                "timestamp": datetime.now().isoformat()
            }
        
        total_rows = len(all_data) - 1
        print(f"📈 Found {total_rows} data rows to process")
        
        # 4. PROCESS EACH ROW
        updates_made = 0
        skipped_rows = 0
        errors = []
        
        for row_idx, row in enumerate(all_data[1:], start=2):  # Start from row 2
            row_position = f"Row {row_idx}"
            try:
                # Create dictionary of row data
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_dict[header] = row[i]
                    else:
                        row_dict[header] = ""
                
                # Check if we should process this row
                should_process, reason = should_process_row(row_dict, headers)
                if not should_process:
                    if debug:
                        print(f"⏭️ {row_position}: Skipping - {reason}")
                    skipped_rows += 1
                    continue
                
                rfq_no = row_dict.get("RFQ NO", "").strip()
                customer_name = row_dict.get("CUSTOMER NAME", "").strip()
                
                if debug:
                    print(f"\n🔍 {row_position}: Processing RFQ {rfq_no} | Customer: {customer_name}")
                
                # =====================================================
                # RULE 1: VENDOR EMAIL FETCH & STATUS DETECTION
                # =====================================================
                email_data = None
                if not debug:  # In production, fetch real emails
                    email_data = get_vendor_email_content(rfq_no, customer_name)
                else:
                    # Debug mode: Use dummy email data
                    email_data = {
                        'subject': f'Quotation for RFQ {rfq_no}',
                        'body': 'Attached quotation for your review. Please confirm.',
                        'from': 'vendor@example.com',
                        'date': datetime.now().isoformat()
                    }
                    print(f"  🧪 Debug: Using dummy email data")
                
                if email_data and email_data.get('body'):
                    # Detect status from email content
                    detected_status = detect_status_from_text(email_data['body'])
                    
                    # Update VENDOR STATUS column
                    if "vendor_status" in COLUMN_MAP:
                        status_col_idx = COLUMN_MAP["vendor_status"] + 1  # Convert 0-index to 1-index
                        if status_col_idx <= len(headers):
                            success = update_sheet_cell(worksheet, row_idx, status_col_idx, detected_status.upper())
                            if success:
                                print(f"  ✅ Updated VENDOR STATUS to: {detected_status.upper()}")
                    
                    # Update REMARKS column
                    if "remarks" in COLUMN_MAP:
                        remarks_col_idx = COLUMN_MAP["remarks"] + 1
                        if remarks_col_idx <= len(headers):
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                            new_remarks = f"Status: {detected_status} | Email: {current_time}"
                            
                            # Preserve existing remarks if any
                            existing_remarks = row_dict.get(headers[remarks_col_idx-1] if remarks_col_idx-1 < len(headers) else "", "")
                            if existing_remarks and existing_remarks.strip():
                                new_remarks = f"{existing_remarks} | {new_remarks}"
                            
                            success = update_sheet_cell(worksheet, row_idx, remarks_col_idx, new_remarks)
                            if success:
                                print(f"  ✅ Updated REMARKS")
                    
                    # =====================================================
                    # RULE 2: FOLLOW-UP DATE CALCULATION
                    # =====================================================
                    if "followup_date" in COLUMN_MAP:
                        # Get RFQ value if available
                        rfq_value = 0
                        value_columns = ["VALUE", "AMOUNT", "TOTAL", "PRICE"]
                        for col in value_columns:
                            if col in row_dict:
                                try:
                                    value_str = str(row_dict[col]).replace(",", "").replace("₹", "").replace("$", "").strip()
                                    if value_str:
                                        rfq_value = float(value_str)
                                        break
                                except ValueError:
                                    continue
                        
                        # Calculate follow-up date
                        followup_date = calculate_followup_date(detected_status, rfq_value)
                        if followup_date:
                            followup_col_idx = COLUMN_MAP["followup_date"] + 1
                            if followup_col_idx <= len(headers):
                                date_str = followup_date.strftime("%Y-%m-%d")
                                success = update_sheet_cell(worksheet, row_idx, followup_col_idx, date_str)
                                if success:
                                    print(f"  ✅ Updated FOLLOWUP DATE to: {date_str}")
                    
                    # =====================================================
                    # RULE 3: QUOTATION DATE UPDATE
                    # =====================================================
                    if "quotation_date" in COLUMN_MAP:
                        # If status is "submitted" or "won", update quotation date
                        if detected_status in ["submitted", "won"]:
                            quote_col_idx = COLUMN_MAP["quotation_date"] + 1
                            if quote_col_idx <= len(headers):
                                today_str = datetime.now().strftime("%Y-%m-%d")
                                success = update_sheet_cell(worksheet, row_idx, quote_col_idx, today_str)
                                if success:
                                    print(f"  ✅ Updated QUOTATION DATE to: {today_str}")
                    
                    # =====================================================
                    # RULE 4: VENDOR QUERY DETECTION
                    # =====================================================
                    if detected_status == "query":
                        # Check for specific query types
                        email_body_lower = email_data['body'].lower() if email_data.get('body') else ""
                        
                        is_gad_query = any(keyword in email_body_lower for keyword in VENDOR_QUERY_RULES.get("gad_keywords", []))
                        is_price_query = any(keyword in email_body_lower for keyword in VENDOR_QUERY_RULES.get("price_keywords", []))
                        
                        # Update remarks with query details
                        if (is_gad_query or is_price_query) and "remarks" in COLUMN_MAP:
                            remarks_col_idx = COLUMN_MAP["remarks"] + 1
                            if remarks_col_idx <= len(headers):
                                current_remarks_cell = worksheet.cell(row_idx, remarks_col_idx)
                                current_remarks = current_remarks_cell.value or ""
                                
                                query_details = []
                                if is_gad_query:
                                    query_details.append("GAD required")
                                if is_price_query:
                                    query_details.append("Price negotiation")
                                
                                if query_details:
                                    new_remarks = f"{current_remarks} | Query detected: {', '.join(query_details)}"
                                    success = update_sheet_cell(worksheet, row_idx, remarks_col_idx, new_remarks)
                                    if success:
                                        print(f"  ✅ Detected query type: {', '.join(query_details)}")
                    
                    # =====================================================
                    # RULE 5: AUTO-SEND EMAIL FOR QUERIES (Optional)
                    # =====================================================
                    if detected_status == "query" and VENDOR_QUERY_RULES.get("needs_vendor_mail", False):
                        vendor_email = row_dict.get("VENDOR", "").strip()
                        if vendor_email and "@" in vendor_email:
                            subject = f"Follow-up: {rfq_no} - {customer_name}"
                            body = f"""Dear Vendor,

Following up on our RFQ {rfq_no} for {customer_name}.

Please provide the requested information at your earliest convenience.

Regards,
RFQ Automation System
"""
                            # Uncomment to actually send emails
                            # send_vendor_email(vendor_email, subject, body)
                            print(f"  📧 Would send email to: {vendor_email}")
                
                updates_made += 1
                print(f"  ✓ Processing complete for RFQ {rfq_no}")
                
            except Exception as row_error:
                error_msg = f"❌ Error at {row_position}: {str(row_error)}"
                print(error_msg)
                errors.append({
                    "row": row_idx,
                    "rfq_no": row_dict.get("RFQ NO", "Unknown"),
                    "error": str(row_error)
                })
        
        # 5. FINAL SUMMARY
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print("📊 AUTOMATION COMPLETE - SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Total rows scanned: {total_rows}")
        print(f"✅ Rows processed: {updates_made}")
        print(f"⏭️ Rows skipped: {skipped_rows}")
        print(f"❌ Errors: {len(errors)}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"🆔 Trace ID: {trace_id}")
        
        if errors and debug:
            print(f"\n📝 Error details ({len(errors)} errors):")
            for err in errors[:5]:  # Show first 5 errors only
                print(f"  - Row {err['row']} (RFQ: {err['rfq_no']}): {err['error'][:100]}...")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")
        
        return {
            "status": "success",
            "message": f"Automation completed. Processed {updates_made}/{total_rows} rows.",
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_rows": total_rows,
                "processed": updates_made,
                "skipped": skipped_rows,
                "errors": len(errors),
                "duration_seconds": duration
            },
            "errors": errors[:10] if errors else []  # Return first 10 errors only
        }
        
    except Exception as e:
        error_msg = f"❌ CRITICAL ERROR in automation engine: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": error_msg,
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "error_details": str(e)
        }
    finally:
        sys.stdout.flush()

# ------------------------------------------------------------
# ADDITIONAL FUNCTIONS FOR SPECIFIC TASKS
# ------------------------------------------------------------
def update_single_rfq(spreadsheet_id: str, rfq_no: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Single RFQ ko manually update karne ke liye"""
    try:
        auth_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not auth_json:
            return {"status": "error", "message": "Google auth credentials not found"}
        
        auth_info = json.loads(auth_json)
        creds = Credentials.from_service_account_info(
            auth_info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        
        worksheet = gc.open_by_key(spreadsheet_id).worksheet("RFQ TEST SHEET")
        headers = worksheet.row_values(1)
        
        # Find row with matching RFQ NO
        all_data = worksheet.get_all_values()
        target_row = None
        
        for row_idx, row in enumerate(all_data[1:], start=2):
            if row[headers.index("RFQ NO")] == rfq_no:
                target_row = row_idx
                break
        
        if not target_row:
            return {"status": "error", "message": f"RFQ {rfq_no} not found"}
        
        # Apply updates
        for header, value in updates.items():
            if header in headers:
                col_idx = headers.index(header) + 1
                worksheet.update_cell(target_row, col_idx, value)
        
        return {
            "status": "success",
            "message": f"RFQ {rfq_no} updated successfully",
            "updates_applied": len(updates)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_pending_followups(spreadsheet_id: str) -> List[Dict[str, Any]]:
    """Pending follow-ups check karta hai"""
    try:
        auth_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not auth_json:
            return []
        
        auth_info = json.loads(auth_json)
        creds = Credentials.from_service_account_info(
            auth_info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        
        worksheet = gc.open_by_key(spreadsheet_id).worksheet("RFQ TEST SHEET")
        headers = worksheet.row_values(1)
        
        # Find followup_date column
        followup_col_name = None
        for header in headers:
            if "followup" in header.lower() or "follow-up" in header.lower():
                followup_col_name = header
                break
        
        if not followup_col_name:
            return []
        
        followup_col_idx = headers.index(followup_col_name)
        today = datetime.now().date()
        
        pending_followups = []
        all_data = worksheet.get_all_values()
        
        for row_idx, row in enumerate(all_data[1:], start=2):
            followup_date_str = row[followup_col_idx] if followup_col_idx < len(row) else ""
            if followup_date_str:
                try:
                    followup_date = datetime.strptime(followup_date_str, "%Y-%m-%d").date()
                    if followup_date <= today:
                        pending_followups.append({
                            "row": row_idx,
                            "rfq_no": row[headers.index("RFQ NO")] if "RFQ NO" in headers else "",
                            "customer": row[headers.index("CUSTOMER NAME")] if "CUSTOMER NAME" in headers else "",
                            "followup_date": followup_date_str,
                            "status": row[headers.index("VENDOR STATUS")] if "VENDOR STATUS" in headers else ""
                        })
                except ValueError:
                    continue
        
        return pending_followups
        
    except Exception as e:
        print(f"Error checking followups: {str(e)}")
        return []

# ------------------------------------------------------------
# EXECUTION EXAMPLE (TESTING KE LIYE)
# ------------------------------------------------------------
if __name__ == "__main__":
    # Test ke liye - environment variable set karna hoga
    # export GOOGLE_SERVICE_ACCOUNT_JSON='{...}'
    
    # Tumhara actual spreadsheet ID yahaan daalo
    TEST_SPREADSHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"  # Example from config.py
    
    print("🧪 Testing LEVEL 80 Automation Engine...")
    print("=" * 50)
    
    result = run_level50(
        spreadsheet_id=TEST_SPREADSHEET_ID,
        sheet_name="RFQ TEST SHEET",
        debug=True  # Set to False for production
    )
    
    print(f"\n🎯 Test Result: {result['status'].upper()}")
    print(f"📨 Message: {result['message']}")
    
    if result['status'] == 'success' and 'metrics' in result:
        metrics = result['metrics']
        print(f"📊 Metrics: {metrics['processed']}/{metrics['total_rows']} rows processed in {metrics['duration_seconds']:.1f}s")
