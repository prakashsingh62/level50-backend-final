import os
import json
import logging
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class LogicEngine:
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.spreadsheet_id = os.getenv('PROD_SHEET_ID', '1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo')
        self.worksheet_name = os.getenv('PROD_TAB', 'RFQ TEST SHEET')
        self._initialize_connection()
    
    def _get_credentials(self):
        creds_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') or os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
    
    def _initialize_connection(self):
        try:
            logger.info("=" * 60)
            logger.info("INITIALIZING GOOGLE SHEETS CONNECTION")
            logger.info("=" * 60)
            
            credentials = self._get_credentials()
            logger.info(f"Service Account: {credentials.service_account_email}")
            
            self.client = gspread.authorize(credentials)
            logger.info("Client authorized")
            
            logger.info(f"Opening spreadsheet ID: {self.spreadsheet_id}")
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info(f"Connected to spreadsheet: {self.spreadsheet.title}")
            
            try:
                self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
                logger.info(f"Worksheet found: {self.worksheet_name}")
                # Check headers
                current_headers = self.worksheet.row_values(1)
                logger.info(f"Current headers ({len(current_headers)} columns): {current_headers}")
            except gspread.WorksheetNotFound:
                logger.info(f"Creating new worksheet: {self.worksheet_name}")
                self.worksheet = self.spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=35)
                self._initialize_headers()
            
            logger.info("=" * 60)
            logger.info("CONNECTION SUCCESSFUL")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise
    
    def _initialize_headers(self):
        # MATCHING YOUR ACTUAL SHEET HEADERS
        headers = [
            'SR.NO', 'SALES PERSON', 'CUSTOMER NAME', 'LOCATION', 'RFQ NO', 'RFQ DATE',
            'PRODUCT', 'UID NO', 'UID DATE', 'DUE DATE', 'VENDOR', 'CONCERN PERSON 1',
            'INQUIRY SENT ON', 'VENDOR QUOTATION STATUS', 'VENDOR QUOTATION NO.', 
            'VENDOR QUOTATION DATE', 'CONCERN PERSON 2', 'VEPL OFFER NO.',
            'VEPL OFFER DATE', 'VEPL OFFER VALUE', 'CURRENT STATUS', 'FINAL STATUS',
            'POST OFFER QUERY', 'POST QUERY DATE', 'REMARKS 1', 'FOLLOWUP CONCERN PERSON',
            'FOLLOWUP DATE', 'FOLLOWUP EMAIL', 'FOLLOWUP CALL', 'REMARKS 2',
            'Vendor Follow-up Aging', 'Aging', 'SYSTEM CATEGORY', 'LAST EMAIL DATE',
            'SYSTEM NOTES'
        ]
        self.worksheet.update('A1:AI1', [headers])  # 35 columns (A to AI)
        logger.info("Headers initialized")
    
    def test_connection(self):
        try:
            self.worksheet.cell(1, 1)
            return True
        except:
            return False
    
    def write_rfq(self, rfq_data):
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            rfq_date = rfq_data.get('rfq_date', timestamp.split('T')[0])
            
            # MAP API DATA TO YOUR SHEET COLUMNS (35 columns total)
            row_data = [
                '',  # SR.NO (auto-increment) - Column A
                rfq_data.get('sales_person', ''),  # SALES PERSON - Column B
                rfq_data.get('customer_name', ''),  # CUSTOMER NAME - Column C
                rfq_data.get('location', ''),  # LOCATION - Column D
                rfq_data.get('rfq_id', ''),  # RFQ NO - Column E
                rfq_date,  # RFQ DATE - Column F
                json.dumps(rfq_data.get('product_details', {}), separators=(',', ':')),  # PRODUCT - Column G
                rfq_data.get('uid_no', ''),  # UID NO - Column H
                rfq_data.get('uid_date', ''),  # UID DATE - Column I
                rfq_data.get('due_date', ''),  # DUE DATE - Column J
                rfq_data.get('vendor', ''),  # VENDOR - Column K
                rfq_data.get('concern_person_1', ''),  # CONCERN PERSON 1 - Column L
                rfq_data.get('inquiry_sent_on', ''),  # INQUIRY SENT ON - Column M
                '',  # VENDOR QUOTATION STATUS - Column N
                '',  # VENDOR QUOTATION NO. - Column O
                '',  # VENDOR QUOTATION DATE - Column P
                rfq_data.get('concern_person_2', ''),  # CONCERN PERSON 2 - Column Q
                '',  # VEPL OFFER NO. - Column R
                '',  # VEPL OFFER DATE - Column S
                '',  # VEPL OFFER VALUE - Column T
                rfq_data.get('current_status', 'Submitted'),  # CURRENT STATUS - Column U (21st column)
                '',  # FINAL STATUS - Column V
                '',  # POST OFFER QUERY - Column W
                '',  # POST QUERY DATE - Column X
                rfq_data.get('remarks_1', ''),  # REMARKS 1 - Column Y
                rfq_data.get('followup_concern_person', ''),  # FOLLOWUP CONCERN PERSON - Column Z
                '',  # FOLLOWUP DATE - Column AA
                '',  # FOLLOWUP EMAIL - Column AB
                '',  # FOLLOWUP CALL - Column AC
                rfq_data.get('remarks_2', ''),  # REMARKS 2 - Column AD
                '',  # Vendor Follow-up Aging - Column AE
                '',  # Aging - Column AF
                rfq_data.get('system_category', 'API Generated'),  # SYSTEM CATEGORY - Column AG
                '',  # LAST EMAIL DATE - Column AH
                rfq_data.get('system_notes', 'Submitted via API')  # SYSTEM NOTES - Column AI
            ]
            
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            row_number = len(self.worksheet.get_all_values())
            
            # Update SR.NO automatically
            self.worksheet.update(f'A{row_number}', [[row_number - 1]])  # -1 because header row
            
            logger.info(f"RFQ {rfq_data.get('rfq_id')} written at row {row_number}")
            
            return {
                "success": True,
                "row_number": row_number,
                "sheet_id": self.spreadsheet_id,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Write failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def read_rfq(self, rfq_id):
        try:
            records = self.worksheet.get_all_records()
            
            for record in records:
                if record.get('RFQ NO') == rfq_id:
                    # Parse product details
                    product_str = str(record.get('PRODUCT', '{}')).strip()
                    product_details = {}
                    try:
                        if product_str.startswith('{') and product_str.endswith('}'):
                            product_details = json.loads(product_str)
                        else:
                            product_details = {'raw_product': product_str}
                    except:
                        product_details = {'raw_product': product_str}
                    
                    return {
                        'rfq_id': record.get('RFQ NO'),
                        'sales_person': record.get('SALES PERSON'),
                        'customer_name': record.get('CUSTOMER NAME'),
                        'location': record.get('LOCATION'),
                        'rfq_date': record.get('RFQ DATE'),
                        'product_details': product_details,
                        'uid_no': record.get('UID NO'),  # ✅ UID NO included
                        'uid_date': record.get('UID DATE'),
                        'due_date': record.get('DUE DATE'),
                        'vendor': record.get('VENDOR'),
                        'concern_person_1': record.get('CONCERN PERSON 1'),
                        'inquiry_sent_on': record.get('INQUIRY SENT ON'),
                        'concern_person_2': record.get('CONCERN PERSON 2'),
                        'current_status': record.get('CURRENT STATUS'),
                        'final_status': record.get('FINAL STATUS'),
                        'remarks_1': record.get('REMARKS 1'),
                        'followup_concern_person': record.get('FOLLOWUP CONCERN PERSON'),
                        'remarks_2': record.get('REMARKS 2'),
                        'system_category': record.get('SYSTEM CATEGORY'),
                        'system_notes': record.get('SYSTEM NOTES'),
                        'row_number': record.get('SR.NO')
                    }
            
            logger.warning(f"RFQ not found: {rfq_id}")
            return None
            
        except Exception as e:
            logger.error(f"Read failed: {str(e)}")
            raise
    
    def update_rfq(self, rfq_id, update_data):
        try:
            # Search in Column E (5th column) which is RFQ NO
            cell = self.worksheet.find(rfq_id, in_column=5)
            
            if not cell:
                return {"success": False, "error": f"RFQ {rfq_id} not found"}
            
            row = cell.row
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # CORRECT COLUMN MAPPING FOR YOUR SHEET
            column_map = {
                'current_status': 21,   # Column U = CURRENT STATUS (21st column)
                'final_status': 22,     # Column V = FINAL STATUS (22nd column)
                'vendor_quotation_status': 14,  # Column N = VENDOR QUOTATION STATUS
                'vendor_quotation_no': 15,      # Column O = VENDOR QUOTATION NO.
                'vendor_quotation_date': 16,    # Column P = VENDOR QUOTATION DATE
                'vepl_offer_no': 18,    # Column R = VEPL OFFER NO.
                'vepl_offer_date': 19,  # Column S = VEPL OFFER DATE
                'vepl_offer_value': 20, # Column T = VEPL OFFER VALUE
                'remarks_1': 25,        # Column Y = REMARKS 1 (25th column)
                'followup_date': 27,    # Column AA = FOLLOWUP DATE
                'remarks_2': 30,        # Column AD = REMARKS 2 (30th column)
                'last_email_date': 34,  # Column AH = LAST EMAIL DATE
                'system_notes': 35      # Column AI = SYSTEM NOTES (35th column)
            }
            
            updates = []
            
            for field, value in update_data.items():
                if field in column_map:
                    col = column_map[field]
                    updates.append({'range': f'{chr(64 + col)}{row}', 'values': [[value]]})
            
            # Update SYSTEM NOTES with timestamp
            current_notes = self.worksheet.cell(row, 35).value or ''
            new_note = f"{timestamp}: Status updated to {update_data.get('current_status', 'Updated')}"
            updated_notes = f"{current_notes}\n{new_note}" if current_notes else new_note
            updates.append({'range': f'AI{row}', 'values': [[updated_notes]]})
            
            if updates:
                self.worksheet.batch_update(updates, value_input_option='USER_ENTERED')
            
            logger.info(f"RFQ {rfq_id} updated")
            return {"success": True, "timestamp": timestamp}
            
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_rfqs(self, limit=100, offset=0, status_filter=None):
        try:
            records = self.worksheet.get_all_records()
            
            if status_filter:
                records = [r for r in records if str(r.get('CURRENT STATUS', '')).upper() == str(status_filter).upper()]
            
            records = records[offset:offset + limit]
            
            formatted_records = []
            for index, record in enumerate(records, 1):
                # 1. PRODUCT DETAILS को सही तरीके से हैंडल करें
                product_str = str(record.get('PRODUCT', '{}')).strip()
                product_details = {}
                
                try:
                    # JSON स्ट्रिंग है या नहीं चेक करें
                    if product_str.startswith('{') and product_str.endswith('}'):
                        product_details = json.loads(product_str)
                    else:
                        # JSON नहीं है, तो डिक्शनरी बनाएं
                        product_details = {
                            'raw_product': product_str,
                            'vendor': record.get('VENDOR', '')
                        }
                except json.JSONDecodeError as e:
                    # JSON parse error होने पर
                    logger.warning(f"JSON parse error for product: {product_str}")
                    product_details = {'raw_product': product_str}
                except Exception as e:
                    logger.error(f"Product parsing error: {e}")
                    product_details = {'error': str(e)}
                
                # 2. UID NO - FIRST PRIORITY: Google Sheets Column H
                uid_no = str(record.get('UID NO', '')).strip()
                
                # अगर UID NO खाली है, तो product_details से id चेक करें
                if not uid_no and isinstance(product_details, dict) and product_details.get('id'):
                    uid_no = str(product_details.get('id', '')).strip()
                
                # अगर फिर भी खाली है, तो auto-generate करें
                if not uid_no:
                    rfq_id = str(record.get('RFQ NO', '')).strip()
                    sr_no = str(record.get('SR.NO', index)).strip()
                    uid_no = f"{rfq_id}-{sr_no}" if rfq_id else f"AUTO-UID-{sr_no}"
                
                # 3. VENDOR information
                vendor_value = ''
                if isinstance(product_details, dict):
                    vendor_value = product_details.get('vendor') or product_details.get('VENDOR') or ''
                
                if not vendor_value:
                    vendor_value = str(record.get('VENDOR', '')).strip()
                
                # 4. FINAL रिकॉर्ड बनाएं
                formatted_records.append({
                    'sr_no': record.get('SR.NO') or index,
                    'rfq_id': record.get('RFQ NO', ''),
                    'sales_person': record.get('SALES PERSON', ''),
                    'customer_name': record.get('CUSTOMER NAME', ''),
                    'location': record.get('LOCATION', ''),
                    'rfq_date': record.get('RFQ DATE', ''),
                    'product_details': product_details,
                    'uid_no': uid_no,  # ✅ GUARANTEED - हमेशा भरेगा
                    'vendor': vendor_value,
                    'concern_person_1': record.get('CONCERN PERSON 1', ''),
                    'concern_person_2': record.get('CONCERN PERSON 2', ''),
                    'current_status': record.get('CURRENT STATUS', ''),
                    'final_status': record.get('FINAL STATUS', ''),
                    'remarks_1': record.get('REMARKS 1', ''),
                    'remarks_2': record.get('REMARKS 2', ''),
                    'system_category': record.get('SYSTEM CATEGORY', ''),
                    'last_updated': record.get('SYSTEM NOTES', '').split('\n')[-1] if record.get('SYSTEM NOTES') else ''
                })
            
            logger.info(f"✅ Returned {len(formatted_records)} records with UID NO")
            return formatted_records
            
        except Exception as e:
            logger.error(f"❌ List failed: {str(e)}", exc_info=True)
            raise

# ============================================================
# RFQ EXPERT AI SYSTEM - HUMAN-LIKE DECISION MAKING
# ADD THIS COMPLETE SECTION AT THE END OF logic_engine.py
# ============================================================

class RFQExpertSystem:
    """
    HUMAN EXPERT की तरह RFQ analyze करता है
    5 स्तरों पर सोचता है:
    1. Current stage पहचाने
    2. Missing information check करे
    3. Next logical action suggest करे
    4. Complete email draft generate करे
    5. Priority और timeline suggest करे
    """
    
    def analyze_rfq_context(self, rfq_data, email_context=None):
        """
        COMPLETE RFQ ANALYSIS with next action prediction
        
        Parameters:
        - rfq_data: Dictionary with RFQ information
        - email_context: Recent email thread (optional)
        
        Returns:
        {
            "rfq_number": "RFQ-2024-001",
            "current_stage": "INQUIRY",
            "next_action": "SEND_VENDOR_QUOTATION_REQUEST",
            "confidence": 85,
            "reasoning": ["No vendor quotes received yet"],
            "draft_email": "Dear Vendor...",
            "priority": "HIGH",
            "suggested_recipient": "vendor@company.com",
            "suggested_subject": "Quotation Request: RFQ-2024-001",
            "timeline": "URGENT: Send within 24 hours"
        }
        """
        try:
            # Get logger if exists, otherwise create simple logger
            try:
                logger
            except NameError:
                import logging
                logger = logging.getLogger(__name__)
            
            logger.info(f"🤖 AI Analyzing RFQ: {rfq_data.get('rfq_number', 'UNKNOWN')}")
            
            # 1. FIRST USE EXISTING LOGIC TO GET CURRENT STAGE
            # YOUR EXISTING FUNCTION - DON'T CHANGE
            current_stage = "INQUIRY"  # Default, your function will replace this
            if hasattr(self, 'determine_rfq_stage'):
                current_stage = self.determine_rfq_stage(rfq_data)
            elif 'current_stage' in rfq_data:
                current_stage = rfq_data.get('current_stage', 'INQUIRY')
            
            # 2. INITIALIZE ANALYSIS OBJECT
            analysis = {
                "rfq_number": rfq_data.get("rfq_number", "UNKNOWN"),
                "customer_name": rfq_data.get("customer_name", "Unknown"),
                "current_stage": current_stage,
                "next_action": None,
                "confidence": 0,
                "reasoning": [],
                "draft_email": None,
                "priority": "MEDIUM",
                "suggested_recipient": None,
                "suggested_subject": None,
                "timeline": "Standard: 3 days",
                "requires_human_approval": True,
                "ai_engine": "RFQExpertSystem_v1.0"
            }
            
            # ============================================
            # EXPERT RULE 1: NEED VENDOR QUOTATION
            # ============================================
            vendor_condition = (
                current_stage in ["INQUIRY", "INQUIRY_RECEIVED", "NEW"] and
                not rfq_data.get("vendor_quotes_received", False) and
                not rfq_data.get("vendor_quotation_sent", False) and
                rfq_data.get("valve_count", 0) > 0
            )
            
            if vendor_condition:
                analysis["next_action"] = "SEND_VENDOR_QUOTATION_REQUEST"
                analysis["confidence"] = 85
                analysis["reasoning"].append("New RFQ received, vendor quotation needed")
                analysis["priority"] = "HIGH"
                analysis["suggested_recipient"] = rfq_data.get("assigned_vendor_email") or "vendor@company.com"
                analysis["suggested_subject"] = f"Quotation Request: {rfq_data.get('rfq_number')}"
                analysis["draft_email"] = self._generate_vendor_quote_email(rfq_data)
                analysis["timeline"] = "URGENT: Send within 24 hours"
            
            # ============================================
            # EXPERT RULE 2: NEED GAD FOR COMPLEX VALVES
            # ============================================
            gad_condition = (
                rfq_data.get("valve_count", 0) > 3 or 
                rfq_data.get("complexity_score", 0) > 7 or
                rfq_data.get("requires_gad", False) or
                ("GAD" in str(rfq_data.get("technical_specs", "")).upper() or 
                 "DRAWING" in str(rfq_data.get("technical_specs", "")).upper())
            )
            
            if gad_condition and analysis["next_action"] is None:
                analysis["next_action"] = "REQUEST_GAD_FROM_VENDOR"
                analysis["confidence"] = 90
                analysis["reasoning"].append(f"Complex assembly: {rfq_data.get('valve_count', 0)} valves")
                if rfq_data.get("complexity_score", 0) > 7:
                    analysis["reasoning"].append(f"High complexity score: {rfq_data.get('complexity_score')}")
                analysis["priority"] = "HIGH"
                analysis["suggested_recipient"] = rfq_data.get("vendor_email") or rfq_data.get("assigned_vendor_email") or "technical@vendor.com"
                analysis["suggested_subject"] = f"GAD (General Arrangement Drawing) Request: {rfq_data.get('rfq_number')}"
                analysis["draft_email"] = self._generate_gad_request_email(rfq_data)
                analysis["timeline"] = "Priority: Required within 3 working days"
            
            # ============================================
            # EXPERT RULE 3: CLIENT FOLLOW-UP NEEDED
            # ============================================
            followup_condition = (
                current_stage in ["QUOTATION_SENT", "PROPOSAL_SENT", "WAITING_CLIENT"] and
                rfq_data.get("days_since_last_action", 0) > 3
            )
            
            if followup_condition and analysis["next_action"] is None:
                analysis["next_action"] = "FOLLOW_UP_WITH_CLIENT"
                analysis["confidence"] = 75
                analysis["reasoning"].append(f"No response for {rfq_data.get('days_since_last_action', 0)} days")
                analysis["priority"] = "MEDIUM"
                analysis["suggested_recipient"] = rfq_data.get("customer_email") or rfq_data.get("client_email")
                analysis["suggested_subject"] = f"Follow-up: RFQ {rfq_data.get('rfq_number')} - Quotation"
                analysis["draft_email"] = self._generate_followup_email(rfq_data)
                analysis["timeline"] = f"Follow up after {rfq_data.get('days_since_last_action', 0)} days silence"
            
            # ============================================
            # EXPERT RULE 4: SEND FINAL PRICE TO CLIENT
            # ============================================
            final_price_condition = (
                current_stage in ["PRICE_NEGOTIATION", "TECHNICAL_APPROVED", "FINALIZING"] and
                rfq_data.get("final_price_ready", False) and
                not rfq_data.get("final_price_sent", False) and
                rfq_data.get("client_awaiting_final_price", True)
            )
            
            if final_price_condition and analysis["next_action"] is None:
                analysis["next_action"] = "SEND_FINAL_PRICE_TO_CLIENT"
                analysis["confidence"] = 80
                analysis["reasoning"].append("Final price approved, ready to send to client")
                analysis["priority"] = "HIGH"
                analysis["suggested_recipient"] = rfq_data.get("customer_email") or rfq_data.get("decision_maker_email")
                analysis["suggested_subject"] = f"FINAL PRICE SUBMISSION: RFQ {rfq_data.get('rfq_number')}"
                analysis["draft_email"] = self._generate_final_price_email(rfq_data)
                analysis["timeline"] = "Send today to avoid delays"
            
            # ============================================
            # EXPERT RULE 5: TECHNICAL QUERY TO CLIENT
            # ============================================
            technical_query_condition = (
                current_stage in ["TECHNICAL_REVIEW", "SPECIFICATION_CLARIFICATION"] and
                rfq_data.get("technical_queries_pending", False) and
                not rfq_data.get("technical_query_sent", False)
            )
            
            if technical_query_condition and analysis["next_action"] is None:
                analysis["next_action"] = "SEND_TECHNICAL_QUERY_TO_CLIENT"
                analysis["confidence"] = 70
                analysis["reasoning"].append("Technical specifications need clarification")
                analysis["priority"] = "MEDIUM"
                analysis["suggested_recipient"] = rfq_data.get("customer_email") or rfq_data.get("technical_contact")
                analysis["suggested_subject"] = f"Technical Query: RFQ {rfq_data.get('rfq_number')}"
                analysis["draft_email"] = self._generate_technical_query_email(rfq_data)
                analysis["timeline"] = "Clarify before proceeding with vendor"
            
            # ============================================
            # FALLBACK: GENERAL FOLLOW-UP
            # ============================================
            if analysis["next_action"] is None:
                analysis["next_action"] = "GENERAL_FOLLOW_UP"
                analysis["confidence"] = 60
                analysis["reasoning"].append("Regular follow-up recommended to move RFQ forward")
                analysis["priority"] = "LOW"
                analysis["suggested_recipient"] = (
                    rfq_data.get("customer_email") or 
                    rfq_data.get("vendor_email") or 
                    "contact@company.com"
                )
                analysis["suggested_subject"] = f"Status Update Request: RFQ {rfq_data.get('rfq_number')}"
                analysis["draft_email"] = self._generate_general_followup(rfq_data)
                analysis["timeline"] = "Schedule for next week"
            
            logger.info(f"🤖 AI Analysis Complete: {analysis['rfq_number']} -> {analysis['next_action']}")
            return analysis
            
        except Exception as e:
            # Log error safely
            error_msg = f"AI Analysis error in RFQExpertSystem: {str(e)}"
            print(f"❌ ERROR: {error_msg}")
            
            # Return safe fallback analysis
            return {
                "rfq_number": rfq_data.get("rfq_number", "UNKNOWN"),
                "current_stage": "ERROR",
                "next_action": "MANUAL_REVIEW_REQUIRED",
                "confidence": 0,
                "reasoning": [f"Analysis error: {str(e)}"],
                "draft_email": None,
                "priority": "HIGH",
                "suggested_recipient": "manager@company.com",
                "suggested_subject": f"ERROR in RFQ {rfq_data.get('rfq_number', 'UNKNOWN')}",
                "timeline": "IMMEDIATE ATTENTION NEEDED",
                "requires_human_approval": True,
                "ai_engine": "RFQExpertSystem_v1.0_ERROR"
            }
    
    # ============================================
    # EMAIL TEMPLATE GENERATORS
    # ============================================
    
    def _generate_vendor_quote_email(self, rfq_data):
        """Generate vendor quotation request email"""
        customer_name = rfq_data.get('customer_name', 'Valued Customer')
        location = rfq_data.get('location', 'Site Location')
        required_date = rfq_data.get('required_date', 'ASAP')
        valve_count = rfq_data.get('valve_count', 'Multiple')
        
        return f"""Dear Vendor,

**QUOTATION REQUEST - {rfq_data.get('rfq_number', 'RFQ')}**

We request your competitive quotation for the following:

**CUSTOMER:** {customer_name}
**LOCATION:** {location}
**RFQ NUMBER:** {rfq_data.get('rfq_number', 'N/A')}
**REQUIRED DATE:** {required_date}
**VALVES REQUIRED:** {valve_count} valves

**TECHNICAL SPECIFICATIONS:**
{rfq_data.get('technical_specs', 'Please refer to attached technical data sheet')}

**ADDITIONAL NOTES:**
{rfq_data.get('special_requirements', 'Standard commercial terms apply')}

**SUBMISSION DEADLINE:** Please submit your quotation within 3 working days.

Please include:
1. Detailed pricing (ex-works, freight, taxes)
2. Delivery timeline
3. Validity period
4. Technical compliance statement

We look forward to your prompt response.

Best regards,

**Procurement Department**
[Your Company Name]
Phone: [Your Contact]
Email: [Your Email]

---
*This is an AI-generated draft. Please review before sending.*
"""
    
    def _generate_gad_request_email(self, rfq_data):
        """Generate GAD (General Arrangement Drawing) request email"""
        return f"""Dear Technical Team / Vendor,

**URGENT: GAD (GENERAL ARRANGEMENT DRAWING) REQUEST**
**RFQ:** {rfq_data.get('rfq_number', 'N/A')}

We require General Arrangement Drawings for the following valve assembly:

**PROJECT DETAILS:**
- Customer: {rfq_data.get('customer_name', 'Confidential')}
- Valve Count: {rfq_data.get('valve_count', 'Multiple')}
- Complexity Level: {'High' if rfq_data.get('complexity_score', 0) > 7 else 'Medium'}
- Application: {rfq_data.get('application', 'Process Industry')}

**GAD REQUIREMENTS:**
1. Complete assembly drawings with dimensions
2. Material specifications
3. Connection details (flanges, ratings)
4. Actuator mounting details (if applicable)
5. Bill of Materials (BOM)

**SUBMISSION REQUIREMENTS:**
- Format: PDF and DWG/AutoCAD
- Scale: As appropriate for clarity
- Deadline: Within 72 hours (3 working days)

**IMPORTANT:** GAD approval is required before proceeding with manufacturing.

Please acknowledge receipt and provide expected submission time.

Regards,

**Engineering & Technical Department**
[Your Company Name]

---
*This is an AI-generated draft. Please review technical details before sending.*
"""
    
    def _generate_followup_email(self, rfq_data):
        """Generate client follow-up email"""
        days_pending = rfq_data.get('days_since_last_action', 'several')
        quotation_date = rfq_data.get('quotation_date', 'previous week')
        
        return f"""Dear {rfq_data.get('customer_name', 'Valued Client')},

**FOLLOW-UP: RFQ {rfq_data.get('rfq_number', '')}**

Hope this email finds you well.

We wanted to follow up on our quotation submitted on {quotation_date} for the above RFQ.

**CURRENT STATUS:** Quotation submitted - awaiting your review/feedback

Could you please provide:
1. Any technical clarifications required?
2. Timeline for decision?
3. Next steps from your side?

We are ready to proceed immediately upon your approval and can discuss:
- Delivery schedule optimization
- Technical support
- Any modifications required

Looking forward to your response.

Warm regards,

**Sales Department**
[Your Company Name]
[Contact Person]
[Phone Number]

---
*This is an AI-generated draft. Please personalize before sending.*
"""
    
    def _generate_final_price_email(self, rfq_data):
        """Generate final price submission email"""
        return f"""Dear {rfq_data.get('customer_name', 'Decision Maker')},

**FINAL PRICE SUBMISSION & ORDER CONFIRMATION**
**RFQ:** {rfq_data.get('rfq_number', '')}

We are pleased to submit our final and best price for your approval:

**FINAL COMMERCIAL OFFER:**
- Total Price: {rfq_data.get('final_price', 'Please see attached quotation')}
- Price Validity: {rfq_data.get('price_validity', '30 days')}
- Delivery: {rfq_data.get('delivery_time', 'As agreed')}
- Payment Terms: {rfq_data.get('payment_terms', 'Standard terms')}

**KEY HIGHLIGHTS:**
✓ All technical requirements met
✓ Competitive pricing finalized
✓ Ready for immediate execution
✓ Quality certification included

**NEXT STEPS FOR ORDER:**
1. Your formal PO with this final price
2. We will acknowledge within 24 hours
3. Production will commence immediately

Please issue the Purchase Order to proceed.

Thank you for your business.

Sincerely,

**Sales & Commercial Department**
[Your Company Name]

---
*This is an AI-generated draft. Please verify price details before sending.*
"""
    
    def _generate_technical_query_email(self, rfq_data):
        """Generate technical clarification email"""
        return f"""Dear {rfq_data.get('technical_contact', 'Technical Team')},

**TECHNICAL QUERY: RFQ {rfq_data.get('rfq_number', '')}**

We are preparing the quotation and require clarification on the following:

**QUERY POINTS:**
1. {rfq_data.get('query_1', 'Operating pressure and temperature ranges')}
2. {rfq_data.get('query_2', 'Material specifications - exact grades required')}
3. {rfq_data.get('query_3', 'Actuator requirements - pneumatic/electric, fail-safe mode')}
4. {rfq_data.get('query_4', 'Connection standards and flange ratings')}

**ADDITIONAL INFORMATION REQUIRED:**
- Process fluid characteristics
- Installation environment details
- Any special testing/certification requirements

These clarifications will help us provide the most accurate technical solution and pricing.

Please respond at your earliest convenience.

Technical regards,

**Engineering & Proposal Department**
[Your Company Name]

---
*This is an AI-generated draft. Please verify technical queries before sending.*
"""
    
    def _generate_general_followup(self, rfq_data):
        """Generate general follow-up email"""
        return f"""Dear Sir/Madam,

**STATUS UPDATE REQUEST: RFQ {rfq_data.get('rfq_number', '')}**

Following up on the above RFQ to understand current status from your side.

**OUR RECORDS SHOW:**
- Current Stage: {rfq_data.get('current_stage', 'In Progress')}
- Last Update: {rfq_data.get('last_update_date', 'Recently')}
- Pending Actions: {rfq_data.get('pending_actions', 'Decision/Feedback')}

Could you please update us on:
1. Current status and timeline?
2. Any pending information required from us?
3. Next expected milestone?

We want to ensure we are aligned and can support your schedule.

Thank you for your cooperation.

Best regards,

**Project Coordination Team**
[Your Company Name]

---
*This is an AI-generated draft. Please review before sending.*
"""
    
    def get_expert_rules_summary(self):
        """Return summary of all expert rules for documentation"""
        return {
            "system": "RFQExpertSystem",
            "version": "1.0",
            "rules_count": 5,
            "rules": [
                {
                    "id": "RULE_001",
                    "name": "Vendor Quotation Request",
                    "condition": "New RFQ with no vendor quotes",
                    "action": "SEND_VENDOR_QUOTATION_REQUEST",
                    "priority": "HIGH"
                },
                {
                    "id": "RULE_002",
                    "name": "GAD Request",
                    "condition": "Complex valves (>3) or high complexity",
                    "action": "REQUEST_GAD_FROM_VENDOR",
                    "priority": "HIGH"
                },
                {
                    "id": "RULE_003",
                    "name": "Client Follow-up",
                    "condition": "No response for >3 days after quotation",
                    "action": "FOLLOW_UP_WITH_CLIENT",
                    "priority": "MEDIUM"
                },
                {
                    "id": "RULE_004",
                    "name": "Final Price Submission",
                    "condition": "Final price ready, not sent to client",
                    "action": "SEND_FINAL_PRICE_TO_CLIENT",
                    "priority": "HIGH"
                },
                {
                    "id": "RULE_005",
                    "name": "Technical Query",
                    "condition": "Technical clarifications pending",
                    "action": "SEND_TECHNICAL_QUERY_TO_CLIENT",
                    "priority": "MEDIUM"
                }
            ],
            "fallback": "GENERAL_FOLLOW_UP",
            "requires_human_approval": True
        }

# ============================================================
# END OF RFQExpertSystem CLASS
# ============================================================
