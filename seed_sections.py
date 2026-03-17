#!/usr/bin/env python3
"""
Section Seeder for CICT Grade Portal
Ensures all required sections exist for the 2025-2026 schedule seeding.
"""

from app.extensions import db
from app.models.section import Section
from datetime import datetime, timezone

def seed_missing_sections():
    """Create missing sections for the 2025-2026 semester"""

    required_sections = [
        # 1st Year
        ("BSIT", 1, "A"),
        ("BSIT", 1, "B"),
        ("BSIT", 1, "C"),

        # 2nd Year
        ("BSIT", 2, "A"),
        ("BSIT", 2, "B"),
        ("BSIT", 2, "C-NT"),  # Non-Traditional
        ("BSIT", 2, "D-NT"),  # Non-Traditional

        # 3rd Year
        ("BSIT", 3, "A-WM"),  # Web/Mobile
        ("BSIT", 3, "A-NT"),  # Non-Traditional
        ("BSIT", 3, "B-WM"),  # Web/Mobile
        ("BSIT", 3, "B-NT"),  # Non-Traditional
        ("BSIT", 3, "C-WM"),  # Web/Mobile
    ]

    print("🏫 Checking required sections...")
    created_count = 0

    for program, year_level, section_letter in required_sections:
        existing = Section.query.filter_by(
            program=program,
            year_level=year_level,
            section_letter=section_letter
        ).first()

        if not existing:
            section = Section(
                program=program,
                year_level=year_level,
                section_letter=section_letter
            )
            db.session.add(section)
            created_count += 1
            print(f"✓ Created section: {section.display_name}")
        else:
            print(f"• Section exists: {existing.display_name}")

    if created_count > 0:
        db.session.commit()
        print(f"\n✅ Created {created_count} new sections")
    else:
        print(f"\n✅ All required sections already exist")

    return created_count

if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        seed_missing_sections()