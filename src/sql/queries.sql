/*
=====================================
SQL QUERIES & OPTIMIZATIONS
=====================================
Common queries for the student enrollment system
Includes aggregations, JOINs, reports, and optimizations
*/

-- ============================================
-- BASIC AGGREGATIONS
-- ============================================

-- 1. Count students per department
SELECT 
    d.name AS department,
    COUNT(s.student_id) AS student_count
FROM department d
LEFT JOIN student s ON d.department_id = s.department_id
GROUP BY d.department_id, d.name
ORDER BY student_count DESC;

-- 2. Average grade per course
SELECT 
    c.code,
    c.name,
    COUNT(e.enrollment_id) AS enrollment_count,
    ROUND(AVG(CASE 
        WHEN e.grade = 'A' THEN 4.0
        WHEN e.grade = 'B' THEN 3.0
        WHEN e.grade = 'C' THEN 2.0
        WHEN e.grade = 'D' THEN 1.0
        WHEN e.grade = 'F' THEN 0.0
        ELSE NULL
    END), 2) AS avg_grade_points
FROM course c
LEFT JOIN enrollment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.code, c.name
ORDER BY avg_grade_points DESC;

-- 3. Student GPA calculation
SELECT 
    s.student_id,
    s.name,
    COUNT(e.enrollment_id) AS courses_taken,
    ROUND(AVG(CASE 
        WHEN e.grade = 'A' THEN 4.0
        WHEN e.grade = 'B' THEN 3.0
        WHEN e.grade = 'C' THEN 2.0
        WHEN e.grade = 'D' THEN 1.0
        WHEN e.grade = 'F' THEN 0.0
        ELSE NULL
    END), 2) AS gpa
FROM student s
LEFT JOIN enrollment e ON s.student_id = e.student_id
GROUP BY s.student_id, s.name
ORDER BY gpa DESC NULLS LAST;

-- ============================================
-- JOIN-HEAVY QUERIES
-- ============================================

-- 4. Get all student enrollments with details
SELECT 
    s.student_id,
    s.name,
    s.year,
    d.name AS department,
    c.code,
    c.name AS course_name,
    e.grade,
    e.enrollment_date
FROM student s
JOIN department d ON s.department_id = d.department_id
LEFT JOIN enrollment e ON s.student_id = e.student_id
LEFT JOIN course c ON e.course_id = c.course_id
ORDER BY s.student_id, e.enrollment_date;

-- 5. Courses with student count
SELECT 
    c.code,
    c.name,
    d.name AS department,
    c.credits,
    COUNT(DISTINCT e.student_id) AS enrolled_students
FROM course c
JOIN department d ON c.department_id = d.department_id
LEFT JOIN enrollment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.code, c.name, d.name, c.credits
ORDER BY enrolled_students DESC;

-- ============================================
-- DATA QUALITY CHECKS
-- ============================================

-- 6. Find duplicate emails
SELECT 
    email,
    COUNT(*) AS occurrence_count
FROM student
GROUP BY email
HAVING COUNT(*) > 1;

-- 7. Students with no enrollments
SELECT 
    s.student_id,
    s.name,
    s.email,
    COUNT(e.enrollment_id) AS enrollment_count
FROM student s
LEFT JOIN enrollment e ON s.student_id = e.student_id
GROUP BY s.student_id, s.name, s.email
HAVING COUNT(e.enrollment_id) = 0;

-- 8. Courses with no students
SELECT 
    c.course_id,
    c.code,
    c.name,
    COUNT(e.enrollment_id) AS student_count
FROM course c
LEFT JOIN enrollment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.code, c.name
HAVING COUNT(e.enrollment_id) = 0;

-- 9. Find orphaned records (shouldn't exist due to FK constraints)
SELECT 
    'Student with invalid dept' AS issue,
    COUNT(*) AS count
FROM student
WHERE department_id NOT IN (SELECT department_id FROM department)
UNION ALL
SELECT 
    'Course with invalid dept',
    COUNT(*)
FROM course
WHERE department_id NOT IN (SELECT department_id FROM department);

-- ============================================
-- REPORTS
-- ============================================

-- 10. Department Performance Report
SELECT 
    d.name AS department,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT c.course_id) AS total_courses,
    COUNT(DISTINCT e.enrollment_id) AS total_enrollments,
    ROUND(AVG(CASE 
        WHEN e.grade = 'A' THEN 4.0
        WHEN e.grade = 'B' THEN 3.0
        WHEN e.grade = 'C' THEN 2.0
        WHEN e.grade = 'D' THEN 1.0
        ELSE 0.0
    END), 2) AS avg_department_gpa
FROM department d
LEFT JOIN student s ON d.department_id = s.department_id
LEFT JOIN course c ON d.department_id = c.department_id
LEFT JOIN enrollment e ON c.course_id = e.course_id
GROUP BY d.department_id, d.name
ORDER BY total_students DESC;

-- 11. Year-wise student distribution
SELECT 
    s.year,
    COUNT(DISTINCT s.student_id) AS student_count,
    ROUND(100.0 * COUNT(DISTINCT s.student_id) / 
        (SELECT COUNT(*) FROM student), 2) AS percentage
FROM student s
GROUP BY s.year
ORDER BY s.year;

-- ============================================
-- OPTIMIZATION: EXPLAIN ANALYZE
-- ============================================

-- Check query performance
EXPLAIN ANALYZE
SELECT s.name, COUNT(e.enrollment_id) AS course_count
FROM student s
LEFT JOIN enrollment e ON s.student_id = e.student_id
GROUP BY s.student_id, s.name;

/*
Expected output shows:
- Seq Scan vs Index Scan
- Est. vs Actual rows
- Execution time
*/
