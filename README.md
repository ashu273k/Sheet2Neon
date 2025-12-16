# Sheet2Neon

## Data Engineering Assignment: Google Sheets → NeonDB Migration

## 📋 Project Overview

This project migrates Google Sheets workflows to PostgreSQL/NeonDB with automated ETL, SQL optimization, and Google Apps Script automation.

---

## 🗂️ Project Structure

```text
sheet2neon/
├── src/
│ ├── etl/
│ │ └── etl_pipeline.py # Main ETL orchestrator
│ ├── sql/
│ │ ├── queries.sql # Analytics queries
│ │ └── views_and_procedures.sql # Views & stored procedures
│ └── schemas/
│ ├── student_enrollment_schema.sql
│ └── seed_data.sql
├── tests/
│ ├── test_etl.py # Unit tests
│ ├── test_api_integration.py # Integration tests
│ └── test_sql_performance.py # Performance tests
├── config/
│ ├── credentials.json # Google API credentials (GITIGNORED)
│ └── settings.py # Configuration
├── data/
│ ├── raw/ # Raw CSV data
│ └── processed/ # Transformed data
├── logs/
│ ├── etl_pipeline.log # ETL execution logs
│ └── etl_log.json # Structured ETL logs
├── docs/
│ ├── ER_DIAGRAM.png # Database design
│ ├── DATA_AUDIT_REPORT.md # Data quality analysis
│ └── API_DOCUMENTATION.md # API reference
├── google_app_scripts/
│ └── auto_registration.gs # Google Apps Script code
├── requirements.txt # Python dependencies
├── .env.example # Environment variables template
└── README.md # This file
```


---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL/NeonDB account
- Google Cloud Project with Sheets API enabled
- Git

### 1. Clone Repository

```bash
git clone https://github.com/ashu273k/Sheet2Neon
cd sheet2neon
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your NeonDB credentials
```

### 3. Initialize Database

```bash
# Create schema
psql -h <your-host> -U <your-user> -d neondb -f src/schemas/student_enrollment_schema.sql

# Load seed data
psql -h <your-host> -U <your-user> -d neondb -f src/schemas/seed_data.sql
```

### 4. Test Connection

```bash
python src/scripts/test_connection.py
# Expected output: ✅ Connected to PostgreSQL/NeonDB!
```

### 5. Run ETL Pipeline

```bash
python src/etl/etl_pipeline.py
# Manually uncomment and configure source file in main block
```

### 6. Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Database Schema

### Entities

| Table | Purpose | Relationships |
|-------|---------|---------------|
| `department` | Department info | 1:N to Student, 1:N to Course |
| `student` | Student info | N:M to Course (via Enrollment) |
| `course` | Course info | N:M to Student (via Enrollment) |
| `enrollment` | Course registrations | Links Student ↔ Course |

### ER Diagram

See `docs/ER_DIAGRAM.png`

---

## 🔄 ETL Pipeline

### Flow

```text
Google Sheets / CSV
↓
EXTRACT (Read raw data)
↓
TRANSFORM (Clean, validate, deduplicate)
↓
LOAD (Insert into PostgreSQL)
↓
NeonDB (Final destination)
```

### Running ETL

```python
from src.etl.etl_pipeline import ETLPipeline

pipeline = ETLPipeline()
pipeline.run_etl('data/raw/students.csv', entity_type='students')
```

### Logging

- Logs: `logs/etl_pipeline.log`
- Structured data: `logs/etl_log.json`

---

## 📈 SQL Queries & Optimization

### Common Queries

Run from `src/sql/queries.sql`:

```sql
-- Students per department
SELECT d.name, COUNT(s.student_id)
FROM department d
LEFT JOIN student s ON d.department_id = s.department_id
GROUP BY d.department_id, d.name;

-- Student GPA calculation
SELECT s.name, ROUND(AVG(grade_points), 2) AS gpa
FROM student s
LEFT JOIN enrollment e ON s.student_id = e.student_id
GROUP BY s.student_id, s.name;
```

