import csv
import io
import os
import logging
from datetime import datetime, timezone

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.audit import GradeAudit
from app.models.academic_settings import AcademicSettings


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_admin_supabase():
    """Return a Supabase client authenticated with the service role key."""
    from supabase import create_client
    url = os.environ['SUPABASE_URL']
    service_key = os.environ['SUPABASE_SERVICE_KEY']
    return create_client(url, service_key)


# ─── User Management ──────────────────────────────────────────────────────────

def get_all_users(search: str = None, page: int = 1, per_page: int = 25):
    q = User.query.order_by(User.created_at.desc())
    if search:
        q = q.filter(User.email.ilike(f'%{search}%'))
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_user(
    email: str,
    password: str,
    role: str,
    full_name: str = None,
    employee_id: str = None,
    student_id_num: str = None,
) -> User:
    """
    Create a user in Supabase (email confirmed) and the local DB.
    If role is 'faculty', also creates a Faculty profile.
    """
    client = _get_admin_supabase()
    response = client.auth.admin.create_user({
        'email': email,
        'password': password,
        'email_confirm': True,
        'user_metadata': {'role': role},
    })
    sb_user = response.user

    user = User(id=str(sb_user.id), email=email, role=role, is_active=True)
    db.session.add(user)

    if role == 'faculty' and full_name:
        faculty = Faculty(
            user_id=str(sb_user.id),
            full_name=full_name,
            employee_id=employee_id,
            department='CICT',
        )
        db.session.add(faculty)

    db.session.commit()
    return user


def update_user_role(user_id: str, new_role: str) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f'User {user_id} not found.')
    if new_role not in ('student', 'faculty', 'admin'):
        raise ValueError(f'Invalid role: {new_role}')
    user.role = new_role

    # Sync metadata in Supabase
    try:
        client = _get_admin_supabase()
        client.auth.admin.update_user_by_id(user_id, {'user_metadata': {'role': new_role}})
    except Exception as e:
        logging.warning(f'Failed to sync role to Supabase for user {user_id}: {e}')

    db.session.commit()
    return user


def toggle_user_active(user_id: str) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f'User {user_id} not found.')
    user.is_active = not user.is_active
    db.session.commit()
    return user


def get_all_faculty(search: str = None, page: int = 1, per_page: int = 25):
    q = Faculty.query.join(User).order_by(Faculty.full_name)
    if search:
        q = q.filter(
            db.or_(
                Faculty.full_name.ilike(f'%{search}%'),
                Faculty.employee_id.ilike(f'%{search}%'),
            )
        )
    return q.paginate(page=page, per_page=per_page, error_out=False)


def assign_subject_to_faculty(faculty_id: int, subject_id: int) -> None:
    faculty = db.session.get(Faculty, faculty_id)
    subject = db.session.get(Subject, subject_id)
    if not faculty or not subject:
        raise ValueError('Faculty or Subject not found.')
    if subject not in faculty.subjects:
        faculty.subjects.append(subject)
        db.session.commit()


def remove_subject_from_faculty(faculty_id: int, subject_id: int) -> None:
    faculty = db.session.get(Faculty, faculty_id)
    subject = db.session.get(Subject, subject_id)
    if not faculty or not subject:
        raise ValueError('Faculty or Subject not found.')
    if subject in faculty.subjects:
        faculty.subjects.remove(subject)
        db.session.commit()


# ─── Student Management ───────────────────────────────────────────────────────

def get_all_students(search: str = None, page: int = 1, per_page: int = 25):
    q = Student.query.order_by(Student.full_name)
    if search:
        q = q.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%'),
                Student.section.ilike(f'%{search}%'),
            )
        )
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_student(
    user_id: str,
    student_id: str,
    full_name: str,
    section: str = None,
    year_level: int = None,
    curriculum_year: str = None,
    age: int = None,
    address: str = None,
    contact_number: str = None,
    gmail: str = None,
) -> Student:
    student = Student(
        user_id=user_id,
        student_id=student_id,
        full_name=full_name,
        section=section,
        year_level=year_level,
        curriculum_year=curriculum_year,
        age=age,
        address=address,
        contact_number=contact_number,
        gmail=gmail,
    )
    db.session.add(student)
    db.session.commit()
    return student


