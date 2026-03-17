from app import create_app
from app.extensions import db
from app.models.student import Student
from sqlalchemy import func

app = create_app()
with app.app_context():
    sections = db.session.query(Student.section, func.count(Student.id)).group_by(Student.section).all()
    print("Unique legacy sections and student counts:")
    for section_text, count in sections:
        print(f"{section_text}: {count} students")
