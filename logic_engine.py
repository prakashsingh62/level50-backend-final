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
                    product_details = record.get('PRODUCT', '{}')
                    try:
                        product_details = json.loads(product_details)
                    except:
                        pass
                    
                    return {
                        'rfq_id': record.get('RFQ NO'),
                        'sales_person': record.get('SALES PERSON'),
                        'customer_name': record.get('CUSTOMER NAME'),
                        'location': record.get('LOCATION'),
                        'rfq_date': record.get('RFQ DATE'),
                        'product_details': product_details,
                        'uid_no': record.get('UID NO'),
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
            for record in records:
                product_details = record.get('PRODUCT', '{}')
                try:
                    product_details = json.loads(product_details)
                except:
                    pass
                
                formatted_records.append({
                    'sr_no': record.get('SR.NO'),
                    'rfq_id': record.get('RFQ NO'),
                    'sales_person': record.get('SALES PERSON'),
                    'customer_name': record.get('CUSTOMER NAME'),
                    'location': record.get('LOCATION'),
                    'rfq_date': record.get('RFQ DATE'),
                    'product_details': product_details,
                    'uid_no': record.get('UID NO'),  # ✅ FIX: UID NO ADDED HERE
                    'vendor': record.get('VENDOR'),
                    'concern_person_1': record.get('CONCERN PERSON 1'),
                    'concern_person_2': record.get('CONCERN PERSON 2'),
                    'current_status': record.get('CURRENT STATUS'),
                    'final_status': record.get('FINAL STATUS'),
                    'remarks_1': record.get('REMARKS 1'),
                    'remarks_2': record.get('REMARKS 2'),
                    'system_category': record.get('SYSTEM CATEGORY'),
                    'last_updated': record.get('SYSTEM NOTES', '').split('\n')[-1] if record.get('SYSTEM NOTES') else ''
                })
            
            return formatted_records
            
        except Exception as e:
            logger.error(f"List failed: {str(e)}")
            raise
