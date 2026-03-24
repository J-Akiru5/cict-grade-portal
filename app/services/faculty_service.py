from app.extensions import db
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.audit import GradeAudit
from app.models.schedule import Schedule
from datetime import datetime, timezone
import logging


def get_faculty_profile(user_id: str) -> Faculty | None:
    """Return the Faculty record linked to a user_id."""
    return Faculty.query.filter_by(user_id=user_id).first()


def get_faculty_subjects(faculty_id: int) -> list:
    """Return subjects assigned to this faculty member."""
    faculty = db.session.get(Faculty, faculty_id)
    return faculty.subjects if faculty else []


def is_subject_owned_by_faculty(faculty_id: int, subject_id: int) -> bool:
    """Verify a subject belongs to the faculty — used for scope enforcement."""
    faculty = db.session.get(Faculty, faculty_id)
    if not faculty:
        return False
    return any(s.id == subject_id for s in faculty.subjects)


def get_grades_for_subject(faculty_id: int, subject_id: int, semester: str, academic_year: str) -> list:
    """
    Return all enrollments (with grades) for a faculty's subject.
    Raises PermissionError if subject is not owned by faculty.
    """
    if not is_subject_owned_by_faculty(faculty_id, subject_id):
        raise PermissionError('Subject not assigned to this faculty member.')

    return (
        Enrollment.query
        .filter_by(subject_id=subject_id, semester=semester, academic_year=academic_year)
        .options(
            db.joinedload(Enrollment.student),
            db.joinedload(Enrollment.grade),
            db.joinedload(Enrollment.subject),
        )
        .join(Enrollment.student)
        .order_by(db.text('students.full_name'))
        .all()
    )


def update_grade(
    faculty_id: int,
    enrollment_id: int,
    grade_value: float | None,
    remarks: str | None,
    actor_user,
) -> Grade:
    """
    Encode or update a grade for a student's enrollment.
    Scope-enforced: faculty can only grade enrollments in their subjects.
    The GradeAudit record is created automatically by the SQLAlchemy event listener.
    """
    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        raise ValueError(f'Enrollment {enrollment_id} not found.')

    if not is_subject_owned_by_faculty(faculty_id, enrollment.subject_id):
        raise PermissionError('Cannot grade a subject not assigned to you.')

    grade = enrollment.grade
    if grade is None:
        grade = Grade(enrollment_id=enrollment_id)
        db.session.add(grade)

    grade.grade_value = grade_value
    grade.remarks = remarks
    grade.date_encoded = datetime.now(timezone.utc)
    grade.encoded_by_id = actor_user.id
    db.session.commit()
    return grade


