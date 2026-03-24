import csv
import io
import os
import logging
import secrets
import string
from datetime import datetime, timezone
from flask import current_app

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.section import Section
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.audit import GradeAudit
from app.models.academic_settings import AcademicSettings
from app.models.schedule import Schedule
from app.services import email_service


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_admin_supabase():
    """Return a Supabase client authenticated with the service role key."""
    from supabase import create_client
    url = os.environ['SUPABASE_URL']
    service_key = os.environ['SUPABASE_SERVICE_KEY']
    return create_client(url, service_key)


# ─── User Management ──────────────────────────────────────────────────────────

def get_all_users(search: str = None, role: str = None, is_active: bool = None, page: int = 1, per_page: int = 25):
    q = User.query.order_by(User.created_at.desc())
    if search:
        q = q.filter(User.email.ilike(f'%{search}%'))
    if role:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
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

    # Auto-create Faculty profile when role is elevated to faculty/admin
    if new_role in ('faculty', 'admin') and not user.faculty_profile:
        name = None
        if user.student_profile:
            name = user.student_profile.full_name
        if not name:
            name = user.email.split('@')[0]
        faculty = Faculty(user_id=user.id, full_name=name, department='CICT')
        db.session.add(faculty)

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


def update_user(
    user_id: str,
    email: str = None,
    password: str = None,
    full_name: str = None,
    employee_id: str = None,
    department: str = None,
) -> User:
    """Update a user's email/password (via Supabase) and their faculty profile fields."""
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(f'User {user_id} not found.')

    updates = {}
    if email and email != user.email:
        updates['email'] = email
    if password:
        updates['password'] = password

    if updates:
        try:
            client = _get_admin_supabase()
            client.auth.admin.update_user_by_id(user_id, updates)
        except Exception as e:
            raise ValueError(f'Failed to update credentials in Supabase: {e}')
        
        if email and email != user.email:
            user.email = email

    if user.faculty_profile:
        if full_name:
            user.faculty_profile.full_name = full_name
        if employee_id is not None:
            user.faculty_profile.employee_id = employee_id or None
        if department:
            user.faculty_profile.department = department

    db.session.commit()
    return user


def send_account_approved_email(user: User, temporary_password: str | None = None) -> bool:
    """Notify the user that their account can now be used."""
    base_url = (current_app.config.get('APP_BASE_URL') or '').rstrip('/')
    login_url = f'{base_url}/auth/login' if base_url else '/auth/login'

    subject = 'Your CICT Grade Portal account is approved'
    html_lines = [
        '<p>Hello,</p>',
        '<p>Your CICT Grade Portal account has been approved and is now active.</p>',
        f'<p>You can sign in here: <a href="{login_url}">{login_url}</a></p>',
    ]
    text_lines = [
        'Hello,',
        'Your CICT Grade Portal account has been approved and is now active.',
        f'Sign in here: {login_url}',
    ]

    if temporary_password:
        html_lines.append(f'<p>Temporary password: <strong>{temporary_password}</strong></p>')
        text_lines.append(f'Temporary password: {temporary_password}')

    html_lines.append('<p>If you did not request this account, please contact the administrator.</p>')
    text_lines.append('If you did not request this account, please contact the administrator.')

    return email_service.send_resend_email(
        to_email=user.email,
        subject=subject,
        html='\n'.join(html_lines),
        text='\n'.join(text_lines),
    )


def _generate_temporary_password(length: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_-+='  # noqa: S105
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in '!@#$%^&*()_-+=' for c in password)
        ):
            return password


