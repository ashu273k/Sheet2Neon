import psycopg2
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

def init_db():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("Creating schemas...")
        with open('src/schemas/student_enrollment_schema.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
            cursor.execute(sql_content)
        
        print("Seeding data...")
        with open('src/schemas/seed_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
            cursor.execute(sql_content)
            
        conn.commit()
        print("✅ Database initialized successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_db()