def get_faculty_audit_log(faculty_user_id: str, limit: int = 200) -> list:
    """Audit entries where this faculty member was the actor."""
    return (
        GradeAudit.query
        .filter_by(actor_id=faculty_user_id)
        .options(
            db.joinedload(GradeAudit.target_student),
        )
        .order_by(GradeAudit.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_faculty_schedule(faculty_id: int, semester: str = None, academic_year: str = None, page: int = 1, per_page: int = 20):
    """Return paginated schedule entries owned by this faculty member."""
    q = (
        Schedule.query
        .filter_by(faculty_id=faculty_id)
        .options(db.joinedload(Schedule.subject))
        .order_by(Schedule.day_of_week, Schedule.time_start)
    )
    if semester:
        q = q.filter(Schedule.semester == semester)
    if academic_year:
        q = q.filter(Schedule.academic_year == academic_year)
    return q.paginate(page=page, per_page=per_page, error_out=False)


def get_faculty_sections(faculty_id: int, semester: str, academic_year: str) -> list:
    """Return distinct sections from the faculty's schedule, with student count and subject list."""
    from app.models.student import Student
    
    # Get schedules for this faculty that are linked to a section
    schedules = (
        Schedule.query
        .filter_by(faculty_id=faculty_id, semester=semester, academic_year=academic_year)
        .filter(Schedule.section_id.isnot(None))
        .options(db.joinedload(Schedule.subject), db.joinedload(Schedule.section_obj))
        .all()
    )

    sections_dict = {}
    for sched in schedules:
        sec_id = sched.section_id
        if sec_id not in sections_dict:
            # Count students officially belonging to this section
            student_count = db.session.query(db.func.count(Student.id)).filter_by(section_id=sec_id).scalar()
            
            sections_dict[sec_id] = {
                'id': sec_id,
                'name': sched.section_obj.display_name,
                'year_level': sched.section_obj.year_level,
                'student_count': student_count,
                'subjects': set()
            }
        
        sections_dict[sec_id]['subjects'].add(sched.subject.subject_code)

    # Convert sets to sorted lists for the template
    result = list(sections_dict.values())
    for r in result:
        r['subjects'] = sorted(list(r['subjects']))

    # Sort by year level, then section name
    return sorted(result, key=lambda x: (x['year_level'], x['name']))


def get_students_for_section(faculty_id: int, section_id: int, semester: str, academic_year: str) -> dict:
    """Return all students in the section, plus irregular students enrolled in faculty's subjects for this section."""
    from app.models.student import Student
    from app.models.section import Section
    
    # 1. Verify faculty handles this section
    handles_section = Schedule.query.filter_by(
        faculty_id=faculty_id, section_id=section_id, 
        semester=semester, academic_year=academic_year
    ).first() is not None
    
    if not handles_section:
        raise PermissionError('You do not handle this section for the current academic period.')

    # 2. Regular section students
    section_students = Student.query.filter_by(section_id=section_id).order_by(Student.full_name).all()
    
    # 3. Irregular students (students not in this section, but taking a subject the faculty teaches to this section)
    faculty_subjects_for_section = [
        sched.subject_id for sched in Schedule.query.filter_by(
            faculty_id=faculty_id, section_id=section_id, 
            semester=semester, academic_year=academic_year
        ).all()
    ]
    
    irregular_students = []
    if faculty_subjects_for_section:
        irregular_students = (
            Student.query
            .join(Enrollment, Enrollment.student_id == Student.id)
            .filter(
                Student.section_id.is_distinct_from(section_id),
                Enrollment.subject_id.in_(faculty_subjects_for_section),
                Enrollment.semester == semester,
                Enrollment.academic_year == academic_year
            )
            .order_by(Student.full_name)
            .distinct()
            .all()
        )
        
    return {
        "section_students": section_students,
        "irregular_students": irregular_students
    }



def add_faculty_schedule(
    faculty_id: int,
    subject_id: int,
    day_of_week: str,
    time_start,
    time_end,
    room: str,
    semester: str,
    academic_year: str,
) -> Schedule:
    """Add a faculty schedule entry. Validates subject ownership."""
    if not is_subject_owned_by_faculty(faculty_id, subject_id):
        raise PermissionError('Subject not assigned to this faculty member.')

    entry = Schedule(
        faculty_id=faculty_id,
        subject_id=subject_id,
        day_of_week=day_of_week,
        time_start=time_start,
        time_end=time_end,
        room=room,
        semester=semester,
        academic_year=academic_year,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def delete_faculty_schedule(faculty_id: int, schedule_id: int) -> None:
    """Delete a schedule entry, verifying ownership."""
    entry = db.session.get(Schedule, schedule_id)
    if not entry or entry.faculty_id != faculty_id:
        raise PermissionError('Schedule entry not found or not owned by you.')
    db.session.delete(entry)
    db.session.commit()


def update_faculty_schedule(
    faculty_id: int,
    schedule_id: int,
    subject_id: int = None,
    day_of_week: str = None,
    time_start=None,
    time_end=None,
    room: str = None,
    semester: str = None,
    academic_year: str = None,
) -> Schedule:
    """Edit a faculty schedule entry, verifying ownership."""
    entry = db.session.get(Schedule, schedule_id)
    if not entry or entry.faculty_id != faculty_id:
        raise PermissionError('Schedule entry not found or not owned by you.')
    if subject_id is not None:
        if not is_subject_owned_by_faculty(faculty_id, subject_id):
            raise PermissionError('Subject not assigned to this faculty member.')
        entry.subject_id = subject_id
    if day_of_week is not None:
        entry.day_of_week = day_of_week
    if time_start is not None:
        entry.time_start = time_start
    if time_end is not None:
        entry.time_end = time_end
    if room is not None:
        entry.room = room or None
    if semester is not None:
        entry.semester = semester
    if academic_year is not None:
        entry.academic_year = academic_year
    db.session.commit()
    return entry


# ─── Grade Release Control ─────────────────────────────────────────────

def release_grades_for_subject(
    faculty_id: int,
    subject_id: int,
    semester: str,
    academic_year: str,
    actor_user,
) -> int:
    """
    Mark all encoded grades for a subject as released (visible to students).
    Returns the count of grades released.
    Raises PermissionError if subject is not owned by faculty.
    """
    if not is_subject_owned_by_faculty(faculty_id, subject_id):
        raise PermissionError('Subject not assigned to this faculty member.')

    now = datetime.now(timezone.utc)

    # Find all grades for this subject that have a value and are not yet released
    grades_to_release = (
        Grade.query
        .join(Enrollment)
        .filter(
            Enrollment.subject_id == subject_id,
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None),
            Grade.is_released == False
        )
        .all()
    )

    count = 0
    for grade in grades_to_release:
        grade.is_released = True
        grade.released_at = now
        grade.released_by_id = actor_user.id
        count += 1

    if count > 0:
        db.session.commit()
        logging.info(f'Released {count} grades for subject {subject_id} by user {actor_user.id}')

    return count


def get_release_status_for_subject(
    faculty_id: int,
    subject_id: int,
    semester: str,
    academic_year: str,
) -> dict:
    """
    Get release status summary for a subject.
    Returns dict with counts of encoded, released, and pending grades.
    """
    if not is_subject_owned_by_faculty(faculty_id, subject_id):
        raise PermissionError('Subject not assigned to this faculty member.')

    total_enrollments = (
        Enrollment.query
        .filter_by(subject_id=subject_id, semester=semester, academic_year=academic_year)
        .count()
    )

    grades_with_value = (
        Grade.query
        .join(Enrollment)
        .filter(
            Enrollment.subject_id == subject_id,
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.grade_value.isnot(None)
        )
        .count()
    )

    grades_released = (
        Grade.query
        .join(Enrollment)
        .filter(
            Enrollment.subject_id == subject_id,
            Enrollment.semester == semester,
            Enrollment.academic_year == academic_year,
            Grade.is_released == True
        )
        .count()
    )

    return {
        'total_enrollments': total_enrollments,
        'grades_encoded': grades_with_value,
        'grades_released': grades_released,
        'grades_pending_release': grades_with_value - grades_released,
        'not_encoded': total_enrollments - grades_with_value,
    }

