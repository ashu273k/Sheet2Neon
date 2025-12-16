/*
=====================================
VIEWS & STORED PROCEDURES
=====================================
Reusable database objects for common operations
*/

-- ============================================
-- VIEWS
-- ============================================

-- 1. Student Summary View
CREATE OR REPLACE VIEW v_student_summary AS
SELECT 
    s.student_id,
    s.name,
    s.email,
    s.year,
    d.name AS department,
    COUNT(e.enrollment_id) AS courses_enrolled,
    ROUND(AVG(CASE 
        WHEN e.grade = 'A' THEN 4.0
        WHEN e.grade = 'B' THEN 3.0
        WHEN e.grade = 'C' THEN 2.0
        WHEN e.grade = 'D' THEN 1.0
        ELSE 0.0
    END), 2) AS gpa
FROM student s
JOIN department d ON s.department_id = d.department_id
LEFT JOIN enrollment e ON s.student_id = e.student_id
GROUP BY s.student_id, s.name, s.email, s.year, d.name;

-- 2. Course Analytics View
CREATE OR REPLACE VIEW v_course_analytics AS
SELECT 
    c.course_id,
    c.code,
    c.name,
    d.name AS department,
    COUNT(DISTINCT e.student_id) AS enrollment_count,
    COUNT(DISTINCT CASE WHEN e.grade = 'A' THEN e.student_id END) AS grade_a_count,
    COUNT(DISTINCT CASE WHEN e.grade = 'F' THEN e.student_id END) AS grade_f_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.grade = 'A' THEN e.student_id END) / 
        NULLIF(COUNT(DISTINCT e.student_id), 0), 2) AS percent_a_grade
FROM course c
JOIN department d ON c.department_id = d.department_id
LEFT JOIN enrollment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.code, c.name, d.name;

-- ============================================
-- STORED PROCEDURES
-- ============================================

-- 1. Register student in course
CREATE OR REPLACE FUNCTION register_student_course(
    p_student_id INT,
    p_course_id INT
)
RETURNS TABLE (success BOOLEAN, message TEXT) AS $$
DECLARE
    v_student_exists BOOLEAN;
    v_course_exists BOOLEAN;
BEGIN
    -- Check if student exists
    SELECT EXISTS(SELECT 1 FROM student WHERE student_id = p_student_id) 
    INTO v_student_exists;
    
    -- Check if course exists
    SELECT EXISTS(SELECT 1 FROM course WHERE course_id = p_course_id) 
    INTO v_course_exists;
    
    IF NOT v_student_exists THEN
        RETURN QUERY SELECT FALSE, 'Student not found'::TEXT;
        RETURN;
    END IF;
    
    IF NOT v_course_exists THEN
        RETURN QUERY SELECT FALSE, 'Course not found'::TEXT;
        RETURN;
    END IF;
    
    -- Check if already enrolled
    IF EXISTS(SELECT 1 FROM enrollment 
              WHERE student_id = p_student_id AND course_id = p_course_id) THEN
        RETURN QUERY SELECT FALSE, 'Already enrolled in this course'::TEXT;
        RETURN;
    END IF;
    
    -- Insert enrollment
    INSERT INTO enrollment (student_id, course_id)
    VALUES (p_student_id, p_course_id);
    
    RETURN QUERY SELECT TRUE, 'Registration successful'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- 2. Calculate GPA for a student
CREATE OR REPLACE FUNCTION calculate_student_gpa(p_student_id INT)
RETURNS NUMERIC AS $$
DECLARE
    v_gpa NUMERIC;
BEGIN
    SELECT ROUND(AVG(CASE 
        WHEN grade = 'A' THEN 4.0
        WHEN grade = 'B' THEN 3.0
        WHEN grade = 'C' THEN 2.0
        WHEN grade = 'D' THEN 1.0
        ELSE 0.0
    END), 2)
    INTO v_gpa
    FROM enrollment
    WHERE student_id = p_student_id;
    
    RETURN COALESCE(v_gpa, 0);
END;
$$ LANGUAGE plpgsql;

-- 3. Get students by department
CREATE OR REPLACE FUNCTION get_students_by_dept(p_dept_id INT)
RETURNS TABLE (
    student_id INT,
    name VARCHAR,
    email VARCHAR,
    year INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT s.student_id, s.name, s.email, s.year
    FROM student s
    WHERE s.department_id = p_dept_id
    ORDER BY s.name;
END;
$$ LANGUAGE plpgsql;
