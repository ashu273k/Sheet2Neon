# Real-World Integration Guide: Google Sheets to NeonDB

This guide explains how to switch from using static CSV files to live Google Sheets data for your ETL pipeline.

## 1. Google Cloud Platform (GCP) Setup
To access Google Sheets via Python, you need a Service Account.

1.  **Create a Project**: Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project (e.g., `Student-ETL`).
2.  **Enable APIs**:
    *   Search for **"Google Sheets API"** -> Enable.
    *   Search for **"Google Drive API"** -> Enable.
3.  **Create Service Account**:
    *   Go to **IAM & Admin** > **Service Accounts**.
    *   Click **Create Service Account**. Name it (e.g., `sheet-access`).
    *   Grant role: **Editor** (optional, but good for testing).
    *   Click **Done**.
4.  **Download Credentials**:
    *   Click on the newly created service account email.
    *   Go to **Keys** tab > **Add Key** > **Create new key** > **JSON**.
    *   Save this file as `credentials.json` in your project root folder (`d:/Projects/Internship/Sheet2Neon/Sheet2Neon/`).
    *   **IMPORTANT**: Add `credentials.json` to your `.gitignore` file immediately!

## 2. Prepare Your Google Sheet
1.  Create a new Google Sheet.
2.  **Share the Sheet**:
    *   Open `credentials.json` and find the `"client_email"` field.
    *   Copy that email address (looks like `sheet-access@project-id.iam.gserviceaccount.com`).
    *   In your Google Sheet, click **Share** and paste this email. Give it **Viewer** or **Editor** access.
3.  **Get Sheet ID**:
    *   Look at the URL: `https://docs.google.com/spreadsheets/d/1aBcD_..._XyZ/edit`
    *   The long string between `/d/` and `/edit` is your `SPREADSHEET_ID`.

## 3. Update Dependencies
Install the required Python libraries for Google API access:

```bash
pip install gspread oauth2client
```

Add these to your `requirements.txt`:
```text
gspread
oauth2client
```

## 4. Code Integration
Modify `src/etl/etl_pipeline.py` to implement the `extract_from_google_sheets` method.

### Step A: Add Imports
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
```

### Step B: Implement Extraction Logic
Replace the placeholder `extract_from_google_sheets` method with this code:

```python
    def extract_from_google_sheets(self, spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
        """Extract data directly from Google Sheets"""
        try:
            logger.info(f"Connecting to Google Sheet: {spreadsheet_id}")
            
            # Define scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Authenticate using credentials.json
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
            client = gspread.authorize(creds)
            
            # Open sheet
            sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
            
            # Get all records
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            self.log_data['records_extracted'] = len(df)
            logger.info(f"✅ Extracted {len(df)} rows from Sheet '{sheet_name}'")
            return df
            
        except Exception as e:
            logger.error(f"❌ Google Sheet extraction failed: {e}")
            self.log_data['errors'].append(str(e))
            return None
```

### Step C: Update Main Execution
In your `run_etl.py` or the `__main__` block of `etl_pipeline.py`, call this new method:

```python
# Configuration
SPREADSHEET_ID = 'your_spreadsheet_id_here'

# Run for Students
print("Fetching Students from Google Cloud...")
df_students = pipeline.extract_from_google_sheets(SPREADSHEET_ID, 'Students')
if df_students is not None:
    df_transformed = pipeline.transform_students(df_students)
    pipeline.load_students(df_transformed)

# Run for Courses
print("Fetching Courses from Google Cloud...")
df_courses = pipeline.extract_from_google_sheets(SPREADSHEET_ID, 'Courses')
if df_courses is not None:
    df_transformed = pipeline.transform_courses(df_courses)
    pipeline.load_courses(df_transformed)
```

## 5. Security Best Practices
- **Never commit `credentials.json`** to GitHub.
- Rotate keys if you suspect a leak.
- Use environment variables for `SPREADSHEET_ID` instead of hardcoding.
