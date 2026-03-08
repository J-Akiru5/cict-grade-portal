from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.security import role_required
from app.services import faculty_service, admin_service
from app.models.academic_settings import AcademicSettings
from app.extensions import db
import logging

panel_bp = Blueprint('panel', __name__, template_folder='../../templates/panel')


def _is_htmx() -> bool:
    return request.headers.get('HX-Request') == 'true'


def _current_period():
    """Return (semester, year) from AcademicSettings."""
    settings = AcademicSettings.get_current()
    return settings.current_semester, settings.current_year


# ═══════════════════════════════════════════════════════════════════
#  SHARED: Faculty + Admin routes
# ═══════════════════════════════════════════════════════════════════

@panel_bp.route('/dashboard')
@login_required
@role_required('faculty', 'admin')
def dashboard():
    semester, year = _current_period()
    faculty = faculty_service.get_faculty_profile(current_user.id)
    subjects = faculty_service.get_faculty_subjects(faculty.id) if faculty else []
    context = {
        'faculty': faculty,
        'subjects': subjects,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'dashboard',
    }
    if _is_htmx():
        return render_template('panel/partials/dashboard.html', **context)
    return render_template('panel/pages/dashboard.html', **context)


@panel_bp.route('/subjects')
@login_required
@role_required('faculty', 'admin')
def my_subjects():
    semester, year = _current_period()
    faculty = faculty_service.get_faculty_profile(current_user.id)
    subjects = faculty_service.get_faculty_subjects(faculty.id) if faculty else []
    context = {
        'faculty': faculty,
        'subjects': subjects,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'subjects',
    }
    if _is_htmx():
        return render_template('panel/partials/subjects.html', **context)
    return render_template('panel/pages/subjects.html', **context)


@panel_bp.route('/subjects/<int:subject_id>/grades')
@login_required
@role_required('faculty', 'admin')
def subject_grades(subject_id):
    semester = request.args.get('semester')
    year = request.args.get('year')
    if not semester or not year:
        semester, year = _current_period()

    faculty = faculty_service.get_faculty_profile(current_user.id)
    if not faculty:
        flash('Faculty profile not found.', 'error')
        return redirect(url_for('panel.my_subjects'))

    try:
        enrollments = faculty_service.get_grades_for_subject(
            faculty.id, subject_id, semester, year
        )
    except PermissionError:
        flash('You do not have access to this subject.', 'error')
        return redirect(url_for('panel.my_subjects'))

    from app.models.subject import Subject
    subject = db.session.get(Subject, subject_id)
    context = {
        'faculty': faculty,
        'subject': subject,
        'enrollments': enrollments,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'subjects',
    }
    if _is_htmx():
        return render_template('panel/partials/grades.html', **context)
    return render_template('panel/pages/grades.html', **context)


@panel_bp.route('/subjects/<int:subject_id>/grades/<int:enrollment_id>/encode', methods=['POST'])
@login_required
@role_required('faculty', 'admin')
def encode_grade(subject_id, enrollment_id):
    faculty = faculty_service.get_faculty_profile(current_user.id)
    if not faculty:
        flash('Faculty profile not found.', 'error')
        return redirect(url_for('panel.my_subjects'))

    raw = request.form.get('grade_value', '').strip().upper()
    remarks = None
    grade_value = None

    if raw in ('INC', 'DRP'):
        remarks = raw
    elif raw:
        try:
            grade_value = round(float(raw), 2)
            if grade_value not in admin_service.VALID_GRADES:
                flash(f'Invalid grade value: {raw}. Must be one of {sorted(admin_service.VALID_GRADES)}.', 'error')
                return redirect(request.referrer or url_for('panel.subject_grades', subject_id=subject_id))
        except ValueError:
            flash(f'Invalid grade: "{raw}".', 'error')
            return redirect(request.referrer or url_for('panel.subject_grades', subject_id=subject_id))

    try:
        faculty_service.update_grade(faculty.id, enrollment_id, grade_value, remarks, current_user)
        flash('Grade saved successfully.', 'success')
    except PermissionError as e:
        flash(str(e), 'error')
    except Exception as e:
        logging.error(f'Grade encode error: {e}')
        flash('An error occurred while saving the grade.', 'error')

    semester = request.form.get('semester')
    year = request.form.get('year')
    return redirect(url_for('panel.subject_grades', subject_id=subject_id,
                            semester=semester, year=year))


@panel_bp.route('/students')
@login_required
@role_required('faculty', 'admin')
def students():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_students(search=search or None, page=page, per_page=20)
    context = {
        'pagination': pagination,
        'students': pagination.items,
        'search': search,
        'active_page': 'students',
    }
    if _is_htmx():
        return render_template('panel/partials/students.html', **context)
    return render_template('panel/pages/students.html', **context)


