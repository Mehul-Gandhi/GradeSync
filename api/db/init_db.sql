-- Sample code to create a table in the database
-- We will be copying and pasting in the database schema from mermaid here

-- This is wrong below this line but sample database schema

CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id SERIAL PRIMARY KEY,
    assignment_name VARCHAR(100),
    due_date DATE
);

CREATE TABLE IF NOT EXISTS grades (
    grade_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    assignment_id INT REFERENCES assignments(assignment_id),
    grade FLOAT,
    submission_date TIMESTAMP
);
