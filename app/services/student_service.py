from app.models.student import Student
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.schedule import Schedule
from app.extensions import db
from datetime import time, datetime, timezone


def get_student_profile(user_id: str) -> Student | None:
    """Fetch the Student profile by Supabase user UUID."""
    return Student.query.filter_by(user_id=user_id).first()


def get_current_semester_enrollments(student_id: int, semester: str, academic_year: str):
    """Return all Enrollment records for a student in a given semester/year."""
    return (
        Enrollment.query
        .filter_by(student_id=student_id, semester=semester, academic_year=academic_year)
        .join(Subject)
        .all()
    )


def get_all_enrollments(student_id: int):
    """Return all Enrollment records for a student (all semesters/years)."""
    return (
        Enrollment.query
        .filter_by(student_id=student_id)
        .join(Subject)
        .order_by(Enrollment.academic_year.desc(), Enrollment.semester)
        .all()
    )


def get_grades(student_id: int, semester: str | None = None, academic_year: str | None = None):
    """
    Return grades for a student, optionally filtered by semester/year.
    Each item is a Grade with eager-loaded enrollment and subject.
    """
    query = (
        db.session.query(Grade)
        .join(Enrollment, Grade.enrollment_id == Enrollment.id)
        .join(Subject, Enrollment.subject_id == Subject.id)
        .filter(Enrollment.student_id == student_id)
    )
    if semester:
        query = query.filter(Enrollment.semester == semester)
    if academic_year:
        query = query.filter(Enrollment.academic_year == academic_year)
    return query.all()


def get_schedule_matrix(student_id: int, semester: str | None = None, academic_year: str | None = None) -> dict:
    """
    Build a dict mapping day → list of schedule entries for the weekly matrix view.
    ONLY includes schedules for subjects the student is enrolled in.
    Returns: {'Mon': [...], 'Tue': [...], ..., 'Sun': [...]}
    """
    DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    matrix: dict = {day: [] for day in DAYS}

    student = db.session.get(Student, student_id)
    if not student:
        return matrix

    # Get subject IDs the student is enrolled in for this semester/year
    enrollment_query = db.session.query(Enrollment.subject_id).filter(
        Enrollment.student_id == student_id
    )
    if semester:
        enrollment_query = enrollment_query.filter(Enrollment.semester == semester)
    if academic_year:
        enrollment_query = enrollment_query.filter(Enrollment.academic_year == academic_year)

    enrolled_subject_ids = [e.subject_id for e in enrollment_query.all()]

    if not enrolled_subject_ids:
        return matrix

    # Query student-individual schedules + section-level schedules,
    # filtered by enrolled subjects only
    conditions = [Schedule.student_id == student_id]
    if student.section_id:
        conditions.append(Schedule.section_id == student.section_id)

    query = (
        Schedule.query
        .filter(db.or_(*conditions))
        .filter(Schedule.subject_id.in_(enrolled_subject_ids))
        .join(Subject, Schedule.subject_id == Subject.id)
    )
    if semester:
        query = query.filter(Schedule.semester == semester)
    if academic_year:
        query = query.filter(Schedule.academic_year == academic_year)

    for sched in query.all():
        matrix[sched.day_of_week].append({
            'time_start': sched.time_start.strftime('%H:%M'),
            'time_end': sched.time_end.strftime('%H:%M'),
            'subject_code': sched.subject.subject_code,
            'subject_title': sched.subject.subject_title,
            'room': sched.room or '',
        })

    # Sort each day's entries by start time
    for day in DAYS:
        matrix[day].sort(key=lambda x: x['time_start'])

    return matrix


def get_time_slots() -> list[str]:
    """Generate hourly time slots from 07:00 to 21:00 for the schedule matrix."""
    slots = []
    for hour in range(7, 21):
        start = f'{hour:02d}:00'
        end = f'{hour + 1:02d}:00'
        slots.append(f'{start}–{end}')
    return slots


def update_student_profile(user_id: str, data: dict) -> Student | None:
    """Update editable fields on a student's profile. Returns the updated Student or None."""
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return None
    allowed_fields = ['full_name', 'age', 'address', 'contact_number', 'gmail', 'year_level', 'gender']
    for field in allowed_fields:
        if field in data:
            setattr(student, field, data[field])
    student.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return student
