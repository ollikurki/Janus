# User routes
# User profile, password change, student portal, and manual access

from flask import (
    render_template, flash, redirect, url_for,
    Blueprint, request
)
from flask_login import login_required, current_user
from app.forms import ChangePasswordForm, ExcuseForm
from app.models import User, Student
from app.services import AttendanceService, AuditService, EmailService
from app import db

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/<username>')
@login_required
def user_profile(username):
    """User profile page."""
    user_obj = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title="User", user=user_obj)


@user_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password for logged-in user.
    
    Enforces password expiry: if password has expired, user must change it.
    """
    # Check if password has expired
    if current_user.check_password_expiry():
        flash('Your password has expired. Please set a new password.')
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.')
            return redirect(url_for('user.change_password'))
        
        current_user.set_password(form.new_password.data)
        current_user.update_password_changed_at()
        db.session.commit()
        AuditService.log(
            action=AuditService.PASSWORD_CHANGED,
            user_id=current_user.id,
            ip_address=request.remote_addr
        )
        flash('Password changed successfully!')
        return redirect(url_for('user.user_profile', username=current_user.username))
    
    return render_template('change_password.html', title='Change Password', form=form)


@user_bp.route('/attendance')
@login_required
def my_attendance():
    """Student portal - view own attendance history."""
    # Find the student record linked to this user
    from app.models import Person
    
    person = Person.query.filter_by(user_id=current_user.id).first()
    if not person or not person.student_id:
        flash('Student record not found for your account.')
        return redirect(url_for('main.index'))
    
    student = Student.query.get(person.student_id)
    if not student:
        flash('Student record not found.')
        return redirect(url_for('main.index'))
    
    # Get attendance records
    attendance_records = AttendanceService.get_attendance_by_student(student.id)
    
    return render_template(
        'student_portal.html',
        title='My Attendance',
        student=student,
        attendance_records=attendance_records
    )


@user_bp.route('/manual')
@login_required
def manual():
    """Redirect to appropriate manual PDF based on user role."""
    if current_user.is_admin():
        return redirect("/static/Admin_manual.pdf")
    elif current_user.is_teacher():
        return redirect("/static/Teacher_manual.pdf")
    else:
        return redirect("/")


@user_bp.route('/submit_excuse', methods=['GET', 'POST'])
@login_required
def submit_excuse():
    """Submit an attendance excuse (students only)."""
    # Find the student record linked to this user
    from app.models import Person, Excuse
    
    person = Person.query.filter_by(user_id=current_user.id).first()
    if not person or not person.student_id:
        flash('Student record not found for your account.')
        return redirect(url_for('main.index'))
    
    student = Student.query.get(person.student_id)
    if not student:
        flash('Student record not found.')
        return redirect(url_for('main.index'))
    
    form = ExcuseForm()
    
    if form.validate_on_submit():
        excuse = Excuse(
            student_id=student.id,
            date_from=form.date_from.data,
            date_to=form.date_to.data,
            reason=form.reason.data
        )
        db.session.add(excuse)
        db.session.commit()
        
        AuditService.log(
            action='excuse.submitted',
            user_id=current_user.id,
            details=f'Submitted excuse for {form.date_from.data} to {form.date_to.data}',
            ip_address=request.remote_addr
        )
        
        flash('Excuse submitted successfully.')
        return redirect(url_for('user.my_attendance'))
    
    return render_template('submit_excuse.html', title='Submit Excuse', form=form)
