from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.services import auth_service
from app.models.user import User
from app.extensions import db
from datetime import datetime, timezone
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
                # First-time login: create local User record
                role = (sb_user.user_metadata or {}).get('role', 'student')
                user = User(
                    id=str(sb_user.id),
                    email=sb_user.email,
                    role=role,
                )
                db.session.add(user)

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


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Faculty self-registration."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        employee_id = request.form.get('employee_id', '').strip() or None

        if not email or not password or not full_name:
            flash('Email, full name, and password are required.', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/register.html')

        try:
            response = auth_service.sign_up(email, password, role='faculty')
            sb_user = response.user

            from app.models.faculty import Faculty
            user = User(
                id=str(sb_user.id),
                email=sb_user.email,
                role='faculty',
                is_active=True,
            )
            db.session.add(user)

            faculty = Faculty(
                user_id=str(sb_user.id),
                full_name=full_name,
                employee_id=employee_id,
                department='CICT',
            )
            db.session.add(faculty)
            db.session.commit()

            flash('Registration successful! Please check your email to confirm your account, then log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            logging.warning(f'Faculty registration failure for {email}: {e}')
            flash('Registration failed. This email may already be registered.', 'error')

    return render_template('auth/register.html')
