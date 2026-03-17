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

with engine.connect() as conn:
    # 1. Get unique sections from students
    result = conn.execute(text("SELECT DISTINCT section FROM students WHERE section IS NOT NULL"))
    legacy_sections = [row[0] for row in result.all()]
    
    sections_created = 0
    students_updated = 0
    
    # 2. Iterate and create Sections if needed
    for sec_str in legacy_sections:
        # e.g., "BSIT-2A"
        if '-' not in sec_str:
            print(f"Skipping badly formatted section string: {sec_str}")
            continue
            
        program, rest = sec_str.split('-', 1) # ['BSIT', '2A']
        if len(rest) < 2:
             print(f"Skipping badly formatted section string (no year/letter): {sec_str}")
             continue
             
        try:
            year_level = int(rest[0])
            section_letter = rest[1:]
        except ValueError:
            print(f"Could not parse year from {sec_str}")
            continue
            
        # Insert or ignore (Postgres syntax for upsert/ignore is complex without ORM, 
        # so we'll check first, then insert)
        check_q = text("""
            SELECT id FROM sections 
            WHERE program = :program 
              AND year_level = :year_level 
              AND section_letter = :section_letter
        """)
        existing = conn.execute(check_q, {
            'program': program,
            'year_level': year_level,
            'section_letter': section_letter
        }).fetchone()
        
        section_id = None
        if existing:
            section_id = existing[0]
        else:
            insert_q = text("""
                INSERT INTO sections (program, year_level, section_letter, created_at)
                VALUES (:program, :year_level, :section_letter, NOW())
                RETURNING id
            """)
            result = conn.execute(insert_q, {
                'program': program,
                'year_level': year_level,
                'section_letter': section_letter
            })
            section_id = result.fetchone()[0]
            sections_created += 1
            
        # 3. Update students with this section_id
        update_q = text("""
            UPDATE students 
            SET section_id = :section_id 
            WHERE section = :legacy_section
        """)
        res = conn.execute(update_q, {
            'section_id': section_id,
            'legacy_section': sec_str
        })
        students_updated += res.rowcount
        
    conn.commit()
    print(f"Migration Complete: Created {sections_created} sections, Updated {students_updated} students.")
