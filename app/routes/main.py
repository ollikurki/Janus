# Main routes
# Index, dashboard, and shared functionality

from flask import (
    render_template, Blueprint
)
from flask_login import login_required, current_user
from app.models import User, Groups
from app.services import AttendanceService, StudentService
from app import db
from datetime import date

main_bp = Blueprint('main', __name__)


@main_bp.before_request
def before_request():
    """Update last seen timestamp for authenticated users."""
    if current_user.is_authenticated:
        current_user.last_seen = db.func.now()
        db.session.commit()


@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    """Home page - displays dashboard with stats."""
    with open('version_history.txt') as file:
        content = file.read()
    
    # Get stats for dashboard
    stats = {}
    if current_user.is_admin():
        stats['total_users'] = User.query.count()
        stats['total_students'] = StudentService.get_student_count()
        stats['total_groups'] = Groups.query.count()
        stats['today_attendance'] = AttendanceService.get_today_attendance_count()
        stats['recent_users'] = User.query.order_by(
            User.created_at.desc()
        ).limit(5).all()
    elif current_user.is_teacher():
        stats['assigned_groups'] = Groups.query.count()
        stats['today_attendance'] = AttendanceService.get_today_attendance_count()
    
    return render_template('index.html', title='Home', version=content, stats=stats)
