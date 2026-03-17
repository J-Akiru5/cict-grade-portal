#!/usr/bin/env python3
"""
OFFICIAL SCHEDULE SEEDER for CICT Grade Portal
Based on actual ISUFST CICT schedules for 2nd Semester A.Y. 2025-2026

This script contains the REAL subject codes and schedules as used by CICT.
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

def seed_official_schedules():
    """Seed all OFFICIAL schedules from ISUFST CICT images"""

    print("🚀 Starting OFFICIAL schedule seeding for 2nd Semester A.Y. 2025-2026")
    print("📋 Based on actual ISUFST CICT schedule documents")
    print("=" * 60)

    # Clear existing schedules for 2025-2026, 2nd semester first
    existing_count = Schedule.query.filter_by(
        academic_year="2025-2026",
        semester="2nd"
    ).count()

    if existing_count > 0:
        print(f"🗑 Clearing {existing_count} existing schedule entries...")
        Schedule.query.filter_by(
            academic_year="2025-2026",
            semester="2nd"
        ).delete()

    # BSIT 1A Schedule - OFFICIAL DATA
    print("\n📚 BSIT-1A Schedule (OFFICIAL)")
    bsit_1a_schedules = [
        # Monday
        ("BSIT-1A", "IT1204", "Introduction to Computing", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-1A", "GEE1201", "Understanding the Self", "Arianne Cagape", "Mon", "10:30", "12:00"),
        ("BSIT-1A", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Mon", "1:00", "2:30"),
        # Tuesday
        ("BSIT-1A", "IT1205", "Data Structures and Algorithms", "Jenyfer Nardo", "Tue", "7:30", "10:30"),
        ("BSIT-1A", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-1A", "IT1204", "Introduction to Computing", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-1A", "GEE1201", "Understanding the Self", "Arianne Cagape", "Wed", "10:30", "12:00"),
        ("BSIT-1A", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Wed", "1:00", "2:30"),
        # Thursday
        ("BSIT-1A", "IT1205", "Data Structures and Algorithms", "Jenyfer Nardo", "Thu", "7:30", "10:30"),
        ("BSIT-1A", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-1A", "GEC1204", "Contemporary World", "Jenevie A. Siaron", "Fri", "7:30", "10:30"),
        ("BSIT-1A", "PATHFIT2", "Physical Education 2", "PE Instructor", "Fri", "1:00", "3:00"),
        ("BSIT-1A", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "3:00", "5:00"),
    ]

    # BSIT 1B Schedule - OFFICIAL DATA
    print("\n📚 BSIT-1B Schedule (OFFICIAL)")
    bsit_1b_schedules = [
        # Monday
        ("BSIT-1B", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-1B", "GEC1204", "Contemporary World", "Jenevie A. Siaron", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-1B", "GEE1201", "Understanding the Self", "Arianne Cagape", "Tue", "10:30", "12:00"),
        ("BSIT-1B", "IT1204", "Introduction to Computing", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        ("BSIT-1B", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Tue", "4:00", "5:30"),
        # Wednesday
        ("BSIT-1B", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-1B", "GEC1204", "Contemporary World", "Jenevie A. Siaron", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-1B", "GEE1201", "Understanding the Self", "Arianne Cagape", "Thu", "10:30", "12:00"),
        ("BSIT-1B", "IT1204", "Introduction to Computing", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        ("BSIT-1B", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Thu", "4:00", "5:30"),
        # Friday
        ("BSIT-1B", "IT1205", "Data Structures and Algorithms", "Jenyfer Nardo", "Fri", "7:30", "10:30"),
        ("BSIT-1B", "PATHFIT2", "Physical Education 2", "PE Instructor", "Fri", "1:00", "3:00"),
        ("BSIT-1B", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "3:00", "5:00"),
    ]

    # BSIT 1C Schedule - OFFICIAL DATA
    print("\n📚 BSIT-1C Schedule (OFFICIAL)")
    bsit_1c_schedules = [
        # Monday
        ("BSIT-1C", "IT1205", "Data Structures and Algorithms", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-1C", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-1C", "GEC1204", "Contemporary World", "Jenevie A. Siaron", "Tue", "7:30", "10:30"),
        ("BSIT-1C", "GEE1201", "Understanding the Self", "Arianne Cagape", "Tue", "1:00", "2:30"),
        ("BSIT-1C", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Tue", "2:30", "4:00"),
        # Wednesday
        ("BSIT-1C", "IT1205", "Data Structures and Algorithms", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-1C", "IT1206", "Computer Programming 1", "Jenyfer Nardo", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-1C", "GEC1204", "Contemporary World", "Jenevie A. Siaron", "Thu", "7:30", "10:30"),
        ("BSIT-1C", "GEE1201", "Understanding the Self", "Arianne Cagape", "Thu", "1:00", "2:30"),
        ("BSIT-1C", "GEM2201", "Mathematics in the Modern World", "Jay-ar Baronda", "Thu", "2:30", "4:00"),
        # Friday
        ("BSIT-1C", "IT1204", "Introduction to Computing", "Jenyfer Nardo", "Fri", "7:30", "10:30"),
        ("BSIT-1C", "PATHFIT2", "Physical Education 2", "PE Instructor", "Fri", "1:00", "3:00"),
        ("BSIT-1C", "NSTP2", "National Service Training Program 2", "NSTP Coordinator", "Fri", "3:00", "5:00"),
    ]

    # BSIT 2A-WM Schedule - OFFICIAL DATA
    print("\n📚 BSIT-2A-WM Schedule (Web/Mobile - OFFICIAL)")
    bsit_2a_wm_schedules = [
        # Monday
        ("BSIT-2A-WM", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-2A-WM", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Mon", "1:00", "2:30"),
        ("BSIT-2A-WM", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Mon", "2:30", "5:30"),
        # Tuesday
        ("BSIT-2A-WM", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Tue", "7:30", "10:30"),
        ("BSIT-2A-WM", "IT2217", "Systems Analysis and Design", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-2A-WM", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-2A-WM", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Wed", "1:00", "2:30"),
        ("BSIT-2A-WM", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Wed", "2:30", "5:30"),
        # Thursday
        ("BSIT-2A-WM", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Thu", "7:30", "10:30"),
        ("BSIT-2A-WM", "IT2217", "Systems Analysis and Design", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-2A-WM", "GEE2207", "Ethics", "Arianne Cagape", "Fri", "7:30", "10:30"),
        ("BSIT-2A-WM", "PATHFIT4", "Physical Education 4", "PE Instructor", "Fri", "1:00", "3:00"),
    ]

    # BSIT 2B-WM Schedule - OFFICIAL DATA
    print("\n📚 BSIT-2B-WM Schedule (Web/Mobile - OFFICIAL)")
    bsit_2b_wm_schedules = [
        # Monday
        ("BSIT-2B-WM", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Mon", "7:30", "10:30"),
        ("BSIT-2B-WM", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-2B-WM", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Tue", "9:00", "10:30"),
        ("BSIT-2B-WM", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-2B-WM", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Wed", "7:30", "10:30"),
        ("BSIT-2B-WM", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-2B-WM", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Thu", "9:00", "10:30"),
        ("BSIT-2B-WM", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-2B-WM", "IT2217", "Systems Analysis and Design", "Jenyfer Nardo", "Fri", "7:30", "10:30"),
        ("BSIT-2B-WM", "GEE2207", "Ethics", "Arianne Cagape", "Fri", "1:00", "2:30"),
        ("BSIT-2B-WM", "PATHFIT4", "Physical Education 4", "PE Instructor", "Fri", "2:30", "4:00"),
    ]

    # BSIT 2C-NT Schedule - OFFICIAL DATA (Non-Traditional Evening)
    print("\n📚 BSIT-2C-NT Schedule (Non-Traditional - OFFICIAL)")
    bsit_2c_nt_schedules = [
        # Monday
        ("BSIT-2C-NT", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Mon", "17:30", "20:30"),
        # Tuesday
        ("BSIT-2C-NT", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Tue", "17:30", "20:30"),
        # Wednesday
        ("BSIT-2C-NT", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Wed", "17:30", "19:00"),
        ("BSIT-2C-NT", "GEE2207", "Ethics", "Arianne Cagape", "Wed", "19:00", "20:30"),
        # Thursday
        ("BSIT-2C-NT", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Thu", "17:30", "20:30"),
        # Friday
        ("BSIT-2C-NT", "IT2217", "Systems Analysis and Design", "Jenyfer Nardo", "Fri", "17:30", "20:30"),
        # Saturday
        ("BSIT-2C-NT", "PATHFIT4", "Physical Education 4", "PE Instructor", "Sat", "7:30", "9:00"),
    ]

    # BSIT 2D-NT Schedule - OFFICIAL DATA (Non-Traditional Evening)
    print("\n📚 BSIT-2D-NT Schedule (Non-Traditional - OFFICIAL)")
    bsit_2d_nt_schedules = [
        # Monday
        ("BSIT-2D-NT", "IT2216", "Database Management Systems", "Jay-ar Baronda", "Mon", "17:30", "20:30"),
        # Tuesday
        ("BSIT-2D-NT", "IT2217", "Systems Analysis and Design", "Jenyfer Nardo", "Tue", "17:30", "20:30"),
        # Wednesday
        ("BSIT-2D-NT", "IT2214", "Object Oriented Programming", "Jenyfer Nardo", "Wed", "17:30", "20:30"),
        # Thursday
        ("BSIT-2D-NT", "GEE2205", "The Life and Works of Rizal", "Arianne Cagape", "Thu", "17:30", "19:00"),
        ("BSIT-2D-NT", "GEE2207", "Ethics", "Arianne Cagape", "Thu", "19:00", "20:30"),
        # Friday
        ("BSIT-2D-NT", "ITAS2218", "Web Development 1", "Jay-ar Baronda", "Fri", "17:30", "20:30"),
        # Saturday
        ("BSIT-2D-NT", "PATHFIT4", "Physical Education 4", "PE Instructor", "Sat", "7:30", "9:00"),
    ]

    # BSIT 3A-WM Schedule - OFFICIAL DATA (Web/Mobile)
    print("\n📚 BSIT-3A-WM Schedule (Web/Mobile - OFFICIAL)")
    bsit_3a_wm_schedules = [
        # Monday
        ("BSIT-3A-WM", "IT3225", "Software Engineering", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-3A-WM", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-3A-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Tue", "7:30", "10:30"),
        ("BSIT-3A-WM", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-3A-WM", "IT3225", "Software Engineering", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-3A-WM", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-3A-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Thu", "7:30", "10:30"),
        ("BSIT-3A-WM", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-3A-WM", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Fri", "7:30", "10:30"),
        ("BSIT-3A-WM", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Fri", "1:00", "3:00"),
    ]

    # BSIT 3A-NT Schedule - OFFICIAL DATA (Non-Traditional)
    print("\n📚 BSIT-3A-NT Schedule (Non-Traditional - OFFICIAL)")
    bsit_3a_nt_schedules = [
        # Monday
        ("BSIT-3A-NT", "IT3225", "Software Engineering", "Jenyfer Nardo", "Mon", "17:30", "20:30"),
        # Tuesday
        ("BSIT-3A-NT", "IT3226", "Information Systems", "Jenyfer Nardo", "Tue", "17:30", "20:30"),
        # Wednesday
        ("BSIT-3A-NT", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Wed", "17:30", "20:30"),
        # Thursday
        ("BSIT-3A-NT", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Thu", "17:30", "20:30"),
        # Friday
        ("BSIT-3A-NT", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Fri", "17:30", "20:30"),
        # Saturday
        ("BSIT-3A-NT", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Sat", "7:30", "10:30"),
    ]

    # BSIT 3B-WM Schedule - OFFICIAL DATA (Web/Mobile)
    print("\n📚 BSIT-3B-WM Schedule (Web/Mobile - OFFICIAL)")
    bsit_3b_wm_schedules = [
        # Monday
        ("BSIT-3B-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Mon", "7:30", "10:30"),
        ("BSIT-3B-WM", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Mon", "1:00", "3:00"),
        # Tuesday
        ("BSIT-3B-WM", "IT3225", "Software Engineering", "Jenyfer Nardo", "Tue", "7:30", "10:30"),
        ("BSIT-3B-WM", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Tue", "1:00", "4:00"),
        # Wednesday
        ("BSIT-3B-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Wed", "7:30", "10:30"),
        ("BSIT-3B-WM", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Wed", "1:00", "3:00"),
        # Thursday
        ("BSIT-3B-WM", "IT3225", "Software Engineering", "Jenyfer Nardo", "Thu", "7:30", "10:30"),
        ("BSIT-3B-WM", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Thu", "1:00", "4:00"),
        # Friday
        ("BSIT-3B-WM", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Fri", "7:30", "10:30"),
        ("BSIT-3B-WM", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Fri", "1:00", "4:00"),
    ]

    # BSIT 3B-NT Schedule - OFFICIAL DATA (Non-Traditional)
    print("\n📚 BSIT-3B-NT Schedule (Non-Traditional - OFFICIAL)")
    bsit_3b_nt_schedules = [
        # Monday
        ("BSIT-3B-NT", "IT3226", "Information Systems", "Jenyfer Nardo", "Mon", "17:30", "20:30"),
        # Tuesday
        ("BSIT-3B-NT", "IT3225", "Software Engineering", "Jenyfer Nardo", "Tue", "17:30", "20:30"),
        # Wednesday
        ("BSIT-3B-NT", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Wed", "17:30", "20:30"),
        # Thursday
        ("BSIT-3B-NT", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Thu", "17:30", "20:30"),
        # Friday
        ("BSIT-3B-NT", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Fri", "17:30", "20:30"),
        # Saturday
        ("BSIT-3B-NT", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Sat", "7:30", "10:30"),
    ]

    # BSIT 3C-WM Schedule - OFFICIAL DATA (Web/Mobile)
    print("\n📚 BSIT-3C-WM Schedule (Web/Mobile - OFFICIAL)")
    bsit_3c_wm_schedules = [
        # Monday
        ("BSIT-3C-WM", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Mon", "7:30", "10:30"),
        ("BSIT-3C-WM", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Mon", "1:00", "4:00"),
        # Tuesday
        ("BSIT-3C-WM", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Tue", "7:30", "9:00"),
        ("BSIT-3C-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Tue", "9:00", "12:00"),
        # Wednesday
        ("BSIT-3C-WM", "GEE2205", "Filipino sa Iba't-ibang Disiplina", "Filipino Faculty", "Wed", "7:30", "10:30"),
        ("BSIT-3C-WM", "ITAS3228", "Mobile Application Development", "Jay-ar Baronda", "Wed", "1:00", "4:00"),
        # Thursday
        ("BSIT-3C-WM", "ITPE3227", "Human Computer Interaction", "Jenyfer Nardo", "Thu", "7:30", "9:00"),
        ("BSIT-3C-WM", "IT3226", "Information Systems", "Jenyfer Nardo", "Thu", "9:00", "12:00"),
        # Friday
        ("BSIT-3C-WM", "IT3225", "Software Engineering", "Jenyfer Nardo", "Fri", "7:30", "10:30"),
        ("BSIT-3C-WM", "ITAS3229", "Advanced Web Development", "Jay-ar Baronda", "Fri", "1:00", "4:00"),
    ]

    # Combine all schedules
    all_schedules = (
        bsit_1a_schedules + bsit_1b_schedules + bsit_1c_schedules +
        bsit_2a_wm_schedules + bsit_2b_wm_schedules + bsit_2c_nt_schedules + bsit_2d_nt_schedules +
        bsit_3a_wm_schedules + bsit_3a_nt_schedules + bsit_3b_wm_schedules +
        bsit_3b_nt_schedules + bsit_3c_wm_schedules
    )

    return all_schedules

def main():
    """Main seeding function for OFFICIAL schedules"""
    app = create_app()

    with app.app_context():
        print("🏫 ISUFST CICT Grade Portal - OFFICIAL Schedule Seeder")
        print("📅 Academic Year: 2025-2026")
        print("📖 Semester: 2nd Semester")
        print("🎯 Source: Official ISUFST CICT Schedule Documents")
        print("=" * 60)

        try:
            # First ensure sections exist
            from seed_sections import seed_missing_sections
            seed_missing_sections()

            # Get all OFFICIAL schedule data
            schedules = seed_official_schedules()

            # Create all schedule entries
            created_count = 0
            for schedule_data in schedules:
                result = create_schedule_entry(*schedule_data)
                if result:
                    created_count += 1

            # Commit all changes
            db.session.commit()

            print(f"\n✅ Successfully created {created_count} OFFICIAL schedule entries")
            print("🎓 OFFICIAL schedule seeding completed!")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise

if __name__ == "__main__":
    main()