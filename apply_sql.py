import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def apply_sql():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("Applying Views and Procedures...")
        with open('src/sql/views_and_procedures.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
            cursor.execute(sql_content)
            
        conn.commit()
        print("✅ Views and Procedures applied successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to apply SQL: {e}")

if __name__ == "__main__":
    apply_sql()