### Views

- `v_student_summary` - Student overview with GPA
- `v_course_analytics` - Course enrollment metrics

### Stored Procedures

- `register_student_course()` - Enroll student in course
- `calculate_student_gpa()` - Compute student GPA

---

## 🤖 Google Apps Script Automation

### Setup

1. Create Google Apps Script project
2. Copy code from `google_app_scripts/auto_registration.gs`
3. Set triggers: `onEdit` trigger on Google Sheet
4. Configure API endpoint in script

### Workflow

```text
New row added to Google Sheet
↓
onEdit trigger fires
↓
Validate row data
↓
If valid: Register in NeonDB
If invalid: Highlight row + send email
↓
Mark status in Sheet
```

---

## ✅ Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_etl.py -v

# With coverage
pytest tests/ --cov=src
```

### Test Coverage

- ✅ Validation functions
- ✅ Transformation logic
- ✅ Database operations
- ✅ SQL queries
- ✅ API integration

---

## 📚 Documentation

- **Data Audit:** `docs/DATA_AUDIT_REPORT.md`
- **Database Design:** `docs/ER_DIAGRAM.png` + `docs/SCHEMA_DOCUMENTATION.md`
- **ETL Process:** `docs/ETL_PIPELINE.md`
- **API Guide:** `docs/API_DOCUMENTATION.md`

---

## 🔐 Security

- `.env` file added to `.gitignore` - Never commit credentials
- Google credentials in `config/` - Added to `.gitignore`
- Use environment variables for all sensitive data
- Validate all user inputs

---

## 📞 Troubleshooting

### Connection Issues

```text
Error: "Could not connect to PostgreSQL"
Solution: Check DATABASE_URL in .env file
```

### ETL Errors

```
Error: "Validation failed"
Solution: Check data format in CSV - review logs/etl_pipeline.log
```

### Google API Issues

```
Error: "Credentials not found"
Solution: Download credentials.json from Google Cloud Console
```

---

## 📝 Submission Checklist

Before submitting, verify:

- [ ] Database schema created and seeded
- [ ] ETL pipeline tested and working
- [ ] All SQL queries and views created
- [ ] Tests passing (pytest)
- [ ] Google Apps Script configured
- [ ] Documentation complete
- [ ] Code committed to GitHub
- [ ] No credentials in Git
- [ ] README updated with instructions

---

## 🎓 Learning Outcomes

You've learned:
- ✅ PostgreSQL database design (normalization, constraints, indexes)
- ✅ ETL pipeline development (extract, transform, load)
- ✅ Data validation & quality assurance
- ✅ SQL optimization & query performance
- ✅ Google APIs & Apps Script automation
- ✅ Testing & logging best practices
- ✅ DevOps basics (environment setup, version control)

---

## 📞 Support

For issues:

1. Check `logs/` folder for error messages
2. Review test output (`pytest -v`)
3. Check README troubleshooting section
4. Contact instructor with logs attached

---

## Data Audit Report

## Sheet Analysis: Students

| Issue | Count | Details |
|-------|-------|---------|
| Missing Email | 5 | Rows: 12, 25, 43, 67, 89 |
| Duplicates | 3 | Student IDs: 102, 105, 110 |
| Invalid Year | 2 | Values: "5", "invalid" |
| Inconsistent Format | 10 | Email domains mixed case |

## Entity-Attribute Mapping

| Entity | Attributes | Primary Key | Notes |
|--------|-----------|-------------|-------|
| Student | student_id, name, email, year, dept_id | student_id | Year: 1-4 |
| Department | dept_id, name, head | dept_id | Unique department name |
| Course | course_id, name, dept_id, credits | course_id | Credits: 1-4 |
| Enrollment | enrollment_id, student_id, course_id, grade | enrollment_id | N:M relationship |

## Data Quality Actions

- ✅ Remove duplicate rows
- ✅ Fill missing emails with "<unknown@example.com>"
- ✅ Normalize year values (1, 2, 3, 4)
- ✅ Standardize email formats
