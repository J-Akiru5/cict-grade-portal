from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.services import auth_service, email_service
from app.models.user import User
from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
import logging

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('auth/login.html')

        try:
            response = auth_service.sign_in(email, password)
            sb_user = response.user
            session_data = response.session

            # Sync with local User record
            user = db.session.get(User, str(sb_user.id))
            if user is None:
                role = (sb_user.user_metadata or {}).get('role', 'student')
                # If local email exists (legacy/mismatched id), reuse it.
                user = User.query.filter_by(email=sb_user.email).first()
                if user is None:
                    # First-time login: create local User record
                    user = User(
                        id=str(sb_user.id),
                        email=sb_user.email,
                        role=role,
                    )
                    db.session.add(user)

            # Registration requires admin approval before first login.
            if not user.is_active:
                if session_data and getattr(session_data, 'access_token', None):
                    try:
                        auth_service.sign_out(session_data.access_token)
                    except Exception:
                        pass
                flash('Your account is pending admin approval.', 'warning')
                return render_template('auth/login.html')

            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()

            # Store access token for Supabase calls
            session['sb_access_token'] = session_data.access_token
            session['sb_refresh_token'] = session_data.refresh_token

            login_user(user, remember=False)
            flash(f'Welcome back, {user.email}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return _redirect_by_role(user.role)

        except Exception as e:
            logging.warning(f'Login failure for {email}: {e}')
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    token = session.pop('sb_access_token', None)
    if token:
        try:
            auth_service.sign_out(token)
        except Exception:
            pass

    session.pop('sb_refresh_token', None)
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))


def _redirect_by_role(role: str):
    """Redirect to the appropriate dashboard based on user role."""
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    elif role in ('faculty', 'admin'):
        return redirect(url_for('panel.dashboard'))
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request a password reset link."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('auth/forgot_password.html')

        try:
            redirect_to = url_for('auth.reset_password', _external=True)
            auth_service.reset_password(email, redirect_to)
        except Exception as e:
            logging.warning(f'Password reset request failed for {email}: {e}')
        # Always show success to prevent email enumeration
        flash('If an account with that email exists, a password reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Set a new password using the token from the reset email."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    access_token = request.args.get('access_token') or request.form.get('access_token', '')

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not access_token:
            flash('Invalid or expired reset link. Please request a new one.', 'error')
            return redirect(url_for('auth.forgot_password'))

        if not password or len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/reset_password.html', access_token=access_token)

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', access_token=access_token)

        try:
            auth_service.update_password(access_token, password)
            flash('Your password has been reset. Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logging.warning(f'Password reset failed: {e}')
            flash('Reset link is invalid or expired. Please request a new one.', 'error')
            return redirect(url_for('auth.forgot_password'))

    if not access_token:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))

    return render_template('auth/reset_password.html', access_token=access_token)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Student/faculty self-registration."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'student').strip()
        employee_id = request.form.get('employee_id', '').strip() or None
        student_id = request.form.get('student_id', '').strip() or None

        if role not in ('student', 'faculty'):
            flash('Invalid role selection.', 'error')
            return render_template('auth/register.html')

        if not email or not password or not full_name:
            flash('Email, full name, and password are required.', 'error')
            return render_template('auth/register.html')

        if role == 'student' and not student_id:
            flash('Student ID is required for student registration.', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/register.html')

        existing_local_user = User.query.filter_by(email=email).first()
        if existing_local_user and existing_local_user.is_active:
            flash('This email is already registered. Please log in instead.', 'error')
            return render_template('auth/register.html')

        try:
            response = auth_service.sign_up(
                email,
                password,
                role=role,
            )
            sb_user = response.user

            if sb_user is None:
                flash('Registration could not be completed right now. Please try again shortly.', 'error')
                return render_template('auth/register.html')

            user = User.query.filter_by(email=sb_user.email).first()
            if user is None:
                user = User(
                    id=str(sb_user.id),
                    email=sb_user.email,
                    role=role,
                    is_active=False,
                )
                db.session.add(user)
            else:
                if user.role != role:
                    flash(f'This email is already registered as {user.role}.', 'error')
                    return render_template('auth/register.html')
                user.is_active = False

            if role == 'faculty':
                from app.models.faculty import Faculty
                if not user.faculty_profile:
                    profile = Faculty(
                        user_id=user.id,
                        full_name=full_name,
                        employee_id=employee_id,
                        department='CICT',
                    )
                    db.session.add(profile)
            else:
                from app.models.student import Student
                if not user.student_profile:
                    profile = Student(
                        user_id=user.id,
                        full_name=full_name,
                        student_id=student_id,
                    )
                    db.session.add(profile)

            db.session.commit()

            # Best-effort notification — does not block registration if email fails
            notification_html = (
                '<p>Hello,</p>'
                '<p>Your registration for the <strong>CICT Grade Portal</strong> has been received.</p>'
                '<p>Your account is currently pending admin approval. '
                'You will be notified once your account has been activated.</p>'
            )
            notification_text = (
                'Hello,\n\nYour CICT Grade Portal registration has been received.\n'
                'Your account is pending admin approval.'
                ' You will be notified once activated.'
            )
            email_service.send_resend_email(
                to_email=email,
                subject='CICT Grade Portal – Registration Received',
                html=notification_html,
                text=notification_text,
            )

            flash('Registration submitted. Please wait for admin approval before logging in.', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError:
            db.session.rollback()
            flash('This email is already registered. Please log in instead.', 'error')
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Registration failure for {email} ({role}): {e}')
            err = str(e).lower()
            if 'rate limit' in err:
                flash('Too many registration attempts. Please wait a few minutes and try again.', 'error')
            elif 'invalid api key' in err:
                flash(
                    'Registration service misconfigured: invalid Supabase service key. '
                    'Please contact admin to update SUPABASE_SERVICE_KEY.',
                    'error'
                )
            elif 'already registered' in err:
                flash('Registration failed. This email is already registered.', 'error')
            else:
                flash(f'Registration failed: {e}', 'error')

    return render_template('auth/register.html')
