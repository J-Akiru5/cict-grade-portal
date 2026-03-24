"""
Analytics service for dashboard charts and statistics.
Provides data aggregation for grade distribution, enrollment trends, and academic performance.
"""

from app.extensions import db
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.subject import Subject
from app.models.section import Section
from app.models.faculty import Faculty
from sqlalchemy import func, case


def get_grade_distribution(semester: str, academic_year: str) -> dict:
    """
    Get grade distribution for charting.
    Returns a dict with grade values as keys and counts as values.
    """
    results = (
        db.session.query(
            Grade.grade_value,
            func.count(Grade.id).label('count')
        )
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None)
        )
        .group_by(Grade.grade_value)
        .order_by(Grade.grade_value)
        .all()
    )

    # Format for chart display
    distribution = {}
    for grade_val, count in results:
        label = f'{grade_val:.2f}' if grade_val else 'N/A'
        distribution[label] = count

    return distribution


def get_grade_remarks_distribution(semester: str, academic_year: str) -> dict:
    """
    Get distribution of grade remarks (PASSED, FAILED, INC, DRP, NOT YET ENCODED).
    """
    # Count graded enrollments with computed remarks
    passed = (
        db.session.query(func.count(Grade.id))
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None),
            Grade.grade_value <= 3.0,
            Grade.remarks.notin_(['INC', 'DRP'])
        )
        .scalar() or 0
    )

    failed = (
        db.session.query(func.count(Grade.id))
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None),
            Grade.grade_value > 3.0,
            Grade.remarks.notin_(['INC', 'DRP'])
        )
        .scalar() or 0
    )

    inc = (
        db.session.query(func.count(Grade.id))
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.remarks == 'INC'
        )
        .scalar() or 0
    )

    drp = (
        db.session.query(func.count(Grade.id))
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.remarks == 'DRP'
        )
        .scalar() or 0
    )

    # Count enrollments without grades
    not_encoded = (
        db.session.query(func.count(Enrollment.id))
        .outerjoin(Grade)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.id.is_(None)
        )
        .scalar() or 0
    )

    return {
        'Passed': passed,
        'Failed': failed,
        'Incomplete': inc,
        'Dropped': drp,
        'Not Encoded': not_encoded,
    }


def get_enrollment_by_section(semester: str, academic_year: str) -> dict:
    """
    Get enrollment counts grouped by section.
    """
    results = (
        db.session.query(
            Section.program,
            Section.year_level,
            Section.section_letter,
            func.count(Enrollment.id).label('count')
        )
        .join(Student, Student.section_id == Section.id)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year
        )
        .group_by(Section.program, Section.year_level, Section.section_letter)
        .order_by(Section.program, Section.year_level, Section.section_letter)
        .all()
    )

    return {
        f'{prog}-{year}{letter}': count
        for prog, year, letter, count in results
    }


def get_enrollment_by_year_level(semester: str, academic_year: str) -> dict:
    """
    Get enrollment counts grouped by year level.
    """
    results = (
        db.session.query(
            Student.year_level,
            func.count(func.distinct(Enrollment.student_id)).label('count')
        )
        .join(Enrollment, Enrollment.student_id == Student.id)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Student.year_level.isnot(None)
        )
        .group_by(Student.year_level)
        .order_by(Student.year_level)
        .all()
    )

    year_labels = {1: '1st Year', 2: '2nd Year', 3: '3rd Year', 4: '4th Year'}
    return {
        year_labels.get(year, f'Year {year}'): count
        for year, count in results
    }


def get_subject_enrollment_counts(semester: str, academic_year: str, limit: int = 10) -> dict:
    """
    Get top N subjects by enrollment count.
    """
    results = (
        db.session.query(
            Subject.subject_code,
            func.count(Enrollment.id).label('count')
        )
        .join(Enrollment, Enrollment.subject_id == Subject.id)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year
        )
        .group_by(Subject.id, Subject.subject_code)
        .order_by(func.count(Enrollment.id).desc())
        .limit(limit)
        .all()
    )

    return {code: count for code, count in results}


