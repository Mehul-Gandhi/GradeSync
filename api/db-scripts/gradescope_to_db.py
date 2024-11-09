# src/load_gradescope_data.py

# Heavily update this because it uses the wrong database schema for now
# This is placeholder code for the future

import json
import psycopg2
from src.database import connect_db

def load_gradescope_data(json_file_path):
    # Open the JSON file from Gradescope
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    conn = connect_db()
    if conn is None:
        print("Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cursor:
            # Insert or update students
            for student in data["students"]:
                cursor.execute("""
                    INSERT INTO students (name, email)
                    VALUES (%s, %s)
                    ON CONFLICT (email) DO NOTHING
                """, (student["name"], student["email"]))
            
            # Insert assignments and grades
            for assignment in data["assignments"]:
                cursor.execute("""
                    INSERT INTO assignments (assignment_name, due_date)
                    VALUES (%s, %s)
                    ON CONFLICT (assignment_name) DO NOTHING
                    RETURNING assignment_id
                """, (assignment["name"], assignment["due_date"]))
                assignment_id = cursor.fetchone()[0]

                for grade_entry in assignment["grades"]:
                    cursor.execute("""
                        INSERT INTO grades (student_id, assignment_id, grade, submission_date)
                        VALUES (
                            (SELECT student_id FROM students WHERE email = %s),
                            %s, %s, %s
                        )
                        ON CONFLICT (student_id, assignment_id) DO UPDATE SET
                        grade = EXCLUDED.grade,
                        submission_date = EXCLUDED.submission_date
                    """, (grade_entry["student_email"], assignment_id, grade_entry["grade"], grade_entry["submission_date"]))
                    
            conn.commit()
            print("Gradescope data loaded successfully.")
    except Exception as e:
        print(f"Error loading Gradescope data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Path to your Gradescope JSON file
    json_file_path = "../data/gradescope_data.json"
    load_gradescope_data(json_file_path)