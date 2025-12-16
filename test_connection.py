"""
Test script to verify NeonDB connection
This confirms your environment is properly configured
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_connection():
    """Test PostgreSQL/NeonDB connection"""
    try:
        # Get connection details from environment
        connection_string = os.getenv('DATABASE_URL')
        
        if not connection_string:
            print("❌ DATABASE_URL not found in .env")
            return False
        
        # Connect to NeonDB
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Simple test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ Connected to PostgreSQL/NeonDB!")
        print(f"Version: {db_version[0]}")
        
        # Test table creation (optional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                message VARCHAR(100)
            );
        """)
        
        cursor.execute("INSERT INTO test_table (message) VALUES ('Connection successful');")
        conn.commit()
        
        cursor.execute("SELECT * FROM test_table;")
        result = cursor.fetchone()
        print(f"Test query result: {result}")
        
        cursor.execute("DROP TABLE test_table;")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
