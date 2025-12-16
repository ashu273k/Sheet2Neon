from src.etl.etl_pipeline import ETLPipeline
import os

def run():
    print("Starting ETL Process...")
    pipeline = ETLPipeline()
    
    # Check if files exist
    students_file = 'data/raw/students.csv'
    courses_file = 'data/raw/courses.csv'
    
    if os.path.exists(students_file):
        print(f"Processing {students_file}...")
        pipeline.run_etl(students_file, entity_type='students')
    else:
        print(f"Warning: {students_file} not found.")

    if os.path.exists(courses_file):
        print(f"Processing {courses_file}...")
        pipeline.run_etl(courses_file, entity_type='courses')
    else:
        print(f"Warning: {courses_file} not found.")

if __name__ == "__main__":
    run()
