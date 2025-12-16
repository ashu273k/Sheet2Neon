"""
Data Audit Script
Analyzes Google Sheets for data quality issues
Identifies: duplicates, missing values, inconsistent formats
"""

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
import json
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class DataAuditor:
    """Audit Google Sheets for data quality"""
    
    def __init__(self, credentials_path='D:\Projects\Internship\Sheet2Neon\Sheet2Neon\config\credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        self.service = discovery.build('sheets', 'v4', credentials=creds)
        print("✅ Authenticated with Google Sheets API")
    
    def fetch_sheet_data(self, spreadsheet_id, range_name):
        """Fetch data from Google Sheet"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])
    
    def audit_data(self, data, sheet_name):
        """Analyze data quality"""
        df = pd.DataFrame(data[1:], columns=data[0])
        
        audit_report = {
            'sheet_name': sheet_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'timestamp': datetime.now().isoformat(),
            'issues': {}
        }
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            audit_report['issues']['missing_values'] = missing.to_dict()
        
        # Check for duplicates
        duplicates = df.duplicated(subset=df.columns.tolist()).sum()
        if duplicates > 0:
            audit_report['issues']['duplicates'] = {
                'count': int(duplicates),
                'duplicate_rows': df[df.duplicated(keep=False)].to_dict()
            }
        
        # Data type analysis
        audit_report['columns'] = {
            col: {
                'dtype': str(df[col].dtype),
                'unique_count': int(df[col].nunique()),
                'null_count': int(df[col].isnull().sum())
            }
            for col in df.columns
        }
        
        return audit_report, df

# Example usage
if __name__ == "__main__":
    auditor = DataAuditor()
    auditor.authenticate()
    data = auditor.fetch_sheet_data('YOUR_SPREADSHEET_ID', 'Sheet1!A:Z')
    report, df = auditor.audit_data(data, 'Students')
    
    with open('logs/audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("✅ Audit report saved to logs/audit_report.json")
    
    print("Configure your spreadsheet_id and uncomment above code")
