import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

# SQLAlchemy 2.0 uses 'postgresql+psycopg' instead of 'postgres://'
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(database_url)

with engine.connect() as connection:
    # Query unique legacy sections
    result = connection.execute(text("SELECT section, COUNT(*) FROM students GROUP BY section"))
    print("Unique legacy sections and student counts:")
    for row in result:
        print(f"{row[0]}: {row[1]} students")

    # Query current sections table
    result = connection.execute(text("SELECT id, program, year_level, section_letter FROM sections"))
    print("\nExisting records in 'sections' table:")
    rows = result.all()
    if not rows:
        print("No sections found.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Program: {row[1]}, Year: {row[2]}, Letter: {row[3]}")
    
    # Check if any students already have section_id set
    result = connection.execute(text("SELECT COUNT(*) FROM students WHERE section_id IS NOT NULL"))
    count = result.scalar()
    print(f"\nStudents with section_id already set: {count}")
