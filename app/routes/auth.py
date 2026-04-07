# Authentication routes
# Login, logout, password reset, and related functionality

from flask import (
    render_template, flash, redirect, url_for,
    Blueprint, request
)
from flask_login import current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.forms import (
    LoginForm, PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm
)
from app.models import User
from app.services import AuditService
from app import db, limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_rate_limit():
    """Get rate limit for login attempts."""
    return "5 per minute"


@auth_bp.route('/login', methods=["GET", "POST"])
@limiter.limit("5 per minute", error_message="Too many login attempts. Please try again later.")
def login():
    """Login page - authenticates users."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if account is locked
        if user and user.is_locked():
            AuditService.log(
                action=AuditService.USER_LOGIN_FAILED,
                user_id=user.id,
                details='Account locked',
                ip_address=request.remote_addr
            )
            flash('Account is temporarily locked due to too many failed attempts. Please try again later.')
            return redirect(url_for('auth.login'))
        
        if user is None or not user.check_password(form.password.data):
            if user:
                user.increment_failed_attempts()
                db.session.commit()
                AuditService.log(
                    action=AuditService.USER_LOGIN_FAILED,
                    user_id=user.id,
                    details='Invalid password',
                    ip_address=request.remote_addr
                )
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        login_user(user)
        
        AuditService.log(
            action=AuditService.USER_LOGIN,
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        # Check password expiry
        if user.check_password_expiry():
            flash('Your password has expired. Please change it now.')
            return redirect(url_for('user.change_password'))
        
        next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    if current_user.is_authenticated:
        AuditService.log(
            action=AuditService.USER_LOGOUT,
            user_id=current_user.id,
            ip_address=request.remote_addr
        )
    logout_user()
    return redirect('/')


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            AuditService.log(
                action=AuditService.PASSWORD_RESET_REQUESTED,
                user_id=user.id,
                details=f'Reset requested for email: {form.email.data}',
                ip_address=request.remote_addr
            )
            flash('Password reset instructions have been sent to your email.')
        else:
            # Don't reveal if user exists
            flash('If an account with that email exists, instructions have been sent.')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.')
        return redirect(url_for('auth.reset_password_request'))
    
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.update_password_changed_at()
        user.clear_reset_token()
        db.session.commit()
        
        AuditService.log(
            action=AuditService.PASSWORD_RESET_COMPLETED,
            user_id=user.id,
            ip_address=request.remote_addr
        )
        
        flash('Password has been reset. Please sign in.')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form, token=token)