def create_account_for_student_profile(student_db_id: int) -> tuple[Student, User, str | None]:
    """Create or attach a login account for an existing profile-only student."""
    student = db.session.get(Student, student_db_id)
    if not student:
        raise ValueError(f'Student {student_db_id} not found.')
    if student.user_id:
        raise ValueError('This student profile already has a linked account.')

    email = (student.gmail or '').strip().lower()
    if not email:
        raise ValueError('Student email is missing. Add Gmail in the student profile first.')

    existing_user = User.query.filter_by(email=email).first()
    temp_password = None

    if existing_user:
        # Existing account: link it if not already tied to another student profile.
        if existing_user.role != 'student':
            raise ValueError('This email is already used by a non-student account.')
        if existing_user.student_profile and existing_user.student_profile.id != student.id:
            other = existing_user.student_profile
            raise ValueError(
                f'This email is already linked to another student: {other.full_name} '
                f'({other.student_id}). Use the merge function to combine these records.'
            )
        existing_user.role = 'student'
        existing_user.is_active = True
        student.user_id = existing_user.id
        user = existing_user
    else:
        # Check if another student profile has this gmail (without linked account)
        duplicate_profile = Student.query.filter(
            Student.id != student_db_id,
            db.func.lower(Student.gmail) == email
        ).first()
        if duplicate_profile:
            raise ValueError(
                f'Gmail "{email}" is also used by another student profile: '
                f'{duplicate_profile.full_name} ({duplicate_profile.student_id}). '
                f'Please merge profiles first using the merge function below.'
            )

        temp_password = _generate_temporary_password()
        client = _get_admin_supabase()
        response = client.auth.admin.create_user({
            'email': email,
            'password': temp_password,
            'email_confirm': True,
            'user_metadata': {'role': 'student'},
        })
        sb_user = response.user

        user = User(id=str(sb_user.id), email=email, role='student', is_active=True)
        db.session.add(user)
        student.user_id = str(sb_user.id)

    db.session.commit()
    return student, user, temp_password


def get_all_faculty(search: str = None, department: str = None, page: int = 1, per_page: int = 25):
    q = Faculty.query.join(User).order_by(Faculty.full_name)
    if search:
        q = q.filter(
            db.or_(
                Faculty.full_name.ilike(f'%{search}%'),
                Faculty.employee_id.ilike(f'%{search}%'),
            )
        )
    if department:
        q = q.filter(Faculty.department == department)
    return q.paginate(page=page, per_page=per_page, error_out=False)


def update_faculty(
    faculty_id: int,
    full_name: str = None,
    employee_id: str = None,
    department: str = None,
) -> Faculty:
    faculty = db.session.get(Faculty, faculty_id)
    if not faculty:
        raise ValueError(f'Faculty {faculty_id} not found.')
    if full_name:
        faculty.full_name = full_name
    if employee_id is not None:
        faculty.employee_id = employee_id or None
    if department:
        faculty.department = department
    db.session.commit()
    return faculty


def delete_faculty_profile(faculty_id: int) -> None:
    """Remove the Faculty profile record without deleting the linked User account."""
    faculty = db.session.get(Faculty, faculty_id)
    if not faculty:
        raise ValueError(f'Faculty {faculty_id} not found.')
    db.session.delete(faculty)
    db.session.commit()


def assign_subject_to_faculty(faculty_id: int, subject_id: int) -> None:
    faculty = db.session.get(Faculty, faculty_id)
    subject = db.session.get(Subject, subject_id)
    if not faculty or not subject:
        raise ValueError('Faculty or Subject not found.')
    if subject not in faculty.subjects:
        faculty.subjects.append(subject)
        # Sync instructor_name to first assigned faculty
        if not subject.instructor_name:
            subject.instructor_name = faculty.full_name
        db.session.commit()


def remove_subject_from_faculty(faculty_id: int, subject_id: int) -> None:
    faculty = db.session.get(Faculty, faculty_id)
    subject = db.session.get(Subject, subject_id)
    if not faculty or not subject:
        raise ValueError('Faculty or Subject not found.')
    if subject in faculty.subjects:
        faculty.subjects.remove(subject)
        # Update instructor_name to next remaining assigned faculty, or clear it
        if subject.instructor_name == faculty.full_name:
            remaining = [f for f in subject.faculty if f.id != faculty_id]
            subject.instructor_name = remaining[0].full_name if remaining else None
        db.session.commit()


# ─── Student Management ───────────────────────────────────────────────────────