@panel_bp.route('/students/<int:student_db_id>')
@login_required
@role_required('faculty', 'admin')
def student_detail(student_db_id):
    from app.models.student import Student
    from app.services import student_service, gwa_service
    student = db.session.get(Student, student_db_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('panel.students'))

    semester, year = _current_period()
    grades = student_service.get_grades(student.id, semester=semester, academic_year=year)
    gwa = gwa_service.compute_gwa(grades)
    gwa_status = gwa_service.get_gwa_status(gwa)
    all_enrollments = student_service.get_all_enrollments(student.id)

    context = {
        'student': student,
        'grades': grades,
        'gwa': gwa,
        'gwa_status': gwa_status,
        'all_enrollments': all_enrollments,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'students',
    }
    if _is_htmx():
        return render_template('panel/partials/student_detail.html', **context)
    return render_template('panel/pages/student_detail.html', **context)


@panel_bp.route('/schedule')
@login_required
@role_required('faculty', 'admin')
def faculty_schedule():
    semester = request.args.get('semester')
    year = request.args.get('year')
    if not semester or not year:
        semester, year = _current_period()

    faculty = faculty_service.get_faculty_profile(current_user.id)
    schedules = faculty_service.get_faculty_schedule(faculty.id, semester, year) if faculty else []
    subjects = faculty_service.get_faculty_subjects(faculty.id) if faculty else []

    context = {
        'faculty': faculty,
        'schedules': schedules,
        'subjects': subjects,
        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'current_semester': semester,
        'current_year': year,
        'active_page': 'schedule',
    }
    if _is_htmx():
        return render_template('panel/partials/schedule.html', **context)
    return render_template('panel/pages/schedule.html', **context)


@panel_bp.route('/schedule/add', methods=['POST'])
@login_required
@role_required('faculty', 'admin')
def add_schedule():
    from datetime import time as dt_time
    faculty = faculty_service.get_faculty_profile(current_user.id)
    if not faculty:
        flash('Faculty profile not found.', 'error')
        return redirect(url_for('panel.faculty_schedule'))

    try:
        subject_id = int(request.form['subject_id'])
        day = request.form['day_of_week']
        ts = request.form['time_start']
        te = request.form['time_end']
        room = request.form.get('room', '').strip() or None
        semester = request.form.get('semester')
        year = request.form.get('year')

        h, m = map(int, ts.split(':'))
        time_start = dt_time(h, m)
        h, m = map(int, te.split(':'))
        time_end = dt_time(h, m)

        faculty_service.add_faculty_schedule(
            faculty.id, subject_id, day, time_start, time_end, room, semester, year
        )
        flash('Schedule entry added.', 'success')
    except PermissionError as e:
        flash(str(e), 'error')
    except Exception as e:
        logging.error(f'Add schedule error: {e}')
        flash('Could not add schedule entry.', 'error')

    return redirect(url_for('panel.faculty_schedule',
                            semester=request.form.get('semester'),
                            year=request.form.get('year')))


@panel_bp.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
@role_required('faculty', 'admin')
def delete_schedule(schedule_id):
    faculty = faculty_service.get_faculty_profile(current_user.id)
    if not faculty:
        flash('Faculty profile not found.', 'error')
        return redirect(url_for('panel.faculty_schedule'))
    try:
        faculty_service.delete_faculty_schedule(faculty.id, schedule_id)
        flash('Schedule entry deleted.', 'success')
    except PermissionError as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.faculty_schedule'))


@panel_bp.route('/audit-log')
@login_required
@role_required('faculty', 'admin')
def audit_log():
    entries = faculty_service.get_faculty_audit_log(current_user.id)
    context = {
        'entries': entries,
        'active_page': 'audit_log',
    }
    if _is_htmx():
        return render_template('panel/partials/audit_log.html', **context)
    return render_template('panel/pages/audit_log.html', **context)


# ═══════════════════════════════════════════════════════════════════
#  ADMIN-ONLY routes
# ═══════════════════════════════════════════════════════════════════

