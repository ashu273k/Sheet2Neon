"""
=====================================
ETL PIPELINE: Google Sheets → NeonDB
=====================================

Extract: Data from Google Sheets / CSV
Transform: Clean, validate, normalize
Load: Insert into PostgreSQL/NeonDB

Handles:
- Duplicate detection & removal
- Missing value handling
- Data type validation
- Logging & error handling
- Incremental updates
"""

import pandas as pd
import psycopg2
from psycopg2 import sql
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Set console encoding to UTF-8 for Windows compatibility
import sys
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================
# LOGGING SETUP
# ============================================
# Get the project root directory (two levels up from current file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'etl_pipeline.log')

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL orchestrator"""
    
    def __init__(self, db_url: str = None):
        """
        Initialize ETL pipeline
        
        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.conn = None
        self.cursor = None
        self.validation_errors = []
        self.log_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'records_extracted': 0,
            'records_transformed': 0,
            'records_loaded': 0,
            'errors': []
        }
    
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor()
            logger.info("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    # ============================================
    # EXTRACT PHASE
    # ============================================
    
    def extract_from_csv(self, file_path: str) -> pd.DataFrame:
        """Extract data from CSV file"""
        try:
            logger.info(f"Extracting from CSV: {file_path}")
            df = pd.read_csv(file_path)
            self.log_data['records_extracted'] = len(df)
            logger.info(f"✅ Extracted {len(df)} rows from CSV")
            return df
        except Exception as e:
            logger.error(f"❌ CSV extraction failed: {e}")
            self.log_data['errors'].append(str(e))
            return None
    
    def extract_from_google_sheets(self, spreadsheet_id: str, range_name: str):
        """Extract data from Google Sheets (requires API setup)"""
        # Implement using Google Sheets API
        # For now, using CSV as placeholder
        pass
    
    # ============================================
    # TRANSFORM PHASE
    # ============================================
    
    def validate_student_data(self, row: Dict) -> Tuple[bool, List[str]]:
        """
        Validate student row
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        if not row.get('name') or str(row['name']).strip() == '':
            errors.append("Missing name")
        
        if not row.get('email') or '@' not in str(row['email']):
            errors.append("Invalid email format")
        
        # Check year is 1-4
        try:
            year = int(row.get('year', 0))
            if year not in [1, 2, 3, 4]:
                errors.append(f"Invalid year: {year} (must be 1-4)")
        except ValueError:
            errors.append(f"Year is not a number: {row.get('year')}")
        
        # Check department exists
        if not row.get('department_id'):
            errors.append("Missing department_id")
        
        return len(errors) == 0, errors
    
    def validate_course_data(self, row: Dict) -> Tuple[bool, List[str]]:
        """Validate course row"""
        errors = []
        
        if not row.get('code') or str(row['code']).strip() == '':
            errors.append("Missing course code")
        
        if not row.get('name') or str(row['name']).strip() == '':
            errors.append("Missing course name")
        
        try:
            credits = int(row.get('credits', 0))
            if credits not in [1, 2, 3, 4]:
                errors.append(f"Invalid credits: {credits} (must be 1-4)")
        except ValueError:
            errors.append(f"Credits is not a number: {row.get('credits')}")
        
        return len(errors) == 0, errors
    
    def transform_students(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform student data:
        - Remove duplicates
        - Handle missing values
        - Normalize formats
        - Validate
        """
        logger.info("Transforming student data...")
        
        original_count = len(df)
        
        # Step 1: Remove complete duplicates
        df = df.drop_duplicates(subset=['email'], keep='first')
        duplicates_removed = original_count - len(df)
        if duplicates_removed > 0:
            logger.warning(f"⚠️  Removed {duplicates_removed} duplicate records")
        
        # Step 2: Handle missing values
        df['name'] = df['name'].fillna('Unknown')
        df['email'] = df['email'].fillna('unknown@example.com')
        df['year'] = df['year'].fillna(1)
        
        # Step 3: Normalize formats
        df['email'] = df['email'].str.lower().str.strip()
        df['name'] = df['name'].str.title().str.strip()
        df['year'] = df['year'].astype(int)
        
        # Step 4: Validate
        valid_rows = []
        for idx, row in df.iterrows():
            is_valid, errors = self.validate_student_data(row.to_dict())
            if is_valid:
                valid_rows.append(row)
            else:
                logger.warning(f"Row {idx} invalid: {', '.join(errors)}")
                self.log_data['errors'].extend(errors)
        
        df_valid = pd.DataFrame(valid_rows)
        self.log_data['records_transformed'] = len(df_valid)
        logger.info(f"✅ Transformed {len(df_valid)} valid student records")
        
        return df_valid
    
    def transform_courses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform course data"""
        logger.info("Transforming course data...")
        
        df = df.drop_duplicates(subset=['code'], keep='first')
        
        df['code'] = df['code'].str.upper().str.strip()
        df['name'] = df['name'].str.title().str.strip()
        df['credits'] = df['credits'].astype(int)
        
        valid_rows = []
        for idx, row in df.iterrows():
            is_valid, errors = self.validate_course_data(row.to_dict())
            if is_valid:
                valid_rows.append(row)
            else:
                logger.warning(f"Row {idx} invalid: {', '.join(errors)}")
        
        df_valid = pd.DataFrame(valid_rows)
        self.log_data['records_transformed'] = len(df_valid)
        logger.info(f"✅ Transformed {len(df_valid)} valid course records")
        
        return df_valid
    
    # ============================================
    # LOAD PHASE
    # ============================================
    
    def load_students(self, df: pd.DataFrame) -> int:
        """
        Load students into database
        Returns: Number of records inserted
        """
        logger.info(f"Loading {len(df)} students into database...")
        
        inserted = 0
        for idx, row in df.iterrows():
            try:
                self.cursor.execute(
                    """
                    INSERT INTO student (name, email, year, department_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                    """,
                    (row['name'], row['email'], row['year'], row['department_id'])
                )
                inserted += self.cursor.rowcount
            except Exception as e:
                logger.error(f"Row {idx} insert failed: {e}")
                self.log_data['errors'].append(str(e))
        
        self.conn.commit()
        self.log_data['records_loaded'] = inserted
        logger.info(f"✅ Loaded {inserted} students successfully")
        return inserted
    
    def load_courses(self, df: pd.DataFrame) -> int:
        """Load courses into database"""
        logger.info(f"Loading {len(df)} courses into database...")
        
        inserted = 0
        for idx, row in df.iterrows():
            try:
                self.cursor.execute(
                    """
                    INSERT INTO course (code, name, department_id, credits)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (code) DO NOTHING
                    """,
                    (row['code'], row['name'], row['department_id'], row['credits'])
                )
                inserted += self.cursor.rowcount
            except Exception as e:
                logger.error(f"Row {idx} insert failed: {e}")
                self.log_data['errors'].append(str(e))
        
        self.conn.commit()
        self.log_data['records_loaded'] = inserted
        logger.info(f"✅ Loaded {inserted} courses successfully")
        return inserted
    
    # ============================================
    # ORCHESTRATION
    # ============================================
    
    def run_etl(self, source_file: str, entity_type: str = 'students'):
        """
        Execute full ETL pipeline
        
        Args:
            source_file: Path to CSV file
            entity_type: 'students' or 'courses'
        """
        try:
            # Connect
            if not self.connect_db():
                raise Exception("Database connection failed")
            
            # Extract
            df_raw = self.extract_from_csv(source_file)
            if df_raw is None:
                raise Exception("Extraction failed")
            
            # Transform
            if entity_type == 'students':
                df_transformed = self.transform_students(df_raw)
            elif entity_type == 'courses':
                df_transformed = self.transform_courses(df_raw)
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Load
            if entity_type == 'students':
                self.load_students(df_transformed)
            elif entity_type == 'courses':
                self.load_courses(df_transformed)
            
            self.log_data['status'] = 'success'
            logger.info("✅ ETL Pipeline completed successfully")
            
        except Exception as e:
            self.log_data['status'] = 'failed'
            logger.error(f"❌ ETL Pipeline failed: {e}")
            
        finally:
            self.close_db()
            self.save_log()
    
    def save_log(self):
        """Save ETL log to file"""
        with open('logs/etl_log.json', 'w') as f:
            json.dump(self.log_data, f, indent=2)
        logger.info(f"Log saved to logs/etl_log.json")


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = ETLPipeline()
    
    # Run ETL for students
    pipeline.run_etl('data/raw/students.csv', entity_type='students')
    
    # Run ETL for courses
    pipeline.run_etl('data/raw/courses.csv', entity_type='courses')
    
    print("ETL Pipeline ready. Configure source files and run above commands.")