def update_student(student_db_id: int, **data) -> Student:
    student = db.session.get(Student, student_db_id)
    if not student:
        raise ValueError(f'Student {student_db_id} not found.')
    allowed = {
        'full_name', 'section', 'year_level', 'curriculum_year',
        'age', 'address', 'contact_number', 'gmail', 'student_id',
    }
    for key, val in data.items():
        if key in allowed:
            setattr(student, key, val)
    db.session.commit()
    return student


def delete_student(student_db_id: int) -> None:
    student = db.session.get(Student, student_db_id)
    if not student:
        raise ValueError(f'Student {student_db_id} not found.')
    db.session.delete(student)
    db.session.commit()


def create_student_with_account(
    email: str,
    password: str,
    student_id: str,
    full_name: str,
    section: str = None,
    year_level: int = None,
    curriculum_year: str = None,
    age: int = None,
    address: str = None,
    contact_number: str = None,
    gmail: str = None,
) -> Student:
    """Create a Supabase auth account + local User + Student profile in one step."""
    client = _get_admin_supabase()
    response = client.auth.admin.create_user({
        'email': email,
        'password': password,
        'email_confirm': True,
        'user_metadata': {'role': 'student'},
    })
    sb_user = response.user

    user = User(id=str(sb_user.id), email=email, role='student', is_active=True)
    db.session.add(user)

    student = Student(
        user_id=str(sb_user.id),
        student_id=student_id,
        full_name=full_name,
        section=section,
        year_level=year_level,
        curriculum_year=curriculum_year,
        age=age,
        address=address,
        contact_number=contact_number,
        gmail=gmail,
    )
    db.session.add(student)
    db.session.commit()
    return student


# ─── Subject Management ───────────────────────────────────────────────────────

def get_all_subjects(search: str = None, page: int = 1, per_page: int = 25):
    q = Subject.query.order_by(Subject.subject_code)
    if search:
        q = q.filter(
            db.or_(
                Subject.subject_code.ilike(f'%{search}%'),
                Subject.subject_title.ilike(f'%{search}%'),
            )
        )
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_subject(code: str, title: str, units: int, instructor_name: str = None, department: str = 'CICT') -> Subject:
    subject = Subject(
        subject_code=code.strip().upper(),
        subject_title=title.strip(),
        units=units,
        instructor_name=instructor_name,
        department=department,
    )
    db.session.add(subject)
    db.session.commit()
    return subject


def update_subject(subject_id: int, **data) -> Subject:
    subject = db.session.get(Subject, subject_id)
    if not subject:
        raise ValueError(f'Subject {subject_id} not found.')
    allowed = {'subject_code', 'subject_title', 'units', 'instructor_name', 'department'}
    for key, val in data.items():
        if key in allowed:
            setattr(subject, key, val)
    db.session.commit()
    return subject


def delete_subject(subject_id: int) -> None:
    subject = db.session.get(Subject, subject_id)
    if not subject:
        raise ValueError(f'Subject {subject_id} not found.')
    db.session.delete(subject)
    db.session.commit()


# ─── Enrollment Management ────────────────────────────────────────────────────

def get_all_enrollments(search: str = None, semester: str = None, academic_year: str = None, page: int = 1, per_page: int = 25):
    q = (
        Enrollment.query
        .join(Student, Enrollment.student_id == Student.id)
        .join(Subject, Enrollment.subject_id == Subject.id)
        .options(db.contains_eager(Enrollment.student), db.contains_eager(Enrollment.subject))
        .order_by(Student.full_name)
    )
    if semester:
        q = q.filter(Enrollment.semester == semester)
    if academic_year:
        q = q.filter(Enrollment.academic_year == academic_year)
    if search:
        q = q.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%'),
                Subject.subject_code.ilike(f'%{search}%'),
            )
        )
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_enrollment(student_db_id: int, subject_id: int, semester: str, academic_year: str) -> Enrollment:
    enrollment = Enrollment(
        student_id=student_db_id,
        subject_id=subject_id,
        semester=semester,
        academic_year=academic_year,
    )
    db.session.add(enrollment)
    db.session.commit()
    return enrollment


def delete_enrollment(enrollment_id: int) -> None:
    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        raise ValueError(f'Enrollment {enrollment_id} not found.')
    db.session.delete(enrollment)
    db.session.commit()


# ─── Grade CSV Import ─────────────────────────────────────────────────────────

VALID_GRADES = {1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 5.0}
VALID_REMARKS = {'INC', 'DRP'}


