import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.faculty import Faculty
from app.services import faculty_service
from app.models.academic_settings import AcademicSettings

app = create_app()
with app.app_context():
    # Get current period
    settings = AcademicSettings.get_current()
    semester = settings.current_semester
    year = settings.current_year
    print(f"Current Period: {semester} {year}")

    # Find a faculty
    faculty = Faculty.query.first()
    if not faculty:
        print("No faculty found.")
        sys.exit(0)
    
    print(f"Testing for faculty: {faculty.full_name} (ID: {faculty.id})")
    
    sections = faculty_service.get_faculty_sections(faculty.id, semester, year)
    print(f"Sections found: {len(sections)}")
    for sec in sections:
        print(f"  - {sec['name']} (Year {sec['year_level']}) - {sec['student_count']} students - Subjects: {sec['subjects']}")
        
        # Test students for this section
        data = faculty_service.get_students_for_section(faculty.id, sec['id'], semester, year)
        print(f"    - Section Students: {len(data['section_students'])}")
        print(f"    - Irregular Students: {len(data['irregular_students'])}")

print("Test complete.")