def get_dashboard_summary(semester: str, academic_year: str) -> dict:
    """
    Get comprehensive dashboard summary statistics.
    """
    # Total enrolled students (unique) this semester
    enrolled_students = (
        db.session.query(func.count(func.distinct(Enrollment.student_id)))
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year
        )
        .scalar() or 0
    )

    # Total enrollments (student-subject pairs)
    total_enrollments = (
        db.session.query(func.count(Enrollment.id))
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year
        )
        .scalar() or 0
    )

    # Grades encoded vs pending
    grades_encoded = (
        db.session.query(func.count(Grade.id))
        .join(Enrollment)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None)
        )
        .scalar() or 0
    )

    grades_pending = total_enrollments - grades_encoded

    # Calculate encoding progress percentage
    encoding_progress = round((grades_encoded / total_enrollments * 100), 1) if total_enrollments > 0 else 0

    # Active subjects this semester
    active_subjects = (
        db.session.query(func.count(func.distinct(Enrollment.subject_id)))
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year
        )
        .scalar() or 0
    )

    # Total students in system
    total_students = db.session.query(func.count(Student.id)).scalar() or 0

    # Total subjects in system
    total_subjects = db.session.query(func.count(Subject.id)).scalar() or 0

    # Total faculty
    total_faculty = db.session.query(func.count(Faculty.id)).scalar() or 0

    # Total sections
    total_sections = db.session.query(func.count(Section.id)).scalar() or 0

    return {
        'enrolled_students': enrolled_students,
        'total_enrollments': total_enrollments,
        'grades_encoded': grades_encoded,
        'grades_pending': grades_pending,
        'encoding_progress': encoding_progress,
        'active_subjects': active_subjects,
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_faculty': total_faculty,
        'total_sections': total_sections,
    }


def get_gwa_distribution(semester: str, academic_year: str) -> dict:
    """
    Get GWA distribution for students (binned into ranges).
    """
    from app.services.gwa_service import compute_gwa

    # Get all students with grades this semester
    students_with_grades = (
        db.session.query(Student.id)
        .join(Enrollment)
        .join(Grade)
        .filter(
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None)
        )
        .distinct()
        .all()
    )

    # Calculate GWA for each student
    gwa_bins = {
        '1.00-1.25 (Excellent)': 0,
        '1.50-1.75 (Superior)': 0,
        '2.00-2.25 (Very Good)': 0,
        '2.50-2.75 (Good)': 0,
        '3.00 (Satisfactory)': 0,
        '5.00 (Failed)': 0,
    }

    for (student_id,) in students_with_grades:
        # Get student grades for this semester
        grades = (
            db.session.query(Grade)
            .join(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.semester == semester,
                Enrollment.academic_year == academic_year
            )
            .all()
        )

        gwa = compute_gwa(grades)
        if gwa is None:
            continue

        if gwa <= 1.25:
            gwa_bins['1.00-1.25 (Excellent)'] += 1
        elif gwa <= 1.75:
            gwa_bins['1.50-1.75 (Superior)'] += 1
        elif gwa <= 2.25:
            gwa_bins['2.00-2.25 (Very Good)'] += 1
        elif gwa <= 2.75:
            gwa_bins['2.50-2.75 (Good)'] += 1
        elif gwa <= 3.0:
            gwa_bins['3.00 (Satisfactory)'] += 1
        else:
            gwa_bins['5.00 (Failed)'] += 1

    return gwa_bins


def get_recent_grade_activity(limit: int = 10) -> list:
    """
    Get recent grade encoding activity for audit display.
    """
    from app.models.audit import GradeAudit
    from app.models.user import User

    recent = (
        db.session.query(GradeAudit, User, Student, Subject)
        .outerjoin(User, GradeAudit.actor_id == User.id)
        .outerjoin(Student, GradeAudit.target_student_id == Student.id)
        .outerjoin(Grade, GradeAudit.grade_id == Grade.id)
        .outerjoin(Enrollment, Grade.enrollment_id == Enrollment.id)
        .outerjoin(Subject, Enrollment.subject_id == Subject.id)
        .order_by(GradeAudit.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            'audit': audit,
            'actor': user,
            'student': student,
            'subject': subject,
        }
        for audit, user, student, subject in recent
    ]