def import_grades_from_csv(
    file_stream,
    semester: str,
    academic_year: str,
    actor_user,
) -> dict:
    """
    Parse and import grades from a CSV file.
    Expected columns: student_id, subject_code, grade
    'grade' can be a float (1.0–5.0) or 'INC'/'DRP'.

    Returns: {'imported': N, 'skipped': M, 'errors': [...]}
    All-or-nothing: if there are ANY errors, no grades are written.
    """
    text = io.TextIOWrapper(file_stream, encoding='utf-8-sig')
    reader = csv.DictReader(text)

    required_cols = {'student_id', 'subject_code', 'grade'}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        return {
            'imported': 0,
            'skipped': 0,
            'errors': [f'CSV must have columns: {", ".join(sorted(required_cols))}. '
                       f'Got: {", ".join(reader.fieldnames or [])}'],
        }

    rows = list(reader)
    errors = []
    pending = []   # list of (enrollment, grade_value, remarks)

    for i, row in enumerate(rows, start=2):   # row 1 is header
        sid = (row.get('student_id') or '').strip()
        code = (row.get('subject_code') or '').strip().upper()
        raw_grade = (row.get('grade') or '').strip().upper()

        if not sid or not code or not raw_grade:
            errors.append(f'Row {i}: missing value(s).')
            continue

        student = Student.query.filter_by(student_id=sid).first()
        if not student:
            errors.append(f'Row {i}: student_id "{sid}" not found.')
            continue

        subject = Subject.query.filter_by(subject_code=code).first()
        if not subject:
            errors.append(f'Row {i}: subject_code "{code}" not found.')
            continue

        enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            subject_id=subject.id,
            semester=semester,
            academic_year=academic_year,
        ).first()
        if not enrollment:
            errors.append(
                f'Row {i}: no enrollment for {sid} in {code} '
                f'({semester} {academic_year}).'
            )
            continue

        # Parse grade
        if raw_grade in VALID_REMARKS:
            grade_value, remarks = None, raw_grade
        else:
            try:
                gv = round(float(raw_grade), 2)
                if gv not in VALID_GRADES:
                    errors.append(
                        f'Row {i}: "{raw_grade}" is not a valid grade value '
                        f'(allowed: {sorted(VALID_GRADES)} or INC/DRP).'
                    )
                    continue
                grade_value, remarks = gv, None
            except ValueError:
                errors.append(f'Row {i}: "{raw_grade}" is not a valid grade.')
                continue

        pending.append((enrollment, grade_value, remarks))

    if errors:
        return {'imported': 0, 'skipped': 0, 'errors': errors}

    # Apply all grades
    now = datetime.now(timezone.utc)
    for enrollment, grade_value, remarks in pending:
        grade = enrollment.grade
        if grade is None:
            grade = Grade(enrollment_id=enrollment.id)
            db.session.add(grade)
        grade.grade_value = grade_value
        grade.remarks = remarks
        grade.date_encoded = now
        grade.encoded_by_id = actor_user.id

    db.session.commit()
    return {'imported': len(pending), 'skipped': 0, 'errors': []}


# ─── Audit Log ────────────────────────────────────────────────────────────────

def get_full_audit_log(search: str = None, page: int = 1, per_page: int = 50):
    q = (
        GradeAudit.query
        .options(
            db.joinedload(GradeAudit.actor),
            db.joinedload(GradeAudit.target_student),
            db.joinedload(GradeAudit.grade)
               .joinedload(Grade.enrollment)
               .joinedload(Enrollment.subject),
        )
        .order_by(GradeAudit.timestamp.desc())
    )
    if search:
        q = (
            q.outerjoin(GradeAudit.actor)
             .outerjoin(GradeAudit.target_student)
             .filter(
                 db.or_(
                     User.email.ilike(f'%{search}%'),
                     Student.full_name.ilike(f'%{search}%'),
                     Student.student_id.ilike(f'%{search}%'),
                 )
             )
        )
    return q.paginate(page=page, per_page=per_page, error_out=False)


# ─── Academic Settings ────────────────────────────────────────────────────────

def get_academic_settings() -> AcademicSettings:
    return AcademicSettings.get_current()


def update_academic_settings(semester: str, year: str, actor_user) -> AcademicSettings:
    settings = AcademicSettings.get_current()
    settings.current_semester = semester
    settings.current_year = year
    settings.updated_by_id = actor_user.id
    db.session.commit()
    return settings
