import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()

def runs_updates():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()

        # Parse queries from file
        with open('src/sql/queries.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple split by semicolon (naive, but works for this structured file)
        queries = content.split(';')
        
        print(f"Found {len(queries)} queries/blocks to test.\n")
        
        for i, query in enumerate(queries):
            query = query.strip()
            if not query:
                continue
            
            # Extract comment/title if possible
            title = "Query"
            lines = query.split('\n')
            for line in lines:
                if line.strip().startswith('--'):
                    title = line.strip().replace('--', '').strip()
                    break
            
            print(f"--- Executing: {title} ---")
            try:
                start_time = time.time()
                cursor.execute(query)
                
                # If returns rows, fetch some
                if cursor.description:
                    rows = cursor.fetchall()
                    duration = (time.time() - start_time) * 1000
                    print(f"✅ Success ({len(rows)} rows) in {duration:.2f}ms")
                    if rows:
                        print("Sample Row:", rows[0])
                else:
                    print("✅ Success (No Result Set)")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                conn.rollback() # Reset transaction
            
            print("\n")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    runs_updates()
