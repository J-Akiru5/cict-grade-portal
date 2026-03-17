import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(database_url)

with engine.connect() as connection:
    # 1. Check for students who SHOULD have a section_id but don't
    result = connection.execute(text("""
        SELECT student_id, section, section_id 
        FROM students 
        WHERE section IS NOT NULL AND section_id IS NULL
    """))
    unlinked = result.all()
    if unlinked:
        print(f"FAILED: {len(unlinked)} students are unlinked!")
        for row in unlinked:
            print(f"Student: {row[0]}, Legacy Section: {row[1]}")
    else:
        print("SUCCESS: All students with legacy sections have been linked to a section_id.")

    # 2. Check for students where section_id doesn't match the legacy section string
    # We join on sections and check if f"{program}-{year_level}{letter}" matches section
    result = connection.execute(text("""
        SELECT s.student_id, s.section, sec.program, sec.year_level, sec.section_letter
        FROM students s
        JOIN sections sec ON s.section_id = sec.id
    """))
    mismatches = []
    for row in result:
        reconstructed = f"{row[2]}-{row[3]}{row[4]}"
        if reconstructed != row[1]:
            mismatches.append((row[0], row[1], reconstructed))
    
    if mismatches:
        print(f"FAILED: {len(mismatches)} mismatches found!")
        for m in mismatches[:10]:
            print(f"Student {m[0]}: Legacy '{m[1]}' vs Linked '{m[2]}'")
    else:
        print("SUCCESS: All linked section_ids match the legacy section strings.")

    # 3. Final counts
    student_count = connection.execute(text("SELECT COUNT(*) FROM students")).scalar()
    linked_count = connection.execute(text("SELECT COUNT(*) FROM students WHERE section_id IS NOT NULL")).scalar()
    section_count = connection.execute(text("SELECT COUNT(*) FROM sections")).scalar()
    
    print(f"\nFinal Stats:")
    print(f"Total Students: {student_count}")
    print(f"Total Sections Created: {section_count}")
    print(f"Students Linked to Sections: {linked_count}")
