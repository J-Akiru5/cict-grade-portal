#!/usr/bin/env python3
"""
Schedule Seeder for CICT Grade Portal
Semester: 2nd Semester, A.Y. 2025-2026

This script seeds the database with class schedules extracted from the
physical schedule images provided by the CICT department.
"""

from app import create_app, db
from app.models.schedule import Schedule
from app.models.subject import Subject
from app.models.faculty import Faculty
from app.models.user import User
from app.models.section import Section
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import time

def create_time(time_str):
    """Convert time string like '8:00' to time object"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except:
        return None

def get_or_create_subject(subject_code, subject_title, units=3):
    """Get existing subject or create new one"""
    subject = Subject.query.filter_by(subject_code=subject_code).first()
    if not subject:
        subject = Subject(
            subject_code=subject_code,
            subject_title=subject_title,
            units=units,
            department="CICT"
        )
        db.session.add(subject)
        print(f"✓ Created subject: {subject_code} - {subject_title}")
    return subject

def get_or_create_faculty(faculty_name):
    """Get existing faculty or create new one"""
    if not faculty_name or faculty_name.strip() == "":
        return None

    faculty = Faculty.query.filter_by(full_name=faculty_name).first()
    if not faculty:
        # Create a user account for the faculty
        user = User(
            id=str(uuid.uuid4()),
            email=f"{faculty_name.lower().replace(' ', '.')}@isufst.edu.ph",
            role='faculty',
            is_active=True
        )
        db.session.add(user)
        db.session.flush()

        # Create faculty record
        faculty = Faculty(
            user_id=user.id,
            full_name=faculty_name,
            employee_id=f"FAC{Faculty.query.count() + 1:04d}",
            department="CICT"
        )
        db.session.add(faculty)
        print(f"✓ Created faculty: {faculty_name}")
    return faculty

def get_section(section_name):
    """Get section by name (e.g., 'BSIT-1A')"""
    if not section_name.startswith('BSIT-'):
        return None

    parts = section_name.split('-')
    if len(parts) != 2:
        return None

    program = parts[0]  # 'BSIT'
    year_section = parts[1]  # '1A', '2B-NT', etc.

    # Extract year level and section letter
    year_level = int(year_section[0])
    section_letter = year_section[1:]

    section = Section.query.filter_by(
        program=program,
        year_level=year_level,
        section_letter=section_letter
    ).first()

    return section

def create_schedule_entry(section_name, subject_code, subject_title, faculty_name,
                         day, time_start, time_end, room="", units=3):
    """Create a schedule entry"""
    try:
        # Get or create entities
        subject = get_or_create_subject(subject_code, subject_title, units)
        faculty = get_or_create_faculty(faculty_name)
        section = get_section(section_name)

        if not section:
            print(f"⚠ Section not found: {section_name}")
            return None

        # Convert time strings to time objects
        start_time = create_time(time_start)
        end_time = create_time(time_end)

        if not start_time or not end_time:
            print(f"⚠ Invalid time format: {time_start}-{time_end}")
            return None

        # Create schedule entry
        schedule = Schedule(
            section_id=section.id,
            faculty_id=faculty.id if faculty else None,
            subject_id=subject.id,
            day_of_week=day,
            time_start=start_time,
            time_end=end_time,
            room=room,
            academic_year="2025-2026",
            semester="2nd"
        )

        db.session.add(schedule)
        print(f"✓ {section_name} | {subject_code} | {faculty_name} | {day} {time_start}-{time_end}")

        return schedule

    except Exception as e:
        print(f"✗ Error creating schedule: {e}")
        return None

def seed_all_schedules():
    """Seed all schedules from the images"""

    print("🚀 Starting schedule seeding for 2nd Semester A.Y. 2025-2026")
    print("=" * 60)

    # BSIT 1A Schedule
    print("\n📚 BSIT-1A Schedule")
    bsit_1a_schedules = [
        # Monday
        ("BSIT-1A", "GEC1101", "Understanding the Self", "Arianne Cagape", "Mon", "8:00", "9:00"),
        ("BSIT-1A", "IT1101", "Introduction to Computing", "Jenyfer Nardo", "Mon", "9:00", "12:00"),
        ("BSIT-1A", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Mon", "1:00", "3:00"),
        # Tuesday
        ("BSIT-1A", "GEC1106", "Science, Technology and Society", "Jenevie A. Siaron", "Tue", "8:00", "11:00"),
        ("BSIT-1A", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-1A", "GEC1101", "Understanding the Self", "Arianne Cagape", "Wed", "8:00", "9:00"),
        ("BSIT-1A", "IT1101", "Introduction to Computing", "Jenyfer Nardo", "Wed", "9:00", "12:00"),
        ("BSIT-1A", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Wed", "1:00", "3:00"),
        # Thursday
        ("BSIT-1A", "GEC1106", "Science, Technology and Society", "Jenevie A. Siaron", "Thu", "8:00", "11:00"),
        ("BSIT-1A", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-1A", "GEC1103", "Contemporary World", "Jenevie A. Siaron", "Fri", "8:00", "11:00"),
        ("BSIT-1A", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "1:00", "3:00"),
        ("BSIT-1A", "PE2", "Physical Education 2", "PE Instructor", "Fri", "3:00", "5:00"),
    ]

    # BSIT 1B Schedule
    print("\n📚 BSIT-1B Schedule")
    bsit_1b_schedules = [
        # Monday
        ("BSIT-1B", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Mon", "8:00", "11:00"),
        ("BSIT-1B", "GEC1103", "Contemporary World", "Jenevie A. Siaron", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-1B", "GEC1101", "Understanding the Self", "Arianne Cagape", "Tue", "10:00", "11:00"),
        ("BSIT-1B", "IT1101", "Introduction to Computing", "Jenyfer Nardo", "Tue", "11:00", "2:00"),
        ("BSIT-1B", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Tue", "3:00", "5:00"),
        # Wednesday
        ("BSIT-1B", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Wed", "8:00", "11:00"),
        ("BSIT-1B", "GEC1103", "Contemporary World", "Jenevie A. Siaron", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-1B", "GEC1101", "Understanding the Self", "Arianne Cagape", "Thu", "10:00", "11:00"),
        ("BSIT-1B", "IT1101", "Introduction to Computing", "Jenyfer Nardo", "Thu", "11:00", "2:00"),
        ("BSIT-1B", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Thu", "3:00", "5:00"),
        # Friday
        ("BSIT-1B", "GEC1106", "Science, Technology and Society", "Jenevie A. Siaron", "Fri", "8:00", "11:00"),
        ("BSIT-1B", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "1:00", "3:00"),
        ("BSIT-1B", "PE2", "Physical Education 2", "PE Instructor", "Fri", "3:00", "5:00"),
    ]

    # BSIT 1C Schedule
    print("\n📚 BSIT-1C Schedule")
    bsit_1c_schedules = [
        # Monday
        ("BSIT-1C", "GEC1106", "Science, Technology and Society", "Jenevie A. Siaron", "Mon", "8:00", "11:00"),
        ("BSIT-1C", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-1C", "GEC1103", "Contemporary World", "Jenevie A. Siaron", "Tue", "8:00", "11:00"),
        ("BSIT-1C", "GEC1101", "Understanding the Self", "Arianne Cagape", "Tue", "1:00", "2:00"),
        ("BSIT-1C", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Tue", "2:00", "4:00"),
        # Wednesday
        ("BSIT-1C", "GEC1106", "Science, Technology and Society", "Jenevie A. Siaron", "Wed", "8:00", "11:00"),
        ("BSIT-1C", "IT1102", "Computer Programming 1", "Jenyfer Nardo", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-1C", "GEC1103", "Contemporary World", "Jenevie A. Siaron", "Thu", "8:00", "11:00"),
        ("BSIT-1C", "GEC1101", "Understanding the Self", "Arianne Cagape", "Thu", "1:00", "2:00"),
        ("BSIT-1C", "GEC1105", "Mathematics in the Modern World", "Jay-ar Baronda", "Thu", "2:00", "4:00"),
        # Friday
        ("BSIT-1C", "IT1101", "Introduction to Computing", "Jenyfer Nardo", "Fri", "8:00", "11:00"),
        ("BSIT-1C", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "1:00", "3:00"),
        ("BSIT-1C", "PE2", "Physical Education 2", "PE Instructor", "Fri", "3:00", "5:00"),
    ]

    # BSIT 2A Schedule (Web/Mobile)
    print("\n📚 BSIT-2A Schedule (Web/Mobile)")
    bsit_2a_schedules = [
        # Monday
        ("BSIT-2A", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Mon", "8:00", "11:00"),
        ("BSIT-2A", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Mon", "1:00", "3:00"),
        ("BSIT-2A", "GEC1108", "Ethics", "Arianne Cagape", "Mon", "3:00", "5:00"),
        # Tuesday
        ("BSIT-2A", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Tue", "8:00", "11:00"),
        ("BSIT-2A", "IT2103", "Web Development 1", "Jay-ar Baronda", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-2A", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Wed", "8:00", "11:00"),
        ("BSIT-2A", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Wed", "1:00", "3:00"),
        ("BSIT-2A", "GEC1108", "Ethics", "Arianne Cagape", "Wed", "3:00", "5:00"),
        # Thursday
        ("BSIT-2A", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Thu", "8:00", "11:00"),
        ("BSIT-2A", "IT2103", "Web Development 1", "Jay-ar Baronda", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-2A", "GEC1104", "Purposive Communication", "English Faculty", "Fri", "8:00", "11:00"),
        ("BSIT-2A", "PE3", "Physical Education 3", "PE Instructor", "Fri", "1:00", "3:00"),
    ]

    # BSIT 2B Schedule (Web/Mobile)
    print("\n📚 BSIT-2B Schedule (Web/Mobile)")
    bsit_2b_schedules = [
        # Monday
        ("BSIT-2B", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Mon", "8:00", "11:00"),
        ("BSIT-2B", "GEC1104", "Purposive Communication", "English Faculty", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-2B", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Tue", "9:00", "11:00"),
        ("BSIT-2B", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-2B", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Wed", "8:00", "11:00"),
        ("BSIT-2B", "GEC1104", "Purposive Communication", "English Faculty", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-2B", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Thu", "9:00", "11:00"),
        ("BSIT-2B", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-2B", "IT2103", "Web Development 1", "Jay-ar Baronda", "Fri", "8:00", "11:00"),
        ("BSIT-2B", "GEC1108", "Ethics", "Arianne Cagape", "Fri", "1:00", "3:00"),
        ("BSIT-2B", "PE3", "Physical Education 3", "PE Instructor", "Fri", "3:00", "5:00"),
    ]

    # BSIT 2C-NT Schedule (Non-Traditional - Evening)
    print("\n📚 BSIT-2C-NT Schedule (Non-Traditional)")
    bsit_2c_nt_schedules = [
        # Monday
        ("BSIT-2C-NT", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Mon", "17:00", "20:00"),
        # Tuesday
        ("BSIT-2C-NT", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Tue", "17:00", "20:00"),
        # Wednesday
        ("BSIT-2C-NT", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Wed", "17:00", "19:00"),
        ("BSIT-2C-NT", "GEC1108", "Ethics", "Arianne Cagape", "Wed", "19:00", "21:00"),
        # Thursday
        ("BSIT-2C-NT", "IT2103", "Web Development 1", "Jay-ar Baronda", "Thu", "17:00", "20:00"),
        # Friday
        ("BSIT-2C-NT", "GEC1104", "Purposive Communication", "English Faculty", "Fri", "17:00", "20:00"),
        # Saturday
        ("BSIT-2C-NT", "PE3", "Physical Education 3", "PE Instructor", "Sat", "8:00", "10:00"),
    ]

    # BSIT 2D-NT Schedule (Non-Traditional - Evening)
    print("\n📚 BSIT-2D-NT Schedule (Non-Traditional)")
    bsit_2d_nt_schedules = [
        # Monday
        ("BSIT-2D-NT", "IT2102", "Object Oriented Programming", "Jenyfer Nardo", "Mon", "17:00", "20:00"),
        # Tuesday
        ("BSIT-2D-NT", "GEC1104", "Purposive Communication", "English Faculty", "Tue", "17:00", "20:00"),
        # Wednesday
        ("BSIT-2D-NT", "IT2101", "Data Structures and Algorithms", "Jenyfer Nardo", "Wed", "17:00", "20:00"),
        # Thursday
        ("BSIT-2D-NT", "GEC1107", "The Life and Works of Rizal", "Arianne Cagape", "Thu", "17:00", "19:00"),
        ("BSIT-2D-NT", "GEC1108", "Ethics", "Arianne Cagape", "Thu", "19:00", "21:00"),
        # Friday
        ("BSIT-2D-NT", "IT2103", "Web Development 1", "Jay-ar Baronda", "Fri", "17:00", "20:00"),
        # Saturday
        ("BSIT-2D-NT", "PE3", "Physical Education 3", "PE Instructor", "Sat", "8:00", "10:00"),
    ]

    # BSIT 3A-WM Schedule (Web/Mobile)
    print("\n📚 BSIT-3A-WM Schedule (Web/Mobile)")
    bsit_3a_wm_schedules = [
        # Monday
        ("BSIT-3A-WM", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Mon", "8:00", "11:00"),
        ("BSIT-3A-WM", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-3A-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Tue", "8:00", "11:00"),
        ("BSIT-3A-WM", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-3A-WM", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Wed", "8:00", "11:00"),
        ("BSIT-3A-WM", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-3A-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Thu", "8:00", "11:00"),
        ("BSIT-3A-WM", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-3A-WM", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Fri", "8:00", "11:00"),
        ("BSIT-3A-WM", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Fri", "1:00", "3:00"),
    ]

    # BSIT 3A-NT Schedule (Non-Traditional)
    print("\n📚 BSIT-3A-NT Schedule (Non-Traditional)")
    bsit_3a_nt_schedules = [
        # Monday
        ("BSIT-3A-NT", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Mon", "17:00", "20:00"),
        # Tuesday
        ("BSIT-3A-NT", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Tue", "17:00", "20:00"),
        # Wednesday
        ("BSIT-3A-NT", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Wed", "17:00", "20:00"),
        # Thursday
        ("BSIT-3A-NT", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Thu", "17:00", "20:00"),
        # Friday
        ("BSIT-3A-NT", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Fri", "17:00", "20:00"),
        # Saturday
        ("BSIT-3A-NT", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Sat", "8:00", "11:00"),
    ]

    # BSIT 3B-WM Schedule (Web/Mobile)
    print("\n📚 BSIT-3B-WM Schedule (Web/Mobile)")
    bsit_3b_wm_schedules = [
        # Monday
        ("BSIT-3B-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Mon", "8:00", "11:00"),
        ("BSIT-3B-WM", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Mon", "1:00", "3:00"),
        # Tuesday
        ("BSIT-3B-WM", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Tue", "8:00", "11:00"),
        ("BSIT-3B-WM", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-3B-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Wed", "8:00", "11:00"),
        ("BSIT-3B-WM", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Wed", "1:00", "3:00"),
        # Thursday
        ("BSIT-3B-WM", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Thu", "8:00", "11:00"),
        ("BSIT-3B-WM", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-3B-WM", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Fri", "8:00", "11:00"),
        ("BSIT-3B-WM", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Fri", "1:00", "4:00"),
    ]

    # BSIT 3B-NT Schedule (Non-Traditional)
    print("\n📚 BSIT-3B-NT Schedule (Non-Traditional)")
    bsit_3b_nt_schedules = [
        # Monday
        ("BSIT-3B-NT", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Mon", "17:00", "20:00"),
        # Tuesday
        ("BSIT-3B-NT", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Tue", "17:00", "20:00"),
        # Wednesday
        ("BSIT-3B-NT", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Wed", "17:00", "20:00"),
        # Thursday
        ("BSIT-3B-NT", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Thu", "17:00", "20:00"),
        # Friday
        ("BSIT-3B-NT", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Fri", "17:00", "20:00"),
        # Saturday
        ("BSIT-3B-NT", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Sat", "8:00", "11:00"),
    ]

    # BSIT 3C-WM Schedule (Web/Mobile)
    print("\n📚 BSIT-3C-WM Schedule (Web/Mobile)")
    bsit_3c_wm_schedules = [
        # Monday
        ("BSIT-3C-WM", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Mon", "8:00", "11:00"),
        ("BSIT-3C-WM", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-3C-WM", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Tue", "8:00", "10:00"),
        ("BSIT-3C-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Tue", "10:00", "1:00"),
        # Wednesday
        ("BSIT-3C-WM", "GEC1109", "Filipino sa IBA't-IBAng Disiplina", "Filipino Faculty", "Wed", "8:00", "11:00"),
        ("BSIT-3C-WM", "IT3102WM", "Mobile Application Development", "Jay-ar Baronda", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-3C-WM", "IT3105", "Human Computer Interaction", "Jenyfer Nardo", "Thu", "8:00", "10:00"),
        ("BSIT-3C-WM", "IT3103", "Systems Analysis and Design", "Jenyfer Nardo", "Thu", "10:00", "1:00"),
        # Friday
        ("BSIT-3C-WM", "IT3101", "Database Management Systems", "Jay-ar Baronda", "Fri", "8:00", "11:00"),
        ("BSIT-3C-WM", "IT3104WM", "Advanced Web Development", "Jay-ar Baronda", "Fri", "1:00", "4:00"),
    ]

    # Combine all schedules
    all_schedules = (
        bsit_1a_schedules + bsit_1b_schedules + bsit_1c_schedules +
        bsit_2a_schedules + bsit_2b_schedules + bsit_2c_nt_schedules + bsit_2d_nt_schedules +
        bsit_3a_wm_schedules + bsit_3a_nt_schedules + bsit_3b_wm_schedules +
        bsit_3b_nt_schedules + bsit_3c_wm_schedules
    )

    return all_schedules

def main():
    """Main seeding function - used when running the script directly"""
    app = create_app()

    with app.app_context():
        print("🏫 CICT Grade Portal - Schedule Seeder")
        print("📅 Academic Year: 2025-2026")
        print("📖 Semester: 2nd Semester")
        print("=" * 50)

        try:
            # First ensure sections exist
            from seed_sections import seed_missing_sections
            seed_missing_sections()

            # Get all schedule data
            schedules = seed_all_schedules()

            # Create all schedule entries
            created_count = 0
            for schedule_data in schedules:
                result = create_schedule_entry(*schedule_data)
                if result:
                    created_count += 1

            # Commit all changes
            db.session.commit()

            print(f"\n✅ Successfully created {created_count} schedule entries")
            print("🎓 Schedule seeding completed!")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise

if __name__ == "__main__":
    main()