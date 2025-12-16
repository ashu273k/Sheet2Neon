# Google App Script Setup Guide

This guide explains how to install the automation script into your Google Sheet to enable **Real-time Validation** and **Auto-Registration** features.

## 1. Open the Script Editor
1.  Open your Google Sheet (where you have the `Students` and `Courses` tabs).
2.  In the top menu, go to **Extensions** > **Apps Script**.
3.  A new tab will open with a code editor.

## 2. Install the Code
1.  You will see a file named `Code.gs` with a default `myFunction()`.
2.  **Delete everything** in that file.
3.  **Copy and Paste** the entire code from the block below:

```javascript
/**
 * Google Sheets Automation Script for NeonDB Migration
 */

// Configuration
const CONFIG = {
  // In a real deployment, this would be your Cloud Function URL
  API_ENDPOINT: 'https://api.your-backend.com/v1/sync', 
  ADMIN_EMAIL: 'admin@college.edu'
};

const COLS = {
  NAME: 0,
  EMAIL: 1,
  YEAR: 2,
  DEPT_ID: 3
};

/**
 * Triggered on every edit in the spreadsheet
 */
function onEdit(e) {
  if (!e || !e.range) return;
  
  const sheet = e.range.getSheet();
  const name = sheet.getName();
  
  // Only Validates 'Students' sheet
  if (name !== 'Students') return;

  const row = e.range.getRow();
  const col = e.range.getColumn();
  
  // Only process data rows (skip header)
  if (row <= 1) return;
  
  // Get the full row data
  const lastCol = sheet.getLastColumn();
  const range = sheet.getRange(row, 1, 1, lastCol);
  const values = range.getValues()[0];
  
  // Validate the row
  const validation = validateRow(values);
  
  if (!validation.isValid) {
    // ❌ INVALID: Highlight RED and show error
    range.setBackground('#FFCCCC'); // Light red
    sheet.getRange(row, lastCol + 1).setValue('Error: ' + validation.errors.join(', '));
  } else {
    // ✅ VALID: Highlight GREEN and clear error
    range.setBackground('#CCFFCC'); // Light green
    sheet.getRange(row, lastCol + 1).setValue('Valid - Ready for NeonDB');
    
    // Auto-registration Simulation
    // In a real app, we would call UrlFetchApp here
    console.log("Auto-registering student: " + values[0]);
  }
}

function validateRow(rowValues) {
  const errors = [];
  const name = rowValues[COLS.NAME];
  const email = rowValues[COLS.EMAIL];
  const year = rowValues[COLS.YEAR];
  const deptId = rowValues[COLS.DEPT_ID];
  
  if (!name || String(name).trim() === '') errors.push('Name req');
  
  // Simple Email Check
  if (!email || !String(email).includes('@')) errors.push('Invalid Email');
  
  // Year Check (1-4)
  if (![1, 2, 3, 4].includes(Number(year))) errors.push('Year 1-4 only');
  
  return { isValid: errors.length === 0, errors: errors };
}

/**
 * Menu item to manually sync/export
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('NeonDB Tools')
    .addItem('Validate All Rows', 'validateAll')
    .addItem('Export JSON for ETL', 'exportToJson')
    .addToUi();
}

function validateAll() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  
  for (let i = 1; i < rows.length; i++) { // Skip header
    const validation = validateRow(rows[i]);
    const range = sheet.getRange(i + 1, 1, 1, rows[i].length);
    
    if (!validation.isValid) {
      range.setBackground('#FFCCCC');
    } else {
      range.setBackground('#CCFFCC');
    }
  }
}

function exportToJson() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const rows = sheet.getDataRange().getValues();
  const headers = rows[0];
  const data = [];
  
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    const validation = validateRow(row); // Only export valid rows
    
    if (validation.isValid) {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header.toLowerCase()] = row[index];
      });
      data.push(obj);
    }
  }
  
  const jsonString = JSON.stringify(data, null, 2);
  const htmlOutput = HtmlService
    .createHtmlOutput('<textarea style="width:100%; height:300px;">' + jsonString + '</textarea>')
    .setWidth(600).setHeight(400);
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Ready for ETL Ingestion');
}
```

## 3. Save and Run
1.  Click the **Save** icon (floppy disk) on the toolbar. Name it `NeonDB Automation`.
2.  **IMPORTANT**: Reload your Google Sheet tab (F5).
3.  Wait a few seconds. You should see a new menu item called **"NeonDB Tools"** appear at the top.

## 4. How to Test (Demo)
### Test Auto-Validation
1.  Go to the `Students` tab.
2.  Add a new row with **INVALID** data:
    *   Name: `Bad User`
    *   Email: `bademail` (Missing @)
    *   Year: `5` (Invalid)
3.  **Result**: As soon as you press Enter, the row turns **RED**.

### Test Auto-Registration
1.  Correct the row:
    *   Name: `Good User`
    *   Email: `good@test.com`
    *   Year: `3`
2.  **Result**: The row turns **GREEN**.
3.  Show the "Valid - Ready for NeonDB" message in the last column.

### Test Export
1.  Click **NeonDB Tools** > **Export JSON for ETL**.
2.  Show the popup with the clean JSON data.
