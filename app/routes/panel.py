from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app.utils.security import role_required
from app.services import faculty_service, admin_service, storage_service
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
#  PROFILE: Faculty + Admin self-service profile
# ═══════════════════════════════════════════════════════════════════

@panel_bp.route('/profile')
@login_required
@role_required('faculty', 'admin')
def panel_profile():
    faculty = current_user.faculty_profile
    context = {
        'faculty': faculty,
        'active_page': 'profile',
    }
    if _is_htmx():
        return render_template('panel/partials/profile.html', **context)
    return render_template('panel/pages/profile.html', **context)


@panel_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('faculty', 'admin')
def panel_edit_profile():
    from datetime import datetime, timezone

    faculty = current_user.faculty_profile

    if request.method == 'POST':
        # Handle avatar upload
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            file_bytes = avatar_file.read()
            content_type = avatar_file.content_type or 'image/jpeg'
            url = storage_service.upload_avatar(current_user.id, file_bytes, content_type)
            if url:
                current_user.avatar_url = url

        # Update faculty profile fields
        if faculty:
            full_name = request.form.get('full_name', '').strip()
            if full_name:
                faculty.full_name = full_name
            emp_id = request.form.get('employee_id', '').strip()
            if emp_id:
                faculty.employee_id = emp_id
            dept = request.form.get('department', '').strip()
            if dept:
                faculty.department = dept
            faculty.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        flash('Profile updated.', 'success')

        if _is_htmx():
            resp = make_response('', 204)
            resp.headers['HX-Redirect'] = url_for('panel.panel_profile')
            return resp
        return redirect(url_for('panel.panel_profile'))

    context = {
        'faculty': faculty,
        'active_page': 'profile',
    }
    if _is_htmx():
        return render_template('panel/partials/edit_profile.html', **context)
    return render_template('panel/pages/edit_profile.html', **context)


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

    # Admin-specific dashboard stats
    if current_user.role == 'admin':
        from app.models.student import Student
        from app.models.subject import Subject
        from app.models.faculty import Faculty
        from app.models.enrollment import Enrollment

        # Count students enrolled in current academic year
        enrolled_students = (
            db.session.query(db.func.count(db.distinct(Enrollment.student_id)))
            .filter(Enrollment.academic_year == year)
            .scalar()
        ) or 0
        context['enrolled_students'] = enrolled_students
        context['total_subjects'] = db.session.query(db.func.count(Subject.id)).scalar() or 0
        context['total_faculty'] = db.session.query(db.func.count(Faculty.id)).scalar() or 0
        context['total_sections'] = (
            db.session.query(db.func.count(db.distinct(Enrollment.student_id)))
            .filter(Enrollment.academic_year == year, Enrollment.semester == semester)
            .scalar()
        ) or 0

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
    semester = request.args.get('semester') or None
    year = request.args.get('year') or None
    page = request.args.get('page', 1, type=int)

    faculty = faculty_service.get_faculty_profile(current_user.id)
    schedules = faculty_service.get_faculty_schedule(
        faculty.id, semester=semester, academic_year=year, page=page
    ) if faculty else None
    subjects = faculty_service.get_faculty_subjects(faculty.id) if faculty else []

    context = {
        'faculty': faculty,
        'schedules': schedules,
        'subjects': subjects,
        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'current_semester': semester or '',
        'current_year': year or '',
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


@panel_bp.route('/schedule/<int:schedule_id>/edit', methods=['POST'])
@login_required
@role_required('faculty', 'admin')
def edit_schedule(schedule_id):
    from datetime import time as dt_time
    faculty = faculty_service.get_faculty_profile(current_user.id)
    if not faculty:
        flash('Faculty profile not found.', 'error')
        return redirect(url_for('panel.faculty_schedule'))
    try:
        subject_id = request.form.get('subject_id', type=int)
        day = request.form.get('day_of_week') or None
        room = request.form.get('room', '').strip() or ''
        semester = request.form.get('semester') or None
        year = request.form.get('year') or None
        ts = request.form.get('time_start', '')
        te = request.form.get('time_end', '')
        time_start = dt_time(*map(int, ts.split(':'))) if ts else None
        time_end = dt_time(*map(int, te.split(':'))) if te else None

        faculty_service.update_faculty_schedule(
            faculty.id, schedule_id,
            subject_id=subject_id,
            day_of_week=day,
            time_start=time_start,
            time_end=time_end,
            room=room,
            semester=semester,
            academic_year=year,
        )
        flash('Schedule entry updated.', 'success')
    except PermissionError as e:
        flash(str(e), 'error')
    except Exception as e:
        logging.error(f'Edit schedule error: {e}')
        flash('Could not update schedule entry.', 'error')
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
    if current_user.role == 'admin':
        return redirect(url_for('panel.admin_audit_log'))
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
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    is_active = None
    if status == 'active':
        is_active = True
    elif status == 'inactive':
        is_active = False

    pagination = admin_service.get_all_users(
        search=search or None,
        role=role or None,
        is_active=is_active,
        page=page
    )
    from app.models.subject import Subject
    from app.models.user import User
    subjects = Subject.query.order_by(Subject.subject_code).all()
    # Users awaiting approval: inactive and never logged in
    pending_users = (
        User.query.filter_by(is_active=False)
        .filter(User.last_login_at.is_(None))
        .order_by(User.created_at.asc())
        .all()
    )
    context = {
        'pagination': pagination,
        'users': pagination.items,
        'search': search,
        'role': role,
        'status': status,
        'subjects': subjects,
        'pending_users': pending_users,
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
        if user.is_active:
            sent = admin_service.send_account_approved_email(user)
            if sent:
                flash(f'User {user.email} activated. Approval email sent.', 'success')
            else:
                flash(f'User {user.email} activated. Approval email not sent (check Resend config).', 'warning')
        else:
            flash(f'User {user.email} deactivated.', 'success')
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


@panel_bp.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_user(user_id):
    from app.models.user import User
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('panel.admin_users'))

    if request.method == 'POST':
        try:
            new_email = request.form.get('email', '').strip().lower() or None
            new_password = request.form.get('new_password', '').strip() or None
            admin_service.update_user(
                user_id,
                email=new_email if new_email != user.email else None,
                password=new_password,
                full_name=request.form.get('full_name', '').strip() or None,
                employee_id=request.form.get('employee_id', '').strip(),
                department=request.form.get('department', '').strip() or None,
            )
            flash('User updated successfully.', 'success')
            return redirect(url_for('panel.admin_users'))
        except Exception as e:
            flash(f'Error: {e}', 'error')

    context = {'user': user, 'active_page': 'admin_users'}
    return render_template('panel/pages/admin/edit_user.html', **context)


# ── Admin Faculty Management ─────────────────────────────────────────

@panel_bp.route('/admin/faculty')
@login_required
@role_required('admin')
def admin_faculty():
    search = request.args.get('q', '').strip()
    dept = request.args.get('dept', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_faculty(
        search=search or None,
        department=dept or None,
        page=page
    )
    from app.models.subject import Subject
    subjects = Subject.query.order_by(Subject.subject_code).all()
    context = {
        'pagination': pagination,
        'faculty_list': pagination.items,
        'search': search,
        'dept': dept,
        'subjects': subjects,
        'active_page': 'admin_faculty',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/faculty.html', **context)
    return render_template('panel/pages/admin/faculty.html', **context)


@panel_bp.route('/admin/faculty/<int:faculty_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def admin_edit_faculty(faculty_id):
    try:
        admin_service.update_faculty(
            faculty_id,
            full_name=request.form.get('full_name', '').strip() or None,
            employee_id=request.form.get('employee_id', '').strip(),
            department=request.form.get('department', '').strip() or None,
        )
        flash('Faculty profile updated.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_faculty'))


@panel_bp.route('/admin/faculty/<int:faculty_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_faculty(faculty_id):
    try:
        admin_service.delete_faculty_profile(faculty_id)
        flash('Faculty profile removed. The user account still exists.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_faculty'))


@panel_bp.route('/admin/faculty/<int:faculty_id>/assign-subject', methods=['POST'])
@login_required
@role_required('admin')
def admin_faculty_assign_subject(faculty_id):
    subject_id = request.form.get('subject_id', type=int)
    try:
        admin_service.assign_subject_to_faculty(faculty_id, subject_id)
        flash('Subject assigned.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_faculty'))


@panel_bp.route('/admin/faculty/<int:faculty_id>/subjects/<int:subject_id>/unassign', methods=['POST'])
@login_required
@role_required('admin')
def admin_faculty_remove_subject(faculty_id, subject_id):
    try:
        admin_service.remove_subject_from_faculty(faculty_id, subject_id)
        flash('Subject removed.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('panel.admin_faculty'))


# ── Admin Students ──────────────────────────────────────────────────

@panel_bp.route('/admin/students')
@login_required
@role_required('admin')
def admin_students():
    search = request.args.get('q', '').strip()
    section_id = request.args.get('section_id', type=int)
    year_level = request.args.get('year_level', type=int)
    page = request.args.get('page', 1, type=int)

    pagination = admin_service.get_all_students(
        search=search or None,
        section_id=section_id,
        year_level=year_level,
        page=page
    )
    from app.models.user import User
    from app.models.section import Section
    from app.models.student import Student
    students_without_profile = (
        User.query.filter_by(role='student')
        .filter(~User.student_profile.has())
        .all()
    )
    all_sections = Section.query.order_by(Section.program, Section.year_level, Section.section_letter).all()
    all_students = Student.query.order_by(Student.full_name).all()

    context = {
        'pagination': pagination,
        'students': pagination.items,
        'search': search,
        'section_id': section_id,
        'year_level': year_level,
        'orphan_users': students_without_profile,
        'sections': all_sections,
        'all_students': all_students,
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
        mode = request.form.get('mode', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        created = False

        if mode == 'create_with_account' or (email and password):
            admin_service.create_student_with_account(
                email=email,
                password=password,
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
            created = True
        elif mode == 'attach_existing' or request.form.get('user_id', '').strip():
            user_id = request.form.get('user_id', '').strip()
            if not user_id:
                flash('Please select a user account to attach.', 'error')
                return redirect(url_for('panel.admin_students'))
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
            created = True
        elif mode == 'profile_only':
            admin_service.create_student(
                user_id=None,
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
            created = True
        else:
            flash('Provide account details, attach an existing user, or choose profile-only mode.', 'error')

        if created:
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


@panel_bp.route('/admin/students/merge', methods=['POST'])
@login_required
@role_required('admin')
def admin_merge_students():
    try:
        primary_id = int(request.form['primary_id'])
        secondary_id = int(request.form['secondary_id'])
        merged = admin_service.merge_student_profiles(primary_id, secondary_id)
        flash(f'Successfully merged into {merged.full_name} ({merged.student_id}).', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Merge failed: {e}', 'error')
    return redirect(url_for('panel.admin_students'))


@panel_bp.route('/admin/students/<int:student_db_id>/create-account', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_student_account(student_db_id):
    try:
        student, user, temp_password = admin_service.create_account_for_student_profile(student_db_id)
        email_sent = admin_service.send_account_approved_email(user, temporary_password=temp_password)

        if temp_password and email_sent:
            flash(
                f'Account created for {student.full_name} ({user.email}). Temporary password sent via email.',
                'success'
            )
        elif temp_password and not email_sent:
            flash(
                f'Account created for {student.full_name} ({user.email}). '
                f'Temporary password: {temp_password}. Email not sent (check Resend config).',
                'warning'
            )
        elif email_sent:
            flash(f'Existing account linked to {student.full_name} and approval email sent.', 'success')
        else:
            flash(f'Existing account linked to {student.full_name}. Email not sent (check Resend config).', 'warning')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect(url_for('panel.admin_students'))


# ── Admin Subjects ──────────────────────────────────────────────────

@panel_bp.route('/admin/subjects')
@login_required
@role_required('admin')
def admin_subjects():
    search = request.args.get('q', '').strip()
    dept = request.args.get('dept', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_all_subjects(
        search=search or None,
        department=dept or None,
        page=page
    )
    context = {
        'pagination': pagination,
        'subjects': pagination.items,
        'search': search,
        'dept': dept,
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


# ── Admin Grades View ────────────────────────────────────────────────

@panel_bp.route('/admin/grades')
@login_required
@role_required('admin')
def admin_grades():
    """Admin view of all students with aggregated grade summary."""
    from app.models.section import Section
    from app.models.subject import Subject
    from app.models.student import Student
    from app.models.enrollment import Enrollment
    from app.models.grade import Grade
    from sqlalchemy import func

    # Get filter parameters
    search = request.args.get('q', '').strip()
    section_id = request.args.get('section_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    semester = request.args.get('semester')
    year = request.args.get('year')
    page = request.args.get('page', 1, type=int)

    if not semester or not year:
        semester, year = _current_period()

    # Subquery for GPA calculation per student
    gpa_subquery = (
        db.session.query(
            Enrollment.student_id,
            func.round(
                func.sum(Grade.grade_value * Subject.units) / func.sum(Subject.units),
                4
            ).label('avg_gpa')
        )
        .join(Grade, Enrollment.id == Grade.enrollment_id)
        .join(Subject, Enrollment.subject_id == Subject.id)
        .filter(Enrollment.semester == semester)
        .filter(Enrollment.academic_year == year)
        .filter(Grade.grade_value.isnot(None))
        .filter((Grade.remarks.notin_(['INC', 'DRP'])) | (Grade.remarks.is_(None)))
        .group_by(Enrollment.student_id)
        .subquery()
    )

    # Main query: aggregate enrollments by student
    q = (
        db.session.query(
            Student,
            func.count(db.distinct(Enrollment.id)).label('subject_count'),
            gpa_subquery.c.avg_gpa
        )
        .join(Enrollment, Student.id == Enrollment.student_id)
        .outerjoin(gpa_subquery, Student.id == gpa_subquery.c.student_id)
        .filter(Enrollment.semester == semester)
        .filter(Enrollment.academic_year == year)
        .group_by(Student.id, gpa_subquery.c.avg_gpa)
    )

    # Apply filters
    if search:
        q = q.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%'),
            )
        )
    if section_id:
        q = q.filter(Student.section_id == section_id)
    if subject_id:
        q = q.filter(Enrollment.subject_id == subject_id)

    q = q.order_by(Student.full_name)
    pagination = q.paginate(page=page, per_page=30, error_out=False)

    # Transform results to include metadata
    students_data = [
        {
            'student': student,
            'subject_count': subject_count,
            'avg_gpa': avg_gpa,
        }
        for student, subject_count, avg_gpa in pagination.items
    ]

    # Get filter options
    sections = Section.query.order_by(Section.program, Section.year_level, Section.section_letter).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()

    context = {
        'pagination': pagination,
        'students_data': students_data,
        'search': search,
        'section_id': section_id,
        'subject_id': subject_id,
        'sections': sections,
        'subjects': subjects,
        'current_semester': semester,
        'current_year': year,
        'active_page': 'admin_grades',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/grades.html', **context)
    return render_template('panel/pages/admin/grades.html', **context)


@panel_bp.route('/admin/grades/<int:enrollment_id>/encode', methods=['POST'])
@login_required
@role_required('admin')
def admin_encode_grade(enrollment_id):
    """Admin can encode grades for any enrollment (no faculty ownership check)."""
    from app.models.enrollment import Enrollment
    from app.models.grade import Grade
    from datetime import datetime, timezone

    enrollment = db.session.get(Enrollment, enrollment_id)
    if not enrollment:
        flash('Enrollment not found.', 'error')
        return redirect(url_for('panel.admin_grades'))

    raw = request.form.get('grade_value', '').strip().upper()
    remarks = None
    grade_value = None

    if raw in ('INC', 'DRP'):
        remarks = raw
    elif raw:
        try:
            grade_value = round(float(raw), 2)
            if grade_value not in admin_service.VALID_GRADES:
                flash(f'Invalid grade: {raw}. Must be one of {sorted(admin_service.VALID_GRADES)}.', 'error')
                return redirect(request.referrer or url_for('panel.admin_grades'))
        except ValueError:
            flash(f'Invalid grade: "{raw}".', 'error')
            return redirect(request.referrer or url_for('panel.admin_grades'))

    # Create or update grade
    grade = enrollment.grade
    if not grade:
        grade = Grade(enrollment_id=enrollment.id)
        db.session.add(grade)

    grade.grade_value = grade_value
    grade.remarks = remarks
    grade.date_encoded = datetime.now(timezone.utc)
    grade.encoded_by_id = current_user.id

    try:
        db.session.commit()
        flash('Grade saved successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Admin grade encode error: {e}')
        flash('Error saving grade.', 'error')

    return redirect(request.referrer or url_for('panel.admin_grades'))


def _group_enrollments(enrollments, layout):
    """Helper to group enrollments by layout type."""
    from collections import defaultdict

    if layout == 'by_semester':
        # Group by semester + year
        grouped = defaultdict(list)
        for e in enrollments:
            key = f"{e.semester} {e.academic_year}"
            grouped[key].append(e)
        return dict(grouped)

    elif layout == 'by_section':
        # Group by year level extracted from subject code
        grouped = defaultdict(list)
        for e in enrollments:
            subject_code = e.subject.subject_code
            year_level = 'Other'
            # Try to extract year level from subject code (e.g., IT 211 -> Year 2)
            parts = subject_code.split()
            if len(parts) > 1 and parts[1].isdigit():
                year_digit = parts[1][0]
                year_level = f"Year {year_digit}"
            grouped[year_level].append(e)
        return dict(grouped)

    else:  # by_subject (simple list, no grouping)
        return {'All Subjects': enrollments}


@panel_bp.route('/admin/grades/student/<int:student_db_id>')
@login_required
@role_required('admin')
def admin_student_grades(student_db_id):
    """Dedicated page for viewing/editing all grades for a specific student."""
    from app.models.student import Student
    from app.models.enrollment import Enrollment
    from app.models.grade import Grade
    from app.models.subject import Subject
    from app.services import gwa_service

    student = db.session.get(Student, student_db_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('panel.admin_grades'))

    # Get filter parameters
    semester = request.args.get('semester')
    year = request.args.get('year')
    layout = request.args.get('layout', 'by_subject')

    # Query all enrollments with grades for this student
    query = (
        Enrollment.query
        .filter_by(student_id=student_db_id)
        .join(Subject)
        .outerjoin(Grade)
        .options(
            db.contains_eager(Enrollment.subject),
            db.joinedload(Enrollment.grade),
        )
    )

    # Optional filters
    if semester:
        query = query.filter(Enrollment.semester == semester)
    if year:
        query = query.filter(Enrollment.academic_year == year)

    # Order based on layout
    if layout == 'by_semester':
        query = query.order_by(
            Enrollment.academic_year.desc(),
            Enrollment.semester,
            Subject.subject_code
        )
    else:
        query = query.order_by(Subject.subject_code)

    enrollments = query.all()

    # Get all grades for GWA calculation
    all_grades = [e.grade for e in enrollments if e.grade]
    overall_gwa = gwa_service.compute_gwa(all_grades) if all_grades else None
    gwa_status = gwa_service.get_gwa_status(overall_gwa)

    # Group enrollments by layout type
    grouped_data = _group_enrollments(enrollments, layout)

    # Get unique semesters/years for filtering
    periods = (
        db.session.query(
            Enrollment.semester,
            Enrollment.academic_year
        )
        .filter_by(student_id=student_db_id)
        .distinct()
        .order_by(Enrollment.academic_year.desc(), Enrollment.semester)
        .all()
    )

    context = {
        'student': student,
        'enrollments': enrollments,
        'grouped_data': grouped_data,
        'layout': layout,
        'overall_gwa': overall_gwa,
        'gwa_status': gwa_status,
        'total_subjects': len(enrollments),
        'total_units': sum(e.subject.units for e in enrollments),
        'encoded_count': sum(1 for e in enrollments if e.grade and e.grade.grade_value is not None),
        'periods': periods,
        'filter_semester': semester,
        'filter_year': year,
        'active_page': 'admin_grades',
    }

    if _is_htmx():
        return render_template('panel/partials/admin/student_grades.html', **context)
    return render_template('panel/pages/admin/student_grades.html', **context)


@panel_bp.route('/admin/grades/student/<int:student_db_id>/save-all', methods=['POST'])
@login_required
@role_required('admin')
def admin_save_student_grades(student_db_id):
    """Batch save all grades for a student."""
    from app.models.student import Student
    from app.models.enrollment import Enrollment
    from app.models.grade import Grade
    from datetime import datetime, timezone

    student = db.session.get(Student, student_db_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('panel.admin_grades'))

    # Parse form data: expect grades[enrollment_id] = grade_value
    grades_data = {}
    for key in request.form:
        if key.startswith('grade_'):
            enrollment_id = int(key.split('_')[1])
            raw_value = request.form[key].strip().upper()
            if raw_value:  # Only include non-empty values
                grades_data[enrollment_id] = raw_value

    if not grades_data:
        flash('No grades to save.', 'warning')
        return redirect(request.referrer or url_for('panel.admin_student_grades', student_db_id=student_db_id))

    # Validate and save all grades
    errors = []
    updated_count = 0

    try:
        for enrollment_id, raw in grades_data.items():
            enrollment = db.session.get(Enrollment, enrollment_id)
            if not enrollment or enrollment.student_id != student_db_id:
                errors.append(f'Invalid enrollment {enrollment_id}')
                continue

            # Parse grade value
            remarks = None
            grade_value = None

            if raw in ('INC', 'DRP'):
                remarks = raw
            else:
                try:
                    grade_value = round(float(raw), 2)
                    if grade_value not in admin_service.VALID_GRADES:
                        errors.append(
                            f'{enrollment.subject.subject_code}: Invalid grade {raw}. '
                            f'Must be one of {sorted(admin_service.VALID_GRADES)}.'
                        )
                        continue
                except ValueError:
                    errors.append(f'{enrollment.subject.subject_code}: Invalid grade "{raw}".')
                    continue

            # Create or update grade
            grade = enrollment.grade
            if not grade:
                grade = Grade(enrollment_id=enrollment.id)
                db.session.add(grade)

            grade.grade_value = grade_value
            grade.remarks = remarks
            grade.date_encoded = datetime.now(timezone.utc)
            grade.encoded_by_id = current_user.id
            updated_count += 1

        if errors:
            db.session.rollback()
            for error in errors:
                flash(error, 'error')
        else:
            db.session.commit()
            flash(f'Successfully saved {updated_count} grade(s).', 'success')

    except Exception as e:
        db.session.rollback()
        logging.error(f'Batch grade save error: {e}')
        flash('Error saving grades.', 'error')

    return redirect(request.referrer or url_for('panel.admin_student_grades', student_db_id=student_db_id))


# ── Admin Audit Log ─────────────────────────────────────────────────

@panel_bp.route('/admin/audit-log')
@login_required
@role_required('admin')
def admin_audit_log():
    search = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = admin_service.get_full_audit_log(
        search=search or None,
        actor_role=role or None,
        page=page
    )
    context = {
        'pagination': pagination,
        'entries': pagination.items,
        'search': search,
        'role': role,
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
        year = request.form.get('academic_year', '').strip()
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


# ── Admin Sections ───────────────────────────────────────────────────

@panel_bp.route('/admin/sections')
@login_required
@role_required('admin')
def admin_sections():
    search = request.args.get('q', '').strip()
    program = request.args.get('program', '').strip()
    year_level = request.args.get('year_level', type=int)
    page = request.args.get('page', 1, type=int)

    pagination = admin_service.get_all_sections(
        search=search or None,
        program=program or None,
        year_level=year_level,
        page=page
    )
    from app.models.student import Student
    all_students = Student.query.order_by(Student.full_name).all()
    context = {
        'pagination': pagination,
        'sections': pagination.items,
        'search': search,
        'program': program,
        'year_level': year_level,
        'all_students': all_students,
        'active_page': 'admin_sections',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/sections.html', **context)
    return render_template('panel/pages/admin/sections.html', **context)


@panel_bp.route('/admin/sections/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_section():
    try:
        admin_service.create_section(
            program=request.form.get('program', 'BSIT').strip(),
            year_level=int(request.form['year_level']),
            section_letter=request.form['section_letter'].strip(),
        )
        flash('Section created.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_sections'))


@panel_bp.route('/admin/sections/<int:section_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def admin_edit_section(section_id):
    try:
        admin_service.update_section(
            section_id,
            program=request.form.get('program') or None,
            year_level=int(request.form['year_level']) if request.form.get('year_level') else None,
            section_letter=request.form.get('section_letter') or None,
        )
        flash('Section updated.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_sections'))


@panel_bp.route('/admin/sections/<int:section_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_section(section_id):
    try:
        admin_service.delete_section(section_id)
        flash('Section deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_sections'))


@panel_bp.route('/admin/sections/assign-student', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_student_section():
    try:
        student_id = int(request.form['student_db_id'])
        section_id = request.form.get('section_id')
        admin_service.assign_student_section(
            student_id,
            int(section_id) if section_id else None,
        )
        flash('Student section assigned.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_sections'))


# ── Admin Schedules ──────────────────────────────────────────────────

@panel_bp.route('/admin/schedules')
@login_required
@role_required('admin')
def admin_schedules():
    from app.models.section import Section
    from app.models.subject import Subject
    from app.models.faculty import Faculty

    section_filter = request.args.get('section_id', type=int)
    semester = request.args.get('semester') or None
    year = request.args.get('year') or None
    page = request.args.get('page', 1, type=int)

    schedules = admin_service.get_all_admin_schedules(
        section_id=section_filter,
        semester=semester,
        academic_year=year,
        page=page,
    )
    sections = admin_service.get_all_sections()
    subjects = Subject.query.order_by(Subject.subject_code).all()
    all_faculty = admin_service.get_all_faculty(page=1, per_page=200).items

    context = {
        'schedules': schedules,
        'sections': sections,
        'subjects': subjects,
        'all_faculty': all_faculty,
        'section_filter': section_filter,
        'current_semester': semester or '',
        'current_year': year or '',
        'active_page': 'admin_schedules',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/schedules.html', **context)
    return render_template('panel/pages/admin/schedules.html', **context)


@panel_bp.route('/admin/schedules/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_schedule():
    from datetime import time as dt_time
    try:
        ts = request.form['time_start']
        te = request.form['time_end']
        h, m = map(int, ts.split(':'))
        time_start = dt_time(h, m)
        h, m = map(int, te.split(':'))
        time_end = dt_time(h, m)

        admin_service.create_admin_schedule(
            section_id=int(request.form['section_id']),
            subject_id=int(request.form['subject_id']),
            faculty_id=int(request.form['faculty_id']),
            day_of_week=request.form['day_of_week'],
            time_start=time_start,
            time_end=time_end,
            room=request.form.get('room', '').strip() or None,
            semester=request.form['semester'],
            academic_year=request.form['year'],
        )
        flash('Schedule entry created.', 'success')
    except Exception as e:
        logging.error(f'Admin schedule create error: {e}')
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_schedules',
                            semester=request.form.get('semester'),
                            year=request.form.get('year')))


@panel_bp.route('/admin/schedules/<int:schedule_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def admin_edit_schedule(schedule_id):
    from datetime import time as dt_time
    try:
        section_id = request.form.get('section_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        faculty_id = request.form.get('faculty_id', type=int)
        day = request.form.get('day_of_week') or None
        room = request.form.get('room', '').strip()
        semester = request.form.get('semester') or None
        year = request.form.get('year') or None
        ts = request.form.get('time_start', '')
        te = request.form.get('time_end', '')
        time_start = dt_time(*map(int, ts.split(':'))) if ts else None
        time_end = dt_time(*map(int, te.split(':'))) if te else None

        admin_service.update_admin_schedule(
            schedule_id,
            section_id=section_id,
            subject_id=subject_id,
            faculty_id=faculty_id,
            day_of_week=day,
            time_start=time_start,
            time_end=time_end,
            room=room,
            semester=semester,
            academic_year=year,
        )
        flash('Schedule entry updated.', 'success')
    except Exception as e:
        logging.error(f'Admin schedule edit error: {e}')
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_schedules',
                            semester=request.form.get('semester'),
                            year=request.form.get('year')))


@panel_bp.route('/admin/schedules/<int:schedule_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_schedule(schedule_id):
    try:
        admin_service.delete_admin_schedule(schedule_id)
        flash('Schedule entry deleted.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('panel.admin_schedules'))
