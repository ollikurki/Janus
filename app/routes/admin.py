# Admin routes
# User management, student management, group management

from flask import (
    render_template, flash, redirect, url_for,
    Blueprint, request
)
from flask_login import login_required, current_user
from app.forms import (
    AdministrationForm, StudentForm, GroupMarkingForm, 
    GetUserForm, ExcuseForm, ReportForm
)
from app.models import Groups
from app.services import UserService, StudentService, AuditService, EmailService, AttendanceService
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_main():
    """Admin dashboard."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    return render_template('admin.html', title='Admin')


@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    create_userform = AdministrationForm()
    check_userform = GetUserForm()
    
    if create_userform.user_submit.data and create_userform.validate():
        user, error = UserService.create_user(
            firstname=create_userform.firstname.data,
            lastname=create_userform.lastname.data,
            password=create_userform.password.data,
            clearance=create_userform.clearance.data
        )
        
        if error:
            flash(error)
            return redirect(url_for('admin.create_user'))
        
        AuditService.log(
            action=AuditService.USER_CREATED,
            user_id=current_user.id,
            details=f'Created user: {user.username} ({user.group})',
            ip_address=request.remote_addr
        )
        flash('User created successfully!')
        return redirect('/admin/create_user')
    
    return render_template(
        'user_management.html',
        title='User Management',
        create_userform=create_userform,
        check_userform=check_userform
    )


@admin_bp.route('/check_users', methods=['GET', 'POST'])
@login_required
def check_users():
    """Search and list users (admin only) with pagination."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    create_userform = AdministrationForm()
    check_userform = GetUserForm()
    user_list = []
    total_users = 0
    page = 1
    per_page = 50
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    
    if check_userform.get_users.data and check_userform.validate():
        user_list, total_users = UserService.get_all_users(page=page, per_page=per_page)
    elif check_userform.get_user.data and check_userform.validate():
        # Search doesn't use pagination (single result set)
        user_list = UserService.search_users(check_userform.user_name.data)
        total_users = len(user_list)
    
    # Calculate pagination info
    total_pages = (total_users + per_page - 1) // per_page if total_users > 0 else 1
    
    return render_template(
        'user_management.html',
        title='User Management',
        create_userform=create_userform,
        check_userform=check_userform,
        user_list=user_list,
        page=page,
        per_page=per_page,
        total_users=total_users,
        total_pages=total_pages
    )


@admin_bp.route('/remove_user/<name>', methods=['GET', 'POST'])
@login_required
def remove_user(name):
    """Remove a user by username (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    UserService.delete_user(name)
    AuditService.log(
        action=AuditService.USER_DELETED,
        user_id=current_user.id,
        details=f'Deleted user: {name}',
        ip_address=request.remote_addr
    )
    return redirect(url_for('admin.check_users'))


@admin_bp.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    form = StudentForm()
    form.group.choices = StudentService.get_groups()
    
    if form.validate_on_submit():
        student = StudentService.create_student(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            group_id=form.group.data
        )
        AuditService.log(
            action=AuditService.STUDENT_CREATED,
            user_id=current_user.id,
            details=f'Added student: {form.firstname.data} {form.lastname.data}',
            ip_address=request.remote_addr
        )
        # Send welcome email to new student if email is configured
        EmailService.send_welcome_email(
            to_email=f"student.{student.id}@janus.local",
            username=f"{form.firstname.data} {form.lastname.data}"
        )
        flash('Student added successfully!')
        return redirect('/admin/add_student')
    
    return render_template('student_management.html', title='Add Student', form=form)


@admin_bp.route('/add_groups', methods=['GET', 'POST'])
@login_required
def add_groups():
    """Add a new group/class (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    form = GroupMarkingForm()
    
    if form.validate_on_submit():
        marking = Groups(marking=form.marking.data)
        db.session.add(marking)
        db.session.commit()
        AuditService.log(
            action=AuditService.GROUP_CREATED,
            user_id=current_user.id,
            details=f'Created group: {form.marking.data}',
            ip_address=request.remote_addr
        )
        flash('Group added successfully!')
    
    return render_template('add_groups.html', title='Add Groups', form=form)


@admin_bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """Attendance reports and statistics (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    form = ReportForm()
    form.group_select.choices = [(0, 'All Groups')] + StudentService.get_groups()
    stats = None
    
    if form.validate_on_submit():
        group_id = form.group_select.data if form.group_select.data > 0 else None
        days = form.days.data or 30
        
        if group_id:
            stats = AttendanceService.get_group_statistics(group_id, days)
        else:
            stats = AttendanceService.get_all_groups_statistics(days)
    
    return render_template('reports.html', title='Attendance Reports', form=form, stats=stats)


@admin_bp.route('/excuses', methods=['GET', 'POST'])
@login_required
def excuses():
    """View and manage attendance excuses (admin only)."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    from app.models import Excuse
    
    # Get pending excuses
    pending_excuses = Excuse.query.filter_by(status='pending').order_by(Excuse.created_at.desc()).all()
    processed_excuses = Excuse.query.filter(Excuse.status != 'pending').order_by(Excuse.created_at.desc()).limit(50).all()
    
    return render_template(
        'excuses.html',
        title='Excuse Management',
        pending_excuses=pending_excuses,
        processed_excuses=processed_excuses
    )


@admin_bp.route('/excuses/<int:excuse_id>/approve', methods=['POST'])
@login_required
def approve_excuse(excuse_id):
    """Approve an attendance excuse."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    from app.models import Excuse
    
    excuse = Excuse.query.get_or_404(excuse_id)
    excuse.status = 'approved'
    db.session.commit()
    
    AuditService.log(
        action='excuse.approved',
        user_id=current_user.id,
        details=f'Approved excuse for student ID {excuse.student_id}',
        ip_address=request.remote_addr
    )
    
    flash('Excuse approved.')
    return redirect(url_for('admin.excuses'))


@admin_bp.route('/excuses/<int:excuse_id>/reject', methods=['POST'])
@login_required
def reject_excuse(excuse_id):
    """Reject an attendance excuse."""
    if not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    from app.models import Excuse
    
    excuse = Excuse.query.get_or_404(excuse_id)
    excuse.status = 'rejected'
    db.session.commit()
    
    AuditService.log(
        action='excuse.rejected',
        user_id=current_user.id,
        details=f'Rejected excuse for student ID {excuse.student_id}',
        ip_address=request.remote_addr
    )
    
    flash('Excuse rejected.')
    return redirect(url_for('admin.excuses'))
