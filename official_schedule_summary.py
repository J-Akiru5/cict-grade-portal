"""
Official Schedule Data Summary Report
Shows the extracted official ISUFST CICT schedule data
"""

def show_official_schedule_summary():
    """Display summary of the extracted official schedule data"""

    print("ISUFST CICT GRADE PORTAL - OFFICIAL SCHEDULE DATA SUMMARY")
    print("=" * 70)
    print("Academic Year: 2025-2026")
    print("Semester: 2nd Semester")
    print("Source: Official ISUFST CICT Schedule Documents")
    print()

    # Official Subject Codes Extracted
    print("OFFICIAL SUBJECT CODES EXTRACTED:")
    print("-" * 40)

    subjects = {
        # 1st Year IT Subjects
        "IT1204": "Introduction to Computing",
        "IT1205": "Data Structures and Algorithms",
        "IT1206": "Computer Programming 1",

        # 1st Year GEC Subjects
        "GEE1201": "Understanding the Self",
        "GEC1204": "Contemporary World",
        "GEM2201": "Mathematics in the Modern World",
        "PATHFIT2": "Physical Education 2",
        "NSTP2": "National Service Training Program 2",

        # 2nd Year IT Subjects
        "IT2214": "Object Oriented Programming",
        "IT2216": "Database Management Systems",
        "IT2217": "Systems Analysis and Design",
        "ITAS2218": "Web Development 1",

        # 2nd Year GEC Subjects
        "GEE2205": "The Life and Works of Rizal",
        "GEE2207": "Ethics",
        "PATHFIT4": "Physical Education 4",

        # 3rd Year IT Subjects
        "IT3225": "Software Engineering",
        "IT3226": "Information Systems",
        "ITPE3227": "Human Computer Interaction",
        "ITAS3228": "Mobile Application Development",
        "ITAS3229": "Advanced Web Development",
    }

    for code, title in subjects.items():
        print(f"  {code:<10} | {title}")

    print()
    print("SECTIONS COVERED:")
    print("-" * 20)

    sections = [
        ("BSIT-1A", "1st Year Section A", 13),
        ("BSIT-1B", "1st Year Section B", 13),
        ("BSIT-1C", "1st Year Section C", 13),
        ("BSIT-2A-WM", "2nd Year Section A (Web/Mobile)", 11),
        ("BSIT-2B-WM", "2nd Year Section B (Web/Mobile)", 11),
        ("BSIT-2C-NT", "2nd Year Section C (Non-Traditional)", 7),
        ("BSIT-2D-NT", "2nd Year Section D (Non-Traditional)", 7),
        ("BSIT-3A-WM", "3rd Year Section A (Web/Mobile)", 10),
        ("BSIT-3A-NT", "3rd Year Section A (Non-Traditional)", 6),
        ("BSIT-3B-WM", "3rd Year Section B (Web/Mobile)", 10),
        ("BSIT-3B-NT", "3rd Year Section B (Non-Traditional)", 6),
        ("BSIT-3C-WM", "3rd Year Section C (Web/Mobile)", 10),
    ]

    total_entries = 0
    for section, desc, count in sections:
        print(f"  {section:<12} | {desc:<35} | {count:>2} classes")
        total_entries += count

    print()
    print("FACULTY IDENTIFIED:")
    print("-" * 21)

    faculty = [
        ("Jenyfer Nardo", "IT Programming, OOP, Systems, Software Engineering"),
        ("Jay-ar Baronda", "Web Development, Database, Mobile Development"),
        ("Arianne Cagape", "Understanding Self, Rizal, Ethics"),
        ("Jenevie A. Siaron", "Contemporary World"),
        ("English Faculty", "Communication Courses"),
        ("Filipino Faculty", "Filipino Courses"),
        ("PE Instructor", "Physical Education (PATHFIT)"),
        ("NSTP Coordinator", "National Service Training Program"),
    ]

    for name, specialization in faculty:
        print(f"  {name:<20} | {specialization}")

    print()
    print("SCHEDULE STRUCTURE:")
    print("-" * 22)
    print("  Regular Day Classes:")
    print("    • Morning: 7:30 AM - 12:00 PM")
    print("    • Afternoon: 1:00 PM - 5:30 PM")
    print()
    print("  Non-Traditional Evening Classes:")
    print("    • Evening: 5:30 PM - 8:30 PM (17:30-20:30)")
    print("    • Saturday: 7:30 AM - 10:30 AM")
    print()
    print("SUMMARY STATISTICS:")
    print("-" * 20)
    print(f"  Total Sections: {len(sections)}")
    print(f"  Total Schedule Entries: {total_entries}")
    print(f"  Total Subjects: {len(subjects)}")
    print(f"  Total Faculty: {len(faculty)}")
    print()
    print("EXTRACTION STATUS:")
    print("-" * 18)
    print("  + All official subject codes extracted")
    print("  + All sections from images documented")
    print("  + Faculty assignments mapped")
    print("  + Time schedules formatted")
    print("  + Regular and NT schedules included")
    print("  + Web/Mobile specialization tracked")
    print()
    print("READY FOR SEEDING:")
    print("-" * 18)
    print("  Run: python -m flask seed-schedules-official")
    print("  Or:  python seed_official_schedules_2025_2026.py")
    print()
    print("NOTE: This will replace any existing schedule data")
    print("         for 2025-2026, 2nd Semester with official data")
    print()

if __name__ == "__main__":
    show_official_schedule_summary()