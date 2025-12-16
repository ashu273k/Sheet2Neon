"""
SQL Performance Testing & Optimization Verification
"""

import psycopg2
from psycopg2 import sql
import time
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

class SQLPerformanceTester:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor()
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def test_query_performance(self, query_name, sql_query):
        """Execute query and measure performance"""
        try:
            start_time = time.time()
            
            self.cursor.execute(sql_query)
            results = self.cursor.fetchall()
            
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # ms
            
            print(f"\n{'='*50}")
            print(f"Query: {query_name}")
            print(f"{'='*50}")
            print(f"Rows returned: {len(results)}")
            print(f"Execution time: {execution_time:.2f}ms")
            
            if results and len(results[0]) <= 3:
                for row in results[:5]:  # Show first 5 rows
                    print(f"  {row}")
                if len(results) > 5:
                    print(f"  ... ({len(results) - 5} more rows)")
            
            return execution_time
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return None
    
    def run_tests(self):
        """Run all performance tests"""
        self.connect()
        
        queries = {
            "Count students per department": """
                SELECT d.name, COUNT(s.student_id)
                FROM department d
                LEFT JOIN student s ON d.department_id = s.department_id
                GROUP BY d.department_id, d.name;
            """,
            
            "Student enrollments with details": """
                SELECT s.name, c.code, e.grade
                FROM student s
                LEFT JOIN enrollment e ON s.student_id = e.student_id
                LEFT JOIN course c ON e.course_id = c.course_id
                LIMIT 100;
            """,
            
            "Find duplicate emails": """
                SELECT email, COUNT(*)
                FROM student
                GROUP BY email
                HAVING COUNT(*) > 1;
            """,
            
            "Department performance": """
                SELECT d.name, COUNT(DISTINCT s.student_id), COUNT(DISTINCT c.course_id)
                FROM department d
                LEFT JOIN student s ON d.department_id = s.department_id
                LEFT JOIN course c ON d.department_id = c.department_id
                GROUP BY d.department_id, d.name;
            """
        }
        
        results = {}
        for query_name, query_sql in queries.items():
            results[query_name] = self.test_query_performance(query_name, query_sql)
        
        self.close()
        
        print(f"\n{'='*50}")
        print("SUMMARY")
        print(f"{'='*50}")
        for query_name, exec_time in results.items():
            if exec_time:
                print(f"{query_name}: {exec_time:.2f}ms")

if __name__ == "__main__":
    tester = SQLPerformanceTester()
    tester.run_tests()
