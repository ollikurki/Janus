# Attendance routes
# Log, check, and export attendance records

from flask import (
    render_template, flash, redirect, url_for,
    Blueprint, request, session
)
from flask_login import login_required, current_user
from app.forms import (
    LogAttendanceGroupSelectForm, CheckAttendanceGroupSelectForm,
    AttendanceForm, ReportForm, BulkAttendanceForm
)
from app.services import AttendanceService, ExportService, StudentService, AuditService
from app.models import Groups, ATTENDANCE_STATUSES
from app import db
from datetime import date

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/', methods=['GET', 'POST'])
@login_required
def attendance_main():
    """Attendance management main page (teachers only)."""
    if not current_user.is_teacher():
        flash('Unauthorized access!')
        return redirect('/')
    return render_template('attendance.html', title='Attendance Management')


@attendance_bp.route('/group_select', methods=['GET', 'POST'])
@login_required
def group_select():
    """Select a group to log attendance (teachers only)."""
    if not current_user.is_teacher():
        flash('Unauthorized access!')
        return redirect('/')
    
    form = LogAttendanceGroupSelectForm()
    form.group_select.choices = StudentService.get_groups()
    
    if form.validate_on_submit():
        students = StudentService.get_students_by_group(form.group_select.data)
        session['student_list'] = [(s.id, s.full_name) for s in students]
        return redirect('/attendance/log_attendance')
    
    return render_template('group_select.html', title='Select Group', form=form)


@attendance_bp.route('/log_attendance', methods=['GET', 'POST'])
@login_required
def log_attendance():
    """Log attendance for selected students (teachers only)."""
    if not current_user.is_teacher():
        flash('Unauthorized access!')
        return redirect('/')
    
    student_list = session.get('student_list', [])
    
    if not student_list:
        flash('Please select a group first.')
        return redirect('/attendance/group_select')
    
    form = AttendanceForm()
    form.attendance.choices = student_list
    
    if form.attendance.data and form.validate_on_submit():
        status = form.status.data
        notes = form.notes.data or None
        created, skipped = AttendanceService.log_attendance(
            form.attendance.data, status=status, notes=notes
        )
        AuditService.log(
            action=AuditService.ATTENDANCE_LOGGED,
            user_id=current_user.id,
            details=f'Logged attendance: {created} {status}, {skipped} skipped',
            ip_address=request.remote_addr
        )
        flash(f'Attendance recorded! Created: {created} ({status}), Skipped (already exists): {skipped}')
        session.pop('student_list', None)
    
    return render_template(
        'log_attendance.html',
        title='Log Attendance',
        form=form,
        sizelength=len(student_list)
    )


@attendance_bp.route('/bulk_attendance', methods=['GET', 'POST'])
@login_required
def bulk_attendance():
    """Bulk attendance marking with per-student status (teachers only).

    Shows all students in a group with individual status dropdowns
    (present/absent/excused/late) and optional notes fields.
    """
    if not current_user.is_teacher():
        flash('Unauthorized access!')
        return redirect('/')

    form = BulkAttendanceForm()

    # GET: show group selector if no group chosen yet
    group_id = request.args.get('group_id', type=int) or request.form.get('group_id', type=int)
    if not group_id:
        groups = StudentService.get_groups()
        form = LogAttendanceGroupSelectForm()
        form.group_select.choices = groups
        return render_template(
            'group_select.html',
            title='Select Group for Bulk Attendance',
            form=form,
            bulk_mode=True,
            groups=groups
        )

    students = StudentService.get_students_by_group(group_id)

    if request.method == 'POST':
        attendance_date = form.attendance_date.data or date.today()
        records = []

        for student in students:
            status = request.form.get(f'status_{student.id}', 'present')
            notes = request.form.get(f'notes_{student.id}', '').strip() or None
            if status in ATTENDANCE_STATUSES:
                records.append({
                    'student_id': student.id,
                    'status': status,
                    'notes': notes
                })

        if records:
            created, updated, skipped = AttendanceService.log_bulk_attendance(
                records, attendance_date=attendance_date
            )
            AuditService.log(
                action=AuditService.ATTENDANCE_LOGGED,
                user_id=current_user.id,
                details=f'Bulk attendance: {created} created, {updated} updated, {skipped} skipped',
                ip_address=request.remote_addr
            )
            flash(f'Attendance saved! Created: {created}, Updated: {updated}, Skipped: {skipped}')
            return redirect(url_for('attendance.bulk_attendance', group_id=group_id))

    # Pre-fill existing attendance for today
    existing = {}
    for student in students:
        record = AttendanceService._record_exists(student.id, date.today())
        if record:
            existing[student.id] = {'status': record.status, 'notes': record.notes or ''}

    return render_template(
        'log_attendance.html',
        title='Bulk Attendance',
        form=form,
        students=students,
        existing=existing,
        statuses=ATTENDANCE_STATUSES,
        group_id=group_id,
        bulk_mode=True
    )


@attendance_bp.route('/check_attendance', methods=['GET', 'POST'])
@login_required
def check_attendance():
    """Check and search attendance records (teachers only)."""
    if not current_user.is_teacher():
        flash('Unauthorized access!')
        return redirect('/')
    
    form = CheckAttendanceGroupSelectForm()
    form.group_select.choices = StudentService.get_groups()
    result_list = []
    
    if form.validate_on_submit():
        group_id = form.group_select.data
        
        if form.by_date.data:
            result_list = AttendanceService.get_attendance_by_group(group_id)
            flash('Attendance sorted by date!')
        
        elif form.by_student.data:
            result_list = AttendanceService.get_attendance_by_group(group_id)
            # Sort by name in the template or reorder
            result_list = sorted(result_list, key=lambda x: x[2])  # Sort by full_name
            flash('Attendance sorted by name!')
        
        elif form.by_name.data:
            result_list = AttendanceService.search_by_name(form.student_name.data)
        
        elif form.by_specific_date.data:
            result_list = AttendanceService.search_by_date_range(
                form.specific_date_start.data,
                form.specific_date_end.data
            )
    
    return render_template(
        'check_attendance.html',
        title="Check Attendance",
        form=form,
        list=result_list
    )


@attendance_bp.route('/export', methods=['GET', 'POST'])
@login_required
def export_attendance():
    """Export attendance records to CSV or PDF."""
    if not current_user.is_teacher() and not current_user.is_admin():
        flash('Unauthorized access!')
        return redirect('/')
    
    # Get query parameters
    group_id = request.args.get('group_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format_type = request.args.get('format', 'csv')
    
    # Get group name for PDF header
    group_name = None
    if group_id:
        group = Groups.query.get(group_id)
        if group:
            group_name = group.marking
    
    if format_type == 'pdf':
        return ExportService.export_attendance_pdf(group_id, start_date, end_date, group_name)
    else:
        return ExportService.export_attendance_csv(group_id, start_date, end_date)


@attendance_bp.route('/reports', methods=['GET', 'POST'])
@login_required
def attendance_reports():
    """View attendance statistics (teachers)."""
    if not current_user.is_teacher() and not current_user.is_admin():
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
    
    return render_template('attendance_reports.html', title='Attendance Reports', form=form, stats=stats)
