/*
=====================================
STUDENT ENROLLMENT SYSTEM - SCHEMA
=====================================
Normalized to 3NF
Entities: Department, Student, Course, Enrollment
Relationships: 1:N (Dept->Student, Dept->Course), N:M (Student<->Course)
*/

-- ============================================
-- 1. DEPARTMENT TABLE
-- ============================================
-- Stores department information
-- One department can have many students and courses
CREATE TABLE IF NOT EXISTS department (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- Unique department name
    head VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dept_name_not_empty CHECK (name != '')
);

-- Index for frequently searched departments
CREATE INDEX IF NOT EXISTS idx_dept_name ON department(name);

-- ============================================
-- 2. STUDENT TABLE
-- ============================================
-- Stores student information
-- Every student belongs to one department
CREATE TABLE IF NOT EXISTS student (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    year INT NOT NULL,  -- Academic year: 1, 2, 3, 4
    department_id INT NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to department
    CONSTRAINT fk_student_dept FOREIGN KEY (department_id) 
        REFERENCES department(department_id) ON DELETE RESTRICT,
    
    -- Data validation
    CONSTRAINT student_year_valid CHECK (year BETWEEN 1 AND 4),
    CONSTRAINT student_name_not_empty CHECK (name != ''),
    CONSTRAINT student_email_not_empty CHECK (email != '')
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_student_email ON student(email);
CREATE INDEX IF NOT EXISTS idx_student_department ON student(department_id);
CREATE INDEX IF NOT EXISTS idx_student_year ON student(year);

-- ============================================
-- 3. COURSE TABLE
-- ============================================
-- Stores course information
-- Every course belongs to one department
CREATE TABLE IF NOT EXISTS course (
    course_id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,  -- e.g., "CS101"
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    credits INT NOT NULL,  -- Credit hours: 1-4
    
    -- Foreign key to department
    CONSTRAINT fk_course_dept FOREIGN KEY (department_id) 
        REFERENCES department(department_id) ON DELETE RESTRICT,
    
    -- Data validation
    CONSTRAINT course_credits_valid CHECK (credits BETWEEN 1 AND 4),
    CONSTRAINT course_name_not_empty CHECK (name != '')
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_course_code ON course(code);
CREATE INDEX IF NOT EXISTS idx_course_department ON course(department_id);

-- ============================================
-- 4. ENROLLMENT TABLE
-- ============================================
-- Junction table for Student-Course N:M relationship
-- Links students to courses with their grades
CREATE TABLE IF NOT EXISTS enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    grade CHAR(2),  -- Grades: A, B, C, D, F
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    CONSTRAINT fk_enrollment_student FOREIGN KEY (student_id) 
        REFERENCES student(student_id) ON DELETE CASCADE,
    
    CONSTRAINT fk_enrollment_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) ON DELETE CASCADE,
    
    -- Ensure unique student-course pair (no duplicate enrollments)
    CONSTRAINT unique_student_course UNIQUE (student_id, course_id),
    
    -- Grade validation
    CONSTRAINT grade_valid CHECK (grade IN ('A', 'B', 'C', 'D', 'F', NULL))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_enrollment_student ON enrollment(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_course ON enrollment(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_date ON enrollment(enrollment_date);

/*
=====================================
ER DIAGRAM SUMMARY
=====================================

DEPARTMENT (1)
    ↓ 1:N
STUDENT (M)

DEPARTMENT (1)
    ↓ 1:N
COURSE (M)

STUDENT (N) ←→ (M) COURSE
    (via ENROLLMENT table)

=====================================
KEY CONSTRAINTS
=====================================
- PK: Unique identifier for each entity
- FK: Enforces referential integrity
- UNIQUE: Prevents duplicate entries
- CHECK: Validates data domain
- NOT NULL: Mandatory fields
- ON DELETE CASCADE: Delete enrollments when student deleted
- ON DELETE RESTRICT: Prevent deletion of referenced departments
*/
