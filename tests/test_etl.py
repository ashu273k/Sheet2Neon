"""
Unit tests for ETL Pipeline
Tests each component: validation, transformation, loading
"""

import pytest
import pandas as pd
from src.etl.etl_pipeline import ETLPipeline
from datetime import datetime
import os

@pytest.fixture
def pipeline():
    """Create pipeline instance for testing"""
    return ETLPipeline()

class TestValidation:
    """Test validation functions"""
    
    def test_validate_valid_student(self, pipeline):
        """Test validation of valid student"""
        student = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'year': 2,
            'department_id': 1
        }
        is_valid, errors = pipeline.validate_student_data(student)
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_missing_email(self, pipeline):
        """Test validation of student with missing email"""
        student = {
            'name': 'John Doe',
            'email': '',
            'year': 2,
            'department_id': 1
        }
        is_valid, errors = pipeline.validate_student_data(student)
        assert is_valid == False
        assert len(errors) > 0
    
    def test_validate_invalid_year(self, pipeline):
        """Test validation of student with invalid year"""
        student = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'year': 5,  # Invalid
            'department_id': 1
        }
        is_valid, errors = pipeline.validate_student_data(student)
        assert is_valid == False
    
    def test_validate_course_valid(self, pipeline):
        """Test validation of valid course"""
        course = {
            'code': 'CS101',
            'name': 'Intro to CS',
            'department_id': 1,
            'credits': 4
        }
        is_valid, errors = pipeline.validate_course_data(course)
        assert is_valid == True

class TestTransformation:
    """Test data transformation"""
    
    def test_transform_removes_duplicates(self, pipeline):
        """Test that duplicates are removed"""
        data = {
            'name': ['John Doe', 'Jane Doe', 'John Doe'],
            'email': ['john@test.com', 'jane@test.com', 'john@test.com'],
            'year': [1, 2, 1],
            'department_id': [1, 1, 1]
        }
        df = pd.DataFrame(data)
        
        df_transformed = pipeline.transform_students(df)
        
        assert len(df_transformed) == 2  # One duplicate removed
    
    def test_transform_normalizes_email(self, pipeline):
        """Test email normalization"""
        data = {
            'name': ['John Doe'],
            'email': ['JOHN@TEST.COM  '],  # Uppercase with spaces
            'year': [1],
            'department_id': [1]
        }
        df = pd.DataFrame(data)
        
        df_transformed = pipeline.transform_students(df)
        
        assert df_transformed.iloc[0]['email'] == 'john@test.com'

class TestETLIntegration:
    """Test full ETL pipeline"""
    
    @pytest.mark.skip(reason="Requires live database")
    def test_etl_full_pipeline(self):
        """Test complete ETL flow"""
        pipeline = ETLPipeline()
        
        # Create test CSV
        test_data = """name,email,year,department_id
        Test User,test@example.com,2,1"""
        
        with open('test_data.csv', 'w') as f:
            f.write(test_data)
        
        # Run ETL
        pipeline.run_etl('test_data.csv', 'students')
        
        # Verify
        assert pipeline.log_data['status'] == 'success'
        assert pipeline.log_data['records_loaded'] > 0
        
        # Cleanup
        os.remove('test_data.csv')

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, '-v'])
