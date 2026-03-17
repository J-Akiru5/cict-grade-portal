from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app.utils.security import role_required
from app.services import student_service, gwa_service, storage_service
from app.models.academic_settings import AcademicSettings
from app.extensions import db

student_bp = Blueprint('student', __name__, template_folder='../../templates/student')


def _get_academic_period():
    """Read the current semester & academic year from the DB (set by admin)."""
    settings = AcademicSettings.get_current()
    return settings.current_semester, settings.current_year


def _is_htmx() -> bool:
    return request.headers.get('HX-Request') == 'true'


@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    CURRENT_SEMESTER, CURRENT_YEAR = _get_academic_period()
    student = student_service.get_student_profile(current_user.id)
    grades = student_service.get_grades(
        student.id, semester=CURRENT_SEMESTER, academic_year=CURRENT_YEAR
    ) if student else []
    gwa = gwa_service.compute_gwa(grades)
    gwa_status = gwa_service.get_gwa_status(gwa)

    context = {
        'student': student,
        'grades': grades,
        'gwa': gwa,
        'gwa_status': gwa_status,
        'current_semester': CURRENT_SEMESTER,
        'current_year': CURRENT_YEAR,
        'active_page': 'dashboard',
    }

    if _is_htmx():
        return render_template('partials/dashboard.html', **context)
    return render_template('student/pages/dashboard.html', **context)


@student_bp.route('/profile')
@login_required
@role_required('student')
def profile():
    student = student_service.get_student_profile(current_user.id)
    context = {
        'student': student,
        'active_page': 'profile',
    }
    if _is_htmx():
        return render_template('partials/profile.html', **context)
    return render_template('student/pages/profile.html', **context)


@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('student')
def edit_profile():
    student = student_service.get_student_profile(current_user.id)

    # If no student profile exists, show error and redirect
    if not student:
        flash('No student profile found. Please contact the registrar.', 'error')
        return redirect(url_for('student.profile'))

    if request.method == 'POST':
        # Handle avatar upload
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            file_bytes = avatar_file.read()
            content_type = avatar_file.content_type or 'image/jpeg'
            url = storage_service.upload_avatar(current_user.id, file_bytes, content_type)
            if url:
                current_user.avatar_url = url
                db.session.commit()

        full_name = request.form.get('full_name', '').strip()
        if not full_name:
            flash('Full name is required.', 'error')
        else:
            data = {
                'full_name': full_name,
                'age': request.form.get('age', type=int) or None,
                'address': request.form.get('address', '').strip() or None,
                'contact_number': request.form.get('contact_number', '').strip() or None,
                'gmail': request.form.get('gmail', '').strip() or None,
                'year_level': request.form.get('year_level', type=int) or None,
                'gender': request.form.get('gender', '').strip() or None,
            }
            updated = student_service.update_student_profile(current_user.id, data)
            if updated:
                flash('Profile updated successfully.', 'success')
            else:
                flash('Failed to update profile. Please try again.', 'error')

            if _is_htmx():
                resp = make_response('', 204)
                resp.headers['HX-Redirect'] = url_for('student.profile')
                return resp
            return redirect(url_for('student.profile'))

    context = {
        'student': student,
        'active_page': 'profile',
    }
    if _is_htmx():
        return render_template('partials/edit_profile.html', **context)
    return render_template('student/pages/edit_profile.html', **context)


@student_bp.route('/subjects')
@login_required
@role_required('student')
def subjects():
    CURRENT_SEMESTER, CURRENT_YEAR = _get_academic_period()
    student = student_service.get_student_profile(current_user.id)
    semester = request.args.get('semester', CURRENT_SEMESTER)
    year = request.args.get('year', CURRENT_YEAR)
    enrollments = student_service.get_all_enrollments(student.id) if student else []
    context = {
        'student': student,
        'enrollments': enrollments,
        'active_page': 'subjects',
        'current_semester': semester,
        'current_year': year,
    }
    if _is_htmx():
        return render_template('partials/subjects.html', **context)
    return render_template('student/pages/subjects.html', **context)


@student_bp.route('/schedule')
@login_required
@role_required('student')
def schedule():
    CURRENT_SEMESTER, CURRENT_YEAR = _get_academic_period()
    student = student_service.get_student_profile(current_user.id)
    semester = request.args.get('semester', CURRENT_SEMESTER)
    year = request.args.get('year', CURRENT_YEAR)
    matrix = student_service.get_schedule_matrix(
        student.id, semester=semester, academic_year=year
    ) if student else {}
    time_slots = student_service.get_time_slots()
    context = {
        'student': student,
        'matrix': matrix,
        'time_slots': time_slots,
        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'active_page': 'schedule',
        'current_semester': semester,
        'current_year': year,
    }
    if _is_htmx():
        return render_template('partials/schedule.html', **context)
    return render_template('student/pages/schedule.html', **context)


@student_bp.route('/grades')
@login_required
@role_required('student')
def grades():
    CURRENT_SEMESTER, CURRENT_YEAR = _get_academic_period()
    student = student_service.get_student_profile(current_user.id)
    semester = request.args.get('semester', CURRENT_SEMESTER)
    year = request.args.get('year', CURRENT_YEAR)
    grade_list = student_service.get_grades(
        student.id, semester=semester, academic_year=year
    ) if student else []
    gwa = gwa_service.compute_gwa(grade_list)
    gwa_status = gwa_service.get_gwa_status(gwa)

    context = {
        'student': student,
        'grades': grade_list,
        'gwa': gwa,
        'gwa_status': gwa_status,
        'active_page': 'grades',
        'current_semester': semester,
        'current_year': year,
        'get_grade_color': gwa_service.get_grade_color,
    }
    if _is_htmx():
        return render_template('partials/grades.html', **context)
    return render_template('student/pages/grades.html', **context)
