"""
Integration tests for database API calls
Tests that ETL correctly inserts data
"""

import pytest
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def db_connection():
    """Create database connection for tests"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")

class TestDatabaseOperations:
    """Test database operations"""
    
    def test_connection(self, db_connection):
        """Test database connection"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
    
    def test_insert_student(self, db_connection):
        """Test inserting a student"""
        cursor = db_connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO student (name, email, year, department_id)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id;
            """, ('Test User', 'test_unique@example.com', 2, 1))
            
            student_id = cursor.fetchone()[0]
            db_connection.commit()
            
            assert student_id is not None
            
            # Cleanup
            cursor.execute("DELETE FROM student WHERE student_id = %s;", (student_id,))
            db_connection.commit()
        finally:
            cursor.close()
    
    def test_duplicate_email_rejected(self, db_connection):
        """Test that duplicate emails are rejected"""
        cursor = db_connection.cursor()
        try:
            # Insert first student
            cursor.execute("""
                INSERT INTO student (name, email, year, department_id)
                VALUES (%s, %s, %s, %s);
            """, ('User 1', 'duplicate@example.com', 1, 1))
            db_connection.commit()
            
            # Try to insert duplicate
            with pytest.raises(psycopg2.IntegrityError):
                cursor.execute("""
                    INSERT INTO student (name, email, year, department_id)
                    VALUES (%s, %s, %s, %s);
                """, ('User 2', 'duplicate@example.com', 2, 1))
                db_connection.commit()
            
            db_connection.rollback()
        finally:
            cursor.execute("DELETE FROM student WHERE email = 'duplicate@example.com';")
            db_connection.commit()
            cursor.close()

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
