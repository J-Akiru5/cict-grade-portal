from app import create_app
from app.extensions import db
from sqlalchemy import func

app = create_app()
with app.app_context():
    # Import Student here to avoid potential circular issues
    from app.models.student import Student
    
    sections = db.session.query(Student.section, func.count(Student.id)).group_by(Student.section).all()
    print("Unique legacy sections and student counts:")
    for section_text, count in sections:
        print(f"{section_text}: {count} students")

    # Also check if any sections already exist
    from app.models.section import Section
    existing_sections = Section.query.all()
    print(f"\nExisting records in 'sections' table: {len(existing_sections)}")
    for s in existing_sections:
        print(f"ID: {s.id}, Name: {s.display_name}")
