/*
=====================================
GOOGLE APPS SCRIPT - AUTO-REGISTRATION
=====================================

Triggered when new rows are added to Google Sheet
Validates data and auto-inserts into NeonDB

Requires:
- Google Sheet with columns: Name, Email, Year, Department
- Google Apps Script project with UrlFetchApp enabled
- NeonDB REST API endpoint or ETL webhook
*/

// ============================================
// CONFIGURATION
// ============================================

const SHEET_NAME = "Students";  // Name of your Google Sheet tab
const API_ENDPOINT = "https://your-api.com/register";  // Your API endpoint
const VALID_DEPARTMENTS = ["1", "2", "3", "4"];  // Valid department IDs
const VALID_YEARS = [1, 2, 3, 4];

// ============================================
// VALIDATION FUNCTIONS
// ============================================

/**
 * Validate email format
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate student row
 * Returns: {isValid: boolean, errors: []}
 */
function validateStudentRow(row) {
  const [name, email, year, deptId] = row;
  const errors = [];

  // Check name
  if (!name || name.trim() === "") {
    errors.push("Missing name");
  }

  // Check email
  if (!email || !isValidEmail(email)) {
    errors.push("Invalid email format");
  }

  // Check year
  const yearNum = parseInt(year);
  if (!VALID_YEARS.includes(yearNum)) {
    errors.push(`Invalid year: ${year} (must be 1-4)`);
  }

  // Check department
  if (!deptId || !VALID_DEPARTMENTS.includes(String(deptId))) {
    errors.push(`Invalid department: ${deptId}`);
  }

  return {
    isValid: errors.length === 0,
    errors: errors,
  };
}

// ============================================
// CORE FUNCTIONS
// ============================================

/**
 * Register student in NeonDB
 * Calls backend API
 */
function registerStudentInDB(studentData) {
  try {
    const payload = {
      name: studentData.name,
      email: studentData.email,
      year: studentData.year,
      department_id: studentData.departmentId,
    };

    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
    };

    const response = UrlFetchApp.fetch(API_ENDPOINT, options);
    const result = JSON.parse(response.getContentText());

    Logger.log(`API Response: ${response.getResponseCode()} - ${result}`);
    return result.success === true;
  } catch (error) {
    Logger.log(`API Error: ${error}`);
    return false;
  }
}

/**
 * Mark row with error/success status
 */
function markRowStatus(sheet, rowIndex, status, message) {
  const statusCell = sheet.getRange(rowIndex, 5);  // Column E for status
  statusCell.setValue(status);

  const messageCell = sheet.getRange(rowIndex, 6);  // Column F for message
  messageCell.setValue(message);

  // Add conditional formatting
  if (status === "❌ Error") {
    statusCell.setBackground("#ffcccc");  // Light red
  } else if (status === "✅ Registered") {
    statusCell.setBackground("#ccffcc");  // Light green
  }
}

/**
 * Process new student entries
 * Called by onEdit or onSubmit trigger
 */
function processNewStudents() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getSheetByName(SHEET_NAME);

  if (!sheet) {
    Logger.log(`❌ Sheet "${SHEET_NAME}" not found`);
    return;
  }

  const data = sheet.getDataRange().getValues();
  const headers = data[0];  // First row is headers

  // Find column indexes
  const nameCol = headers.indexOf("Name") + 1;
  const emailCol = headers.indexOf("Email") + 1;
  const yearCol = headers.indexOf("Year") + 1;
  const deptCol = headers.indexOf("Department") + 1;

  if (nameCol === 0 || emailCol === 0) {
    Logger.log("❌ Missing Name or Email columns");
    return;
  }

  // Process each row (skip header)
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const statusCell = sheet.getRange(i + 1, 5);  // Assuming status is in column E

    // Skip if already processed
    if (statusCell.getValue() !== "") {
      continue;
    }

    const studentData = {
      name: row[nameCol - 1],
      email: row[emailCol - 1],
      year: parseInt(row[yearCol - 1]),
      departmentId: parseInt(row[deptCol - 1]),
    };

    Logger.log(`Processing row ${i + 1}: ${studentData.name}`);

    // Validate
    const validation = validateStudentRow([
      studentData.name,
      studentData.email,
      studentData.year,
      studentData.departmentId,
    ]);

    if (!validation.isValid) {
      const errorMsg = validation.errors.join("; ");
      Logger.log(`❌ Validation failed: ${errorMsg}`);
      markRowStatus(sheet, i + 1, "❌ Error", errorMsg);
      continue;
    }

    // Register in DB
    const success = registerStudentInDB(studentData);

    if (success) {
      Logger.log(`✅ Registered: ${studentData.name}`);
      markRowStatus(
        sheet,
        i + 1,
        "✅ Registered",
        "Successfully registered in NeonDB"
      );
      // Send notification email
      sendNotificationEmail(studentData.email, "Registration Success");
    } else {
      Logger.log(`❌ Registration failed: ${studentData.name}`);
      markRowStatus(
        sheet,
        i + 1,
        "❌ Error",
        "Failed to register in database"
      );
      // Send error notification
      sendNotificationEmail(studentData.email, "Registration Error");
    }
  }

  Logger.log("✅ Batch processing completed");
}

/**
 * Send email notification
 */
function sendNotificationEmail(email, status) {
  try {
    if (status === "Registration Success") {
      GmailApp.sendEmail(
        email,
        "Registration Successful",
        "Your profile has been successfully registered in our system. Welcome!"
      );
    } else {
      GmailApp.sendEmail(
        email,
        "Registration Error",
        "There was an issue registering your profile. Please contact support."
      );
    }
  } catch (error) {
    Logger.log(`Email failed: ${error}`);
  }
}

// ============================================
// TRIGGERS
// ============================================

/**
 * Install trigger: Run processNewStudents() when sheet is edited
 * To set up: Click Triggers → Create new trigger
 * - Function: processNewStudents
 * - Event: onEdit
 */
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() === SHEET_NAME) {
    Logger.log("Sheet edited, processing new students...");
    processNewStudents();
  }
}

/**
 * Alternative: Manual test function
 */
function testAppScript() {
  Logger.log("Testing App Script...");
  processNewStudents();
  Logger.log("Test completed. Check logs above.");
}