@panel_bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_users(search=search or None, page=page)
    all_faculty = admin_service.get_all_faculty(page=1, per_page=200).items
    all_subjects = db.session.execute(
        db.select(db.text('*')).select_from(db.text('subjects ORDER BY subject_code'))
    ).fetchall() if False else []  # fetched in template via service
    from app.models.subject import Subject
    subjects = Subject.query.order_by(Subject.subject_code).all()
    context = {
        'pagination': pagination,
        'users': pagination.items,
        'search': search,
        'all_faculty': all_faculty,
        'subjects': subjects,
        'active_page': 'admin_users',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/users.html', **context)
    return render_template('panel/pages/admin/users.html', **context)


@panel_bp.route('/admin/users/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_user():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'student')
    full_name = request.form.get('full_name', '').strip() or None
    employee_id = request.form.get('employee_id', '').strip() or None

    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('panel.admin_users'))

    try:
        admin_service.create_user(email, password, role, full_name=full_name, employee_id=employee_id)
        flash(f'User {email} created successfully as {role}.', 'success')
    except Exception as e:
        logging.error(f'Create user error: {e}')
        flash(f'Could not create user: {e}', 'error')

    return redirect(url_for('panel.admin_users'))


@panel_bp.route('/admin/users/<user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_update_role(user_id):
    new_role = request.form.get('role')
    try:
        admin_service.update_user_role(user_id, new_role)
        flash(f'Role updated to {new_role}.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_users'))


@panel_bp.route('/admin/users/<user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_user(user_id):
    try:
        user = admin_service.toggle_user_active(user_id)
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.email} {status}.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_users'))


@panel_bp.route('/admin/users/<int:faculty_id>/assign-subject', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_subject(faculty_id):
    subject_id = request.form.get('subject_id', type=int)
    try:
        admin_service.assign_subject_to_faculty(faculty_id, subject_id)
        flash('Subject assigned.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_users'))


@panel_bp.route('/admin/faculty/<int:faculty_id>/remove-subject/<int:subject_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_subject(faculty_id, subject_id):
    try:
        admin_service.remove_subject_from_faculty(faculty_id, subject_id)
        flash('Subject removed.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_users'))


# ── Admin Students ──────────────────────────────────────────────────

@panel_bp.route('/admin/students')
@login_required
@role_required('admin')
def admin_students():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_students(search=search or None, page=page)
    from app.models.user import User
    students_without_profile = (
        User.query.filter_by(role='student')
        .filter(~User.student_profile.has())
        .all()
    )
    context = {
        'pagination': pagination,
        'students': pagination.items,
        'search': search,
        'orphan_users': students_without_profile,
        'active_page': 'admin_students',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/students.html', **context)
    return render_template('panel/pages/admin/students.html', **context)


@panel_bp.route('/admin/students/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_student():
    try:
        user_id = request.form['user_id']
        admin_service.create_student(
            user_id=user_id,
            student_id=request.form['student_id'],
            full_name=request.form['full_name'],
            section=request.form.get('section') or None,
            year_level=int(request.form['year_level']) if request.form.get('year_level') else None,
            curriculum_year=request.form.get('curriculum_year') or None,
            age=int(request.form['age']) if request.form.get('age') else None,
            address=request.form.get('address') or None,
            contact_number=request.form.get('contact_number') or None,
            gmail=request.form.get('gmail') or None,
        )
        flash('Student profile created.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_students'))


@panel_bp.route('/admin/students/<int:student_db_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_student(student_db_id):
    from app.models.student import Student
    student = db.session.get(Student, student_db_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('panel.admin_students'))

    if request.method == 'POST':
        try:
            admin_service.update_student(
                student_db_id,
                student_id=request.form.get('student_id'),
                full_name=request.form.get('full_name'),
                section=request.form.get('section') or None,
                year_level=int(request.form['year_level']) if request.form.get('year_level') else None,
                curriculum_year=request.form.get('curriculum_year') or None,
                age=int(request.form['age']) if request.form.get('age') else None,
                address=request.form.get('address') or None,
                contact_number=request.form.get('contact_number') or None,
                gmail=request.form.get('gmail') or None,
            )
            flash('Student updated.', 'success')
            return redirect(url_for('panel.admin_students'))
        except Exception as e:
            flash(f'Error: {e}', 'error')

    context = {'student': student, 'active_page': 'admin_students'}
    return render_template('panel/pages/admin/edit_student.html', **context)


@panel_bp.route('/admin/students/<int:student_db_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_student(student_db_id):
    try:
        admin_service.delete_student(student_db_id)
        flash('Student deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_students'))


# ── Admin Subjects ──────────────────────────────────────────────────

@panel_bp.route('/admin/subjects')
@login_required
@role_required('admin')
def admin_subjects():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_subjects(search=search or None, page=page)
    context = {
        'pagination': pagination,
        'subjects': pagination.items,
        'search': search,
        'active_page': 'admin_subjects',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/subjects.html', **context)
    return render_template('panel/pages/admin/subjects.html', **context)


@panel_bp.route('/admin/subjects/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_subject():
    try:
        admin_service.create_subject(
            code=request.form['subject_code'],
            title=request.form['subject_title'],
            units=int(request.form.get('units', 3)),
            instructor_name=request.form.get('instructor_name') or None,
            department=request.form.get('department', 'CICT'),
        )
        flash('Subject created.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_subjects'))


@panel_bp.route('/admin/subjects/<int:subject_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def admin_edit_subject(subject_id):
    try:
        admin_service.update_subject(
            subject_id,
            subject_code=request.form.get('subject_code'),
            subject_title=request.form.get('subject_title'),
            units=int(request.form['units']) if request.form.get('units') else None,
            instructor_name=request.form.get('instructor_name') or None,
            department=request.form.get('department') or None,
        )
        flash('Subject updated.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_subjects'))


@panel_bp.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_subject(subject_id):
    try:
        admin_service.delete_subject(subject_id)
        flash('Subject deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_subjects'))


# ── Admin Enrollments ───────────────────────────────────────────────

@panel_bp.route('/admin/enrollments')
@login_required
@role_required('admin')
def admin_enrollments():
    search = request.args.get('q', '').strip()
    semester = request.args.get('semester') or None
    year = request.args.get('year') or None
    page = request.args.get('page', 1, type=int)

    if not semester and not year:
        s, y = _current_period()
        semester, year = s, y

    pagination = admin_service.get_all_enrollments(
        search=search or None, semester=semester, academic_year=year, page=page
    )
    from app.models.student import Student
    from app.models.subject import Subject
    all_students = Student.query.order_by(Student.full_name).all()
    all_subjects = Subject.query.order_by(Subject.subject_code).all()

    context = {
        'pagination': pagination,
        'enrollments': pagination.items,
        'search': search,
        'all_students': all_students,
        'all_subjects': all_subjects,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'admin_enrollments',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/enrollments.html', **context)
    return render_template('panel/pages/admin/enrollments.html', **context)


@panel_bp.route('/admin/enrollments/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_enrollment():
    try:
        admin_service.create_enrollment(
            student_db_id=int(request.form['student_db_id']),
            subject_id=int(request.form['subject_id']),
            semester=request.form['semester'],
            academic_year=request.form['academic_year'],
        )
        flash('Student enrolled.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_enrollments'))


@panel_bp.route('/admin/enrollments/<int:enrollment_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_enrollment(enrollment_id):
    try:
        admin_service.delete_enrollment(enrollment_id)
        flash('Enrollment removed.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_enrollments'))


# ── Admin Grade Import ──────────────────────────────────────────────

@panel_bp.route('/admin/grade-import', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_grade_import():
    result = None
    semester, year = _current_period()

    if request.method == 'POST':
        semester = request.form.get('semester', semester)
        year = request.form.get('year', year)
        file = request.files.get('csv_file')
        if not file or not file.filename:
            flash('No file uploaded.', 'error')
        else:
            result = admin_service.import_grades_from_csv(file.stream, semester, year, current_user)
            if result['errors']:
                flash(f"Import failed: {len(result['errors'])} error(s) found. No grades were saved.", 'error')
            else:
                flash(f"✅ Imported {result['imported']} grade(s) successfully.", 'success')

    context = {
        'result': result,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'admin_grade_import',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/grade_import.html', **context)
    return render_template('panel/pages/admin/grade_import.html', **context)


# ── Admin Audit Log ─────────────────────────────────────────────────

@panel_bp.route('/admin/audit-log')
@login_required
@role_required('admin')
def admin_audit_log():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_full_audit_log(search=search or None, page=page)
    context = {
        'pagination': pagination,
        'entries': pagination.items,
        'search': search,
        'active_page': 'admin_audit_log',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/audit_log.html', **context)
    return render_template('panel/pages/admin/audit_log.html', **context)


# ── Admin Settings ──────────────────────────────────────────────────

@panel_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_settings():
    settings = admin_service.get_academic_settings()

    if request.method == 'POST':
        semester = request.form.get('semester')
        year = request.form.get('year', '').strip()
        if not semester or not year:
            flash('Semester and year are required.', 'error')
        else:
            try:
                admin_service.update_academic_settings(semester, year, current_user)
                flash(f'Academic period updated to {semester} Semester {year}.', 'success')
                settings = admin_service.get_academic_settings()
            except Exception as e:
                flash(f'Error: {e}', 'error')

    context = {
        'settings': settings,
        'active_page': 'admin_settings',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/settings.html', **context)
    return render_template('panel/pages/admin/settings.html', **context)
