# Data Engineering Assignment - Final Documentation

## 📘 Task 1: Environment Setup
- **Database**: NeonDB (PostgreSQL) hosted in cloud.
- **Language Stack**: Python 3.9+ for ETL, Javascript (Google Apps Script) for Automation.
- **Repository**: Git initialized.
- **Dependencies**: `psycopg2`, `pandas`, `python-dotenv`.

## 📘 Task 2: Data Audit
- **Sources**: `students.csv` (Messy student data), `courses.csv` (Course catalog).
- **Findings**:
    - Duplicate student registrations (handled by `ON CONFLICT` and Python dedup).
    - Invalid emails (filtered by ETL).
    - Invalid numeric ranges (Years 5+, Credits 0) detected and logged.
    - [Full Audit Report](file:///C:/Users/ashu9/.gemini/antigravity/brain/c4507109-e820-429b-8a8f-44e764199f98/data_audit.md)

## 📘 Task 3: Database Design & ERD
- **Normalization**: Schema is in 3NF.
- **Entities**:
    - `Department` (1) ----< `Student` (M)
    - `Department` (1) ----< `Course` (M)
    - `Student` (M) >----< `Course` (N) via `Enrollment`
- **Tables**: `student`, `course`, `department`, `enrollment`.
- **Optimization**: Indexes on `email`, `code`, `department_id` for performance.

## 📘 Task 4: ETL Pipeline
- **Architecture**:
    1. **Extract**: Read CSVs from `data/raw/`.
    2. **Transform** (`src/etl/etl_pipeline.py`):
        - Clean names/emails (Title Case, Lowercase).
        - Validate business logic (Year 1-4, Credits 1-4).
        - Remove duplicates.
    3. **Load**: `INSERT` into NeonDB with `ON CONFLICT DO NOTHING`.
- **Logs**: stored in `logs/etl_pipeline.log`.

## 📘 Task 5: SQL Development
- Developed a suite of analytical queries (`src/sql/queries.sql`).
- **Key Reports**:
    - Students per Department.
    - Department Grading Performance (GPA Analysis).
    - Grade Distribution.
- **Views**: `v_student_summary` for quick student lookups.
- **Procedures**: `register_student_course` for safe transactions.

## 📘 Task 6: Automation
- **Google App Script**: `code.gs` designed to:
    - Validate rows in real-time (Red highlight for invalid data).
    - Export validated data to JSON for ETL consumption.

## 📘 Task 7: Optimizations
- **Indexing**: Added B-Tree indexes on foreign keys to speed up JOINs.
- **Performance**: `EXPLAIN ANALYZE` confirms Index Scans are used for finding students by email, reducing cost from O(N) to O(logN).

## 📘 Task 9: Challenges & Future Improvements
### Challenges Faced
- **Data Quality**: The source `students.csv` contained invalid years (e.g., '5') and mismatched column counts.
    - *Solution*: implemented strict row-level validation in `etl_pipeline.py` to log and skip bad rows without crashing the batch.
- **Idempotency**: Re-running the ETL pipeline caused duplicate primary key errors.
    - *Solution*: Used `INSERT ... ON CONFLICT DO NOTHING` to ensure the pipeline can be run multiple times safely.

### Future Improvements
- **Automated Webhook**: Deploy the Google Apps Script to trigger a backend API endpoint (AWS Lambda/Cloud Functions) instead of just validting locally.
- **Data Warehousing**: For larger datasets, implementing a separate OLAP schema (Star Schema) for the analytics queries would improve reporting performance.
- **CI/CD**: Add GitHub Actions to auto-run tests on every commit.
