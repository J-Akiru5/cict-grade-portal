#!/usr/bin/env python3
"""
Seed specific mock data for assimangca@isufst.edu.ph
Creates User, Student profile, Subjects, Enrollments, Grades, and Schedule for BSIT 3B - WM.
Corrected for current DB schema.
"""

import os
import uuid
import psycopg
import secrets
from datetime import datetime, time, timezone
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if db_url and db_url.startswith('postgresql+psycopg://'):
        db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
    # Supabase Transaction Pooler often works better on 6543
    if db_url and ':5432/' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')

    if db_url:
        return psycopg.connect(db_url)
    
    return psycopg.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def main():
    print(">>> Seeding data for assimangca@isufst.edu.ph")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                email = "assimangca@isufst.edu.ph"
                now = datetime.now(timezone.utc)
                
                # 1. Ensure User exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user_row = cursor.fetchone()
                if user_row:
                    user_id = user_row[0]
                    print(f"[+] Found existing user for {email} (ID: {user_id})")
                else:
                    user_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO users (id, email, role, is_active, created_at)
                        VALUES (%s, %s, 'student', true, %s)
                    """, (user_id, email, now))
                    print(f"[+] Created mock user for {email} (ID: {user_id})")

                # 2. Ensure Section exists
                program, year_level, section_letter = 'BSIT', 3, 'B-WM'
                cursor.execute("""
                    SELECT id FROM sections 
                    WHERE program = %s AND year_level = %s AND section_letter = %s
                """, (program, year_level, section_letter))
                section_row = cursor.fetchone()
                if section_row:
                    section_id = section_row[0]
                else:
                    cursor.execute("""
                        INSERT INTO sections (program, year_level, section_letter, created_at)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (program, year_level, section_letter, now))
                    section_id = cursor.fetchone()[0]
                    print(f"[+] Created section BSIT-{year_level}{section_letter}")
                    
                # 3. Ensure Student Profile exists
                cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
                student_row = cursor.fetchone()
                if student_row:
                    student_id = student_row[0]
                    print(f"[+] Found existing student profile (ID: {student_id})")
                    cursor.execute("UPDATE students SET section_id = %s, section = %s, year_level = %s WHERE id = %s", 
                                   (section_id, 'BSIT-3B-WM', 3, student_id))
                else:
                    cursor.execute("""
                        INSERT INTO students (user_id, student_id, full_name, section, section_id, age, gender, gmail, curriculum_year, year_level, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                    """, (user_id, "2023-12345", "A. Simangca", "BSIT-3B-WM", section_id, 20, "Female", email, "2023-2024", 3, now, now))
                    student_id = cursor.fetchone()[0]
                    print(f"[+] Created student profile (Assigned ID: 2023-12345)")

                # 4. Define 3rd Year Subjects
                subjects = [
                    ("IT3201", "Web Systems and Technologies", 3),
                    ("IT3202", "Information Assurance and Security 2", 3),
                    ("IT3203", "Systems Integration and Architecture 2", 3),
                    ("IT3204", "Capstone Project 1", 3),
                    ("IT3205", "Social and Professional Issues", 3)
                ]
                
                subject_ids = {}
                for code, title, units in subjects:
                    cursor.execute("SELECT id FROM subjects WHERE subject_code = %s", (code,))
                    subj_row = cursor.fetchone()
                    if subj_row:
                        subject_ids[code] = subj_row[0]
                    else:
                        cursor.execute("""
                            INSERT INTO subjects (subject_code, subject_title, units, department)
                            VALUES (%s, %s, %s, %s) RETURNING id
                        """, (code, title, units, 'CICT'))
                        subject_ids[code] = cursor.fetchone()[0]
                        print(f"[+] Created subject {code}")

                # 5. Enrollments & Grades
                semester, acad_year = '2nd', '2025-2026'
                grades_data = [
                    ("IT3201", 1.25, "PASSED"),
                    ("IT3202", 1.50, "PASSED"),
                    ("IT3203", 1.75, "PASSED"),
                    ("IT3204", 1.00, "PASSED"),
                    ("IT3205", 1.25, "PASSED")
                ]
                
                for code, grade_val, remarks in grades_data:
                    subj_id = subject_ids[code]
                    
                    # Enrollment
                    cursor.execute("""
                        SELECT id FROM enrollments 
                        WHERE student_id = %s AND subject_id = %s AND semester = %s AND academic_year = %s
                    """, (student_id, subj_id, semester, acad_year))
                    enr_row = cursor.fetchone()
                    if enr_row:
                        enrollment_id = enr_row[0]
                    else:
                        cursor.execute("""
                            INSERT INTO enrollments (student_id, subject_id, semester, academic_year, enrolled_at)
                            VALUES (%s, %s, %s, %s, %s) RETURNING id
                        """, (student_id, subj_id, semester, acad_year, now))
                        enrollment_id = cursor.fetchone()[0]
                        
                    # Grade
                    cursor.execute("SELECT id FROM grades WHERE enrollment_id = %s", (enrollment_id,))
                    grade_row = cursor.fetchone()
                    if grade_row:
                        cursor.execute("UPDATE grades SET grade_value = %s, remarks = %s, date_encoded = %s WHERE id = %s", (grade_val, remarks, now, grade_row[0]))
                    else:
                        cursor.execute("""
                            INSERT INTO grades (enrollment_id, grade_value, remarks, date_encoded)
                            VALUES (%s, %s, %s, %s)
                        """, (enrollment_id, grade_val, remarks, now))
                print(f"[+] Seeded 3rd-year enrollments and mock grades")

                # 6. Schedules for BSIT-3B-WM
                cursor.execute("DELETE FROM schedules WHERE section_id = %s AND semester = %s AND academic_year = %s", (section_id, semester, acad_year))
                
                schedules = [
                    ("IT3201", "Mon", "07:30", "10:30"),
                    ("IT3202", "Tue", "13:00", "16:00"),
                    ("IT3203", "Wed", "07:30", "10:30"),
                    ("IT3204", "Thu", "13:00", "16:00"),
                    ("IT3205", "Fri", "07:30", "10:30"),
                ]
                
                for code, day, start_str, end_str in schedules:
                    subj_id = subject_ids[code]
                    start_time = time(*map(int, start_str.split(':')))
                    end_time = time(*map(int, end_str.split(':')))
                    
                    cursor.execute("""
                        INSERT INTO schedules (section_id, subject_id, day_of_week, time_start, time_end, room, academic_year, semester)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (section_id, subj_id, day, start_time, end_time, 'Lab 1', acad_year, semester))
                
                print(f"[+] Seeded schedules for BSIT 3B - WM")
                
                conn.commit()
                print(">>> Database seeding completed successfully!")
                
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