def get_all_students(search: str = None, section_id: int = None, year_level: int = None, page: int = 1, per_page: int = 25):
    q = Student.query.order_by(Student.full_name)
    if search:
        q = q.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%'),
                Student.section.ilike(f'%{search}%'),
            )
        )
    if section_id:
        q = q.filter(Student.section_id == section_id)
    if year_level:
        q = q.filter(Student.year_level == year_level)
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_student(
    user_id: str | None,
    student_id: str,
    full_name: str,
    section: str = None,
    year_level: int = None,
    curriculum_year: str = None,
    age: int = None,
    address: str = None,
    contact_number: str = None,
    gmail: str = None,
    gender: str = None,
) -> Student:
    # Pre-check: student_id must be unique
    existing_by_id = Student.query.filter_by(student_id=student_id).first()
    if existing_by_id:
        raise ValueError(f'Student ID "{student_id}" already exists (belongs to {existing_by_id.full_name}).')

    # Pre-check: gmail must be unique (if provided)
    if gmail:
        gmail_clean = gmail.strip().lower()
        existing_by_email = Student.query.filter(
            db.func.lower(Student.gmail) == gmail_clean
        ).first()
        if existing_by_email:
            raise ValueError(
                f'Gmail "{gmail}" is already used by student {existing_by_email.full_name} '
                f'({existing_by_email.student_id}). Consider merging records.'
            )

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
        gender=gender,
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
        'age', 'address', 'contact_number', 'gmail', 'student_id', 'gender',
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


def merge_student_profiles(primary_id: int, secondary_id: int) -> Student:
    """
    Merge two student profiles into one.
    The primary profile is kept; data from secondary fills in blanks.
    Enrollments, grades, and schedules are transferred to primary.
    Secondary profile is then deleted.
    """
    from app.models.enrollment import Enrollment
    from app.models.schedule import Schedule

    primary = db.session.get(Student, primary_id)
    secondary = db.session.get(Student, secondary_id)

    if not primary or not secondary:
        raise ValueError('One or both student profiles not found.')
    if primary_id == secondary_id:
        raise ValueError('Cannot merge a profile with itself.')

    # Transfer user account if secondary has one and primary doesn't
    if secondary.user_id and not primary.user_id:
        primary.user_id = secondary.user_id
        secondary.user_id = None

    # Fill in blank fields from secondary
    fields_to_merge = [
        'full_name', 'age', 'address', 'contact_number', 'gmail',
        'gender', 'section', 'section_id', 'year_level', 'curriculum_year'
    ]
    for field in fields_to_merge:
        if not getattr(primary, field) and getattr(secondary, field):
            setattr(primary, field, getattr(secondary, field))

    # Transfer enrollments
    Enrollment.query.filter_by(student_id=secondary_id).update(
        {'student_id': primary_id}, synchronize_session=False
    )

    # Transfer schedules
    Schedule.query.filter_by(student_id=secondary_id).update(
        {'student_id': primary_id}, synchronize_session=False
    )

    # Delete secondary profile
    db.session.delete(secondary)
    db.session.commit()

    return primary


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

def get_all_subjects(search: str = None, department: str = None, page: int = 1, per_page: int = 25):
    q = Subject.query.order_by(Subject.subject_code)
    if search:
        q = q.filter(
            db.or_(
                Subject.subject_code.ilike(f'%{search}%'),
                Subject.subject_title.ilike(f'%{search}%'),
            )
        )
    if department:
        q = q.filter(Subject.department == department)
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

def get_full_audit_log(search: str = None, actor_role: str = None, page: int = 1, per_page: int = 50):
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
    if search or actor_role:
        q = q.outerjoin(GradeAudit.actor)
        if search:
            q = q.outerjoin(GradeAudit.target_student).filter(
                db.or_(
                    User.email.ilike(f'%{search}%'),
                    Student.full_name.ilike(f'%{search}%'),
                    Student.student_id.ilike(f'%{search}%'),
                )
            )
        if actor_role:
            q = q.filter(User.role == actor_role)
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


# ─── Section Management ───────────────────────────────────────────────────────

def get_all_sections(search: str = None, program: str = None, year_level: int = None, page: int = 1, per_page: int = 25):
    q = Section.query.order_by(Section.program, Section.year_level, Section.section_letter)
    if search:
        q = q.filter(
            db.or_(
                Section.program.ilike(f'%{search}%'),
                Section.section_letter.ilike(f'%{search}%'),
            )
        )
    if program:
        q = q.filter(Section.program == program)
    if year_level:
        q = q.filter(Section.year_level == year_level)
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_section(program: str, year_level: int, section_letter: str) -> Section:
    letter = section_letter.strip().upper()
    section = Section(
        program=program.strip().upper(),
        year_level=year_level,
        section_letter=letter,
    )
    db.session.add(section)
    db.session.commit()
    return section


