from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from models import db
from models.user import User
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Root – redirect to appropriate dashboard or login."""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login – no self-registration. Accounts are created by admin."""
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Check if account is locked
        if user.is_locked:
            flash('Your account has been locked due to too many failed attempts. Contact an administrator.', 'danger')
            return render_template('auth/login.html')

        # Verify password
        if not user.check_password(password):
            # Increment failed attempts
            user.login_attempts += 1
            if user.login_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                user.is_locked = True
                db.session.commit()
                flash('Account locked after 3 failed attempts. Contact an administrator.', 'danger')
            else:
                db.session.commit()
                remaining = Config.MAX_LOGIN_ATTEMPTS - user.login_attempts
                flash(f'Invalid password. {remaining} attempt(s) remaining.', 'danger')
            return render_template('auth/login.html')

        # Successful login – reset attempts
        user.login_attempts = 0
        db.session.commit()

        session['user_id'] = user.user_id
        session['user_name'] = user.user_name
        session['role'] = user.role
        session['email'] = user.email
        session.permanent = True

        flash(f'Welcome back, {user.user_name}!', 'success')

        # Role-based redirect
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
