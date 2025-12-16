/*
=====================================
SEED DATA FOR TESTING
=====================================
Inserts sample data into the schema
*/

-- Insert Departments
INSERT INTO department (name, head) VALUES
    ('Computer Science', 'Dr. Rajesh Kumar'),
    ('Mechanical Engineering', 'Prof. Anjali Singh'),
    ('Civil Engineering', 'Prof. Vikram Patel'),
    ('Electrical Engineering', 'Dr. Meera Gupta')
ON CONFLICT (name) DO NOTHING;

-- Insert Students
INSERT INTO student (name, email, year, department_id) VALUES
    ('Aarav Sharma', 'aarav.sharma@college.edu', 2, 1),
    ('Priya Kapoor', 'priya.kapoor@college.edu', 2, 1),
    ('Rohan Verma', 'rohan.verma@college.edu', 3, 1),
    ('Nidhi Reddy', 'nidhi.reddy@college.edu', 1, 2),
    ('Sanjay Kumar', 'sanjay.kumar@college.edu', 4, 3),
    ('Divya Iyer', 'divya.iyer@college.edu', 2, 4)
ON CONFLICT (email) DO NOTHING;

-- Insert Courses
INSERT INTO course (code, name, department_id, credits) VALUES
    ('CS101', 'Introduction to Programming', 1, 4),
    ('CS201', 'Data Structures', 1, 4),
    ('CS301', 'Database Systems', 1, 3),
    ('CS401', 'Machine Learning', 1, 4),
    ('ME101', 'Mechanics', 2, 3),
    ('EE101', 'Circuit Theory', 4, 4)
ON CONFLICT (code) DO NOTHING;

-- Insert Enrollments
INSERT INTO enrollment (student_id, course_id, grade) VALUES
    (1, 1, 'A'),
    (1, 2, 'B'),
    (1, 3, 'A'),
    (2, 1, 'A'),
    (2, 2, 'A'),
    (3, 3, 'B'),
    (3, 4, 'C'),
    (4, 5, 'B'),
    (5, 6, 'A'),
    (6, 1, 'B')
ON CONFLICT (student_id, course_id) DO NOTHING;