def update_section(section_id: int, program: str = None, year_level: int = None, section_letter: str = None) -> Section:
    section = db.session.get(Section, section_id)
    if not section:
        raise ValueError(f'Section {section_id} not found.')
    if program:
        section.program = program.strip().upper()
    if year_level:
        section.year_level = year_level
    if section_letter:
        section.section_letter = section_letter.strip().upper()
    db.session.commit()
    return section


def delete_section(section_id: int) -> None:
    section = db.session.get(Section, section_id)
    if not section:
        raise ValueError(f'Section {section_id} not found.')
    db.session.delete(section)
    db.session.commit()


def assign_student_section(student_db_id: int, section_id: int | None) -> Student:
    """Set the section_id FK on a student record."""
    student = db.session.get(Student, student_db_id)
    if not student:
        raise ValueError(f'Student {student_db_id} not found.')
    if section_id is not None:
        section = db.session.get(Section, section_id)
        if not section:
            raise ValueError(f'Section {section_id} not found.')
        # Also sync the legacy text field
        student.section = section.display_name
    else:
        section = None
    student.section_id = section_id
    db.session.commit()
    return student


# ─── Admin Schedule Management ────────────────────────────────────────────────

def get_all_admin_schedules(
    section_id: int = None,
    semester: str = None,
    academic_year: str = None,
    page: int = 1,
    per_page: int = 20,
):
    """Return paginated section-level schedules, filterable."""
    q = (
        Schedule.query
        .filter(Schedule.section_id.isnot(None))
        .options(
            db.joinedload(Schedule.section_obj),
            db.joinedload(Schedule.subject),
            db.joinedload(Schedule.faculty),
        )
        .order_by(Schedule.section_id, Schedule.day_of_week, Schedule.time_start)
    )
    if section_id:
        q = q.filter(Schedule.section_id == section_id)
    if semester:
        q = q.filter(Schedule.semester == semester)
    if academic_year:
        q = q.filter(Schedule.academic_year == academic_year)
    return q.paginate(page=page, per_page=per_page, error_out=False)


def create_admin_schedule(
    section_id: int,
    subject_id: int,
    faculty_id: int,
    day_of_week: str,
    time_start,
    time_end,
    room: str,
    semester: str,
    academic_year: str,
) -> Schedule:
    from app.models.section import Section as Sec
    section = db.session.get(Sec, section_id)
    subject = db.session.get(Subject, subject_id)
    faculty = db.session.get(Faculty, faculty_id)
    if not section or not subject or not faculty:
        raise ValueError('Section, Subject, or Faculty not found.')
    schedule = Schedule(
        section_id=section_id,
        faculty_id=faculty_id,
        subject_id=subject_id,
        day_of_week=day_of_week,
        time_start=time_start,
        time_end=time_end,
        room=room or None,
        semester=semester,
        academic_year=academic_year,
    )
    db.session.add(schedule)
    db.session.commit()
    return schedule


def delete_admin_schedule(schedule_id: int) -> None:
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        raise ValueError(f'Schedule {schedule_id} not found.')
    if schedule.section_id is None:
        raise ValueError('This is not an admin-managed schedule.')
    db.session.delete(schedule)
    db.session.commit()


def update_admin_schedule(
    schedule_id: int,
    section_id: int = None,
    subject_id: int = None,
    faculty_id: int = None,
    day_of_week: str = None,
    time_start=None,
    time_end=None,
    room: str = None,
    semester: str = None,
    academic_year: str = None,
) -> Schedule:
    """Edit an admin-managed schedule entry."""
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        raise ValueError(f'Schedule {schedule_id} not found.')
    if schedule.section_id is None:
        raise ValueError('This is not an admin-managed schedule.')
    if section_id is not None:
        schedule.section_id = section_id
    if subject_id is not None:
        schedule.subject_id = subject_id
    if faculty_id is not None:
        schedule.faculty_id = faculty_id
    if day_of_week is not None:
        schedule.day_of_week = day_of_week
    if time_start is not None:
        schedule.time_start = time_start
    if time_end is not None:
        schedule.time_end = time_end
    if room is not None:
        schedule.room = room or None
    if semester is not None:
        schedule.semester = semester
    if academic_year is not None:
        schedule.academic_year = academic_year
    db.session.commit()
    return schedule
