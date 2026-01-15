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
        self.spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID', '1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo')
        self.worksheet_name = os.getenv('WORKSHEET_NAME', 'RFQ TEST SHEET')
        self._initialize_connection()
    
    def _get_credentials(self) -> Credentials:
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not set")
        
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict, scopes=self.SCOPES)
    
    def _initialize_connection(self):
        try:
            credentials = self._get_credentials()
            logger.info(f"Service Account: {credentials.service_account_email}")
            
            self.client = gspread.authorize(credentials)
            logger.info(f"Opening spreadsheet: {self.spreadsheet_id}")
            
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info(f"✓ Connected to: {self.spreadsheet.title}")
            
            try:
                self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
                logger.info(f"✓ Worksheet found: {self.worksheet_name}")
            except gspread.WorksheetNotFound:
                logger.info(f"Creating worksheet: {self.worksheet_name}")
                self.worksheet = self.spreadsheet.add_worksheet(title=self.worksheet_name, rows=1000, cols=20)
                self._initialize_headers()
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            raise
    
    def _initialize_headers(self):
        headers = ['RFQ ID', 'Customer Name', 'Product Details', 'Quantity', 'Status', 'Submission Timestamp', 'Last Updated', 'Notes']
        self.worksheet.update('A1:H1', [headers])
    
    def test_connection(self) -> bool:
        try:
            self.worksheet.cell(1, 1)
            return True
        except:
            return False
    
    def write_rfq(self, rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            row_data = [
                rfq_data.get('rfq_id', ''),
                rfq_data.get('customer_name', ''),
                json.dumps(rfq_data.get('product_details', {})),
                rfq_data.get('quantity', ''),
                rfq_data.get('status', 'submitted'),
                timestamp,
                timestamp,
                rfq_data.get('notes', '')
            ]
            
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            row_number = len(self.worksheet.get_all_values())
            
            logger.info(f"✓ RFQ written at row {row_number}")
            return {"success": True, "row_number": row_number, "sheet_id": self.spreadsheet_id, "timestamp": timestamp}
        except Exception as e:
            logger.error(f"Write failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def read_rfq(self, rfq_id: str) -> Optional[Dict[str, Any]]:
        try:
            records = self.worksheet.get_all_records()
            for record in records:
                if record.get('RFQ ID') == rfq_id:
                    product_details = record.get('Product Details', '{}')
                    try:
                        product_details = json.loads(product_details)
                    except:
                        pass
                    return {
                        'rfq_id': record.get('RFQ ID'),
                        'customer_name': record.get('Customer Name'),
                        'product_details': product_details,
                        'quantity': record.get('Quantity'),
                        'status': record.get('Status'),
                        'submission_timestamp': record.get('Submission Timestamp'),
                        'last_updated': record.get('Last Updated'),
                        'notes': record.get('Notes')
                    }
            return None
        except Exception as e:
            logger.error(f"Read failed: {str(e)}")
            raise
    
    def update_rfq(self, rfq_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cell = self.worksheet.find(rfq_id)
            if not cell:
                return {"success": False, "error": f"RFQ {rfq_id} not found"}
            
            row = cell.row
            timestamp = datetime.now(timezone.utc).isoformat()
            
            column_map = {'status': 5, 'last_updated': 7, 'notes': 8}
            updates = []
            
            for field, value in update_data.items():
                if field in column_map:
                    col = column_map[field]
                    updates.append({'range': f'{chr(64 + col)}{row}', 'values': [[value]]})
            
            if 'last_updated' not in update_data:
                updates.append({'range': f'G{row}', 'values': [[timestamp]]})
            
            if updates:
                self.worksheet.batch_update(updates, value_input_option='USER_ENTERED')
            
            return {"success": True, "timestamp": timestamp}
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_rfqs(self, limit: int = 100, offset: int = 0, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            records = self.worksheet.get_all_records()
            
            if status_filter:
                records = [r for r in records if r.get('Status') == status_filter]
            
            records = records[offset:offset + limit]
            
            formatted_records = []
            for record in records:
                product_details = record.get('Product Details', '{}')
                try:
                    product_details = json.loads(product_details)
                except:
                    pass
                
                formatted_records.append({
                    'rfq_id': record.get('RFQ ID'),
                    'customer_name': record.get('Customer Name'),
                    'product_details': product_details,
                    'quantity': record.get('Quantity'),
                    'status': record.get('Status'),
                    'submission_timestamp': record.get('Submission Timestamp'),
                    'last_updated': record.get('Last Updated')
                })
            
            return formatted_records
        except Exception as e:
            logger.error(f"List failed: {str(e)}")
            raise
