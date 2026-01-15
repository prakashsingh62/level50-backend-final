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
            except gspread.WorksheetNotFound:
                logger.info(f"Creating new worksheet: {self.worksheet_name}")
                self.worksheet = self.spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=20)
                self._initialize_headers()
            
            logger.info("=" * 60)
            logger.info("CONNECTION SUCCESSFUL")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise
    
    def _initialize_headers(self):
        # UPDATED HEADERS - Match your Google Sheet
        headers = [
            'RFQ ID', 
            'CUSTOMER NAME', 
            'PRODUCT', 
            'QTY',
            'CONCERN PERSON 1',
            'REMARKS 1',
            'CONCERN PERSON 2', 
            'REMARKS 2',
            'STATUS',
            'TIMESTAMP'
        ]
        self.worksheet.update('A1:J1', [headers])  # 10 columns
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
            
            # UPDATED ROW DATA - Match your sheet structure
            row_data = [
                rfq_data.get('rfq_id', ''),
                rfq_data.get('customer_name', ''),
                json.dumps(rfq_data.get('product_details', {})),  # Goes to PRODUCT column
                rfq_data.get('quantity', ''),
                rfq_data.get('concern_person_1', ''),  # New field
                rfq_data.get('remarks_1', ''),        # New field
                rfq_data.get('concern_person_2', ''),  # New field
                rfq_data.get('remarks_2', ''),        # New field
                rfq_data.get('status', 'submitted'),
                timestamp
            ]
            
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            row_number = len(self.worksheet.get_all_values())
            
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
                if record.get('RFQ ID') == rfq_id:
                    product_details = record.get('PRODUCT', '{}')
                    try:
                        product_details = json.loads(product_details)
                    except:
                        pass
                    
                    return {
                        'rfq_id': record.get('RFQ ID'),
                        'customer_name': record.get('CUSTOMER NAME'),
                        'product_details': product_details,
                        'quantity': record.get('QTY'),
                        'concern_person_1': record.get('CONCERN PERSON 1'),
                        'remarks_1': record.get('REMARKS 1'),
                        'concern_person_2': record.get('CONCERN PERSON 2'),
                        'remarks_2': record.get('REMARKS 2'),
                        'status': record.get('STATUS'),
                        'timestamp': record.get('TIMESTAMP')
                    }
            
            logger.warning(f"RFQ not found: {rfq_id}")
            return None
            
        except Exception as e:
            logger.error(f"Read failed: {str(e)}")
            raise
    
    def update_rfq(self, rfq_id, update_data):
        try:
            cell = self.worksheet.find(rfq_id)
            
            if not cell:
                return {"success": False, "error": f"RFQ {rfq_id} not found"}
            
            row = cell.row
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # UPDATED COLUMN MAP - Match your sheet
            column_map = {
                'status': 9,           # STATUS column (I)
                'concern_person_1': 5, # CONCERN PERSON 1 (E)
                'remarks_1': 6,        # REMARKS 1 (F)
                'concern_person_2': 7, # CONCERN PERSON 2 (G)
                'remarks_2': 8         # REMARKS 2 (H)
            }
            
            updates = []
            
            for field, value in update_data.items():
                if field in column_map:
                    col = column_map[field]
                    updates.append({'range': f'{chr(64 + col)}{row}', 'values': [[value]]})
            
            # Always update timestamp
            updates.append({'range': f'J{row}', 'values': [[timestamp]]})
            
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
                records = [r for r in records if r.get('STATUS') == status_filter]
            
            records = records[offset:offset + limit]
            
            formatted_records = []
            for record in records:
                product_details = record.get('PRODUCT', '{}')
                try:
                    product_details = json.loads(product_details)
                except:
                    pass
                
                formatted_records.append({
                    'rfq_id': record.get('RFQ ID'),
                    'customer_name': record.get('CUSTOMER NAME'),
                    'product_details': product_details,
                    'quantity': record.get('QTY'),
                    'concern_person_1': record.get('CONCERN PERSON 1'),
                    'remarks_1': record.get('REMARKS 1'),
                    'concern_person_2': record.get('CONCERN PERSON 2'),
                    'remarks_2': record.get('REMARKS 2'),
                    'status': record.get('STATUS'),
                    'timestamp': record.get('TIMESTAMP')
                })
            
            return formatted_records
            
        except Exception as e:
            logger.error(f"List failed: {str(e)}")
            raise
