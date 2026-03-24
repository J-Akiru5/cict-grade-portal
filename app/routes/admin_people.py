"""
admin_people.py — Blueprint for People management (Users + Faculty merged).

Routes:
  GET  /panel/admin/people          → list all users (tab: users)
  GET  /panel/admin/people/faculty  → HTMX fragment: faculty tab
  GET  /panel/admin/people/pending  → HTMX fragment: pending tab
  POST /panel/admin/people/create   → unified create (user + optional faculty profile)
  ... (edit / toggle / role / subject assignment)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app.utils.security import role_required
from app.services import admin_service
from app.extensions import db
import logging

admin_people_bp = Blueprint('admin_people', __name__,
                            template_folder='../../templates/panel')


def _is_htmx() -> bool:
    return request.headers.get('HX-Request') == 'true'


# ═══════════════════════════════════════════════════════════════════
#  PEOPLE — unified Users + Faculty page
# ═══════════════════════════════════════════════════════════════════

@admin_people_bp.route('/admin/people')
@login_required
@role_required('admin')
def admin_people():
    search = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'users')

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
    pending_users = (
        User.query.filter_by(is_active=False)
        .filter(User.last_login_at.is_(None))
        .order_by(User.created_at.asc())
        .all()
    )

    # Faculty tab data
    faculty_pagination = admin_service.get_all_faculty(
        search=search or None,
        page=page,
    )

    context = {
        'pagination': pagination,
        'users': pagination.items,
        'faculty_pagination': faculty_pagination,
        'faculty_list': faculty_pagination.items,
        'search': search,
        'role': role,
        'status': status,
        'tab': tab,
        'subjects': subjects,
        'pending_users': pending_users,
        'active_page': 'admin_people',
    }
    if _is_htmx():
        return render_template('panel/partials/admin/people.html', **context)
    return render_template('panel/pages/admin/people.html', **context)


# ── Legacy stubs (redirect old /admin/users and /admin/faculty URLs) ──

@admin_people_bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users_redirect():
    return redirect(url_for('admin_people.admin_people', tab='users'))


@admin_people_bp.route('/admin/faculty')
@login_required
@role_required('admin')
def admin_faculty_redirect():
    return redirect(url_for('admin_people.admin_people', tab='faculty'))


# ═══════════════════════════════════════════════════════════════════
#  CREATE — unified user + faculty profile form
# ═══════════════════════════════════════════════════════════════════

@admin_people_bp.route('/admin/people/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_person():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'student')
    full_name = request.form.get('full_name', '').strip() or None
    employee_id = request.form.get('employee_id', '').strip() or None
    department = request.form.get('department', '').strip() or None

    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('admin_people.admin_people'))

    try:
        user = admin_service.create_user(
            email, password, role,
            full_name=full_name,
            employee_id=employee_id,
        )
        # If faculty/admin, also update department if provided
        if department and role in ('faculty', 'admin') and user.faculty_profile:
            user.faculty_profile.department = department
            db.session.commit()
        flash(f'Person {email} created successfully as {role}.', 'success')
    except Exception as e:
        logging.error(f'Create person error: {e}')
        flash(f'Could not create person: {e}', 'error')

    return redirect(url_for('admin_people.admin_people'))


# ── Legacy stub ──

@admin_people_bp.route('/admin/users/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_user_redirect():
    """Legacy redirect — forward the POST to the new create endpoint."""
    return admin_create_person()


# ═══════════════════════════════════════════════════════════════════
#  USER MANAGEMENT actions
# ═══════════════════════════════════════════════════════════════════

@admin_people_bp.route('/admin/people/<user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_update_role(user_id):
    new_role = request.form.get('role')
    try:
        admin_service.update_user_role(user_id, new_role)
        flash(f'Role updated to {new_role}.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('admin_people.admin_people'))


@admin_people_bp.route('/admin/people/<user_id>/toggle', methods=['POST'])
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
    return redirect(url_for('admin_people.admin_people'))


@admin_people_bp.route('/admin/people/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_user(user_id):
    from app.models.user import User
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_people.admin_people'))

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
            return redirect(url_for('admin_people.admin_people'))
        except Exception as e:
            flash(f'Error: {e}', 'error')

    context = {'user': user, 'active_page': 'admin_people'}
    return render_template('panel/pages/admin/edit_user.html', **context)


# Legacy stub
@admin_people_bp.route('/admin/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_user_legacy(user_id):
    return redirect(url_for('admin_people.admin_edit_user', user_id=user_id))


@admin_people_bp.route('/admin/people/<int:faculty_id>/assign-subject', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_subject(faculty_id):
    subject_id = request.form.get('subject_id', type=int)
    try:
        admin_service.assign_subject_to_faculty(faculty_id, subject_id)
        flash('Subject assigned.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('admin_people.admin_people', tab='faculty'))


@admin_people_bp.route('/admin/people/<int:faculty_id>/subjects/<int:subject_id>/unassign', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_subject(faculty_id, subject_id):
    try:
        admin_service.remove_subject_from_faculty(faculty_id, subject_id)
        flash('Subject removed.', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('admin_people.admin_people', tab='faculty'))


# ── Faculty profile edit/delete ──

@admin_people_bp.route('/admin/people/faculty/<int:faculty_id>/edit', methods=['POST'])
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
    return redirect(url_for('admin_people.admin_people', tab='faculty'))


@admin_people_bp.route('/admin/people/faculty/<int:faculty_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_faculty(faculty_id):
    try:
        admin_service.delete_faculty_profile(faculty_id)
        flash('Faculty profile removed. The user account still exists.', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('admin_people.admin_people', tab='faculty'))


# Legacy stubs for old faculty URLs
@admin_people_bp.route('/admin/faculty/<int:faculty_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def admin_edit_faculty_legacy(faculty_id):
    return admin_edit_faculty(faculty_id)


@admin_people_bp.route('/admin/faculty/<int:faculty_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_faculty_legacy(faculty_id):
    return admin_delete_faculty(faculty_id)


@admin_people_bp.route('/admin/faculty/<int:faculty_id>/assign-subject', methods=['POST'])
@login_required
@role_required('admin')
def admin_faculty_assign_subject_legacy(faculty_id):
    return admin_assign_subject(faculty_id)


@admin_people_bp.route('/admin/faculty/<int:faculty_id>/subjects/<int:subject_id>/unassign', methods=['POST'])
@login_required
@role_required('admin')
def admin_faculty_remove_subject_legacy(faculty_id, subject_id):
    return admin_remove_subject(faculty_id, subject_id)


@admin_people_bp.route('/admin/users/<user_id>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_update_role_legacy(user_id):
    return admin_update_role(user_id)


@admin_people_bp.route('/admin/users/<user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_user_legacy(user_id):
    return admin_toggle_user(user_id)


@admin_people_bp.route('/admin/users/<int:faculty_id>/assign-subject', methods=['POST'])
@login_required
@role_required('admin')
def admin_assign_subject_legacy(faculty_id):
    return admin_assign_subject(faculty_id)


@admin_people_bp.route('/admin/faculty/<int:faculty_id>/remove-subject/<int:subject_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_remove_subject_legacy2(faculty_id, subject_id):
    return admin_remove_subject(faculty_id, subject_id)
