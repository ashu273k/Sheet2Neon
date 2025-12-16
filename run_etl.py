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
    # run()
    print("Starting ETL Process...")
    pipeline = ETLPipeline()
    # Configuration
    SPREADSHEET_ID = '1nGcvMwxvBfbb6K76ZSca5FinArcD_mLcg0wrOPbHE64'

    # Connect to DB
    if pipeline.connect_db():
        try:
            # Run for Students
            print("Fetching Students from Google Cloud...")
            df_students = pipeline.extract_from_google_sheets(SPREADSHEET_ID, 'Students')
            if df_students is not None:
                df_transformed = pipeline.transform_students(df_students)
                pipeline.load_students(df_transformed)

            # Run for Courses
            print("Fetching Courses from Google Cloud...")
            df_courses = pipeline.extract_from_google_sheets(SPREADSHEET_ID, 'Courses')
            if df_courses is not None:
                df_transformed = pipeline.transform_courses(df_courses)
                pipeline.load_courses(df_transformed)
        finally:
            pipeline.close_db()
    else:
        print("Failed to connect to database.")