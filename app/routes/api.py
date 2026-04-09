# API routes
# REST API endpoints for mobile apps and third-party integrations

from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt
)
from app.services import UserService, StudentService, AttendanceService, ExportService
from app.models import User
from app import db
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# ============================================
# Authentication Endpoints
# ============================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - public."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens.
    
    Request body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        {
            "access_token": "string",
            "refresh_token": "string",
            "user": {
                "id": int,
                "username": "string",
                "clearance": int,
                "group": "string"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = UserService.get_user_by_username(username)
    
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'clearance': user.clearance,
            'group': user.group
        }
    }), 200


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token.
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        {
            "access_token": "string"
        }
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200


@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens).
    
    Note: For full logout, implement token blocklisting.
    """
    return jsonify({'message': 'Successfully logged out'}), 200


# ============================================
# User Endpoints (Admin only)
# ============================================

@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination.
    
    Query params:
        page: int (default 1)
        per_page: int (default 50)
    
    Returns:
        {
            "users": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "pages": int
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    users, total = UserService.get_all_users(page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return jsonify({
        'users': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'group': u.group
            } for u in users
        ],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': total_pages
    }), 200


@api_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin only).
    
    Request body:
        {
            "firstname": "string",
            "lastname": "string",
            "password": "string",
            "clearance": int (1=Teacher, 2=Student, 3=Admin)
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['firstname', 'lastname', 'password', 'clearance']
    if not all(field in data for field in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    user, error = UserService.create_user(
        firstname=data['firstname'],
        lastname=data['lastname'],
        password=data['password'],
        clearance=int(data['clearance'])
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'clearance': user.clearance,
            'group': user.group
        }
    }), 201


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user by ID."""
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = UserService.get_user_by_username(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'clearance': user.clearance,
            'group': user.group
        }
    }), 200


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user by ID (admin only)."""
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    UserService.delete_user(user.username)
    
    return jsonify({'message': 'User deleted successfully'}), 200


# ============================================
# Student Endpoints
# ============================================

@api_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students with pagination.
    
    Query params:
        page: int (default 1)
        per_page: int (default 50)
    
    Returns:
        {
            "students": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "pages": int
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not (current_user_obj.is_admin() or current_user_obj.is_teacher()):
        return jsonify({'error': 'Teacher or admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    students, total = StudentService.get_all_students(page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return jsonify({
        'students': [
            {
                'id': s.id,
                'full_name': s.full_name,
                'group_id': s.group_id
            } for s in students
        ],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': total_pages
    }), 200


@api_bp.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    """Create a new student (admin only).
    
    Request body:
        {
            "firstname": "string",
            "lastname": "string",
            "group_id": int
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['firstname', 'lastname', 'group_id']
    if not all(field in data for field in required):
        return jsonify({'error': f'Missing required fields: {required}'}), 400
    
    student = StudentService.create_student(
        firstname=data['firstname'],
        lastname=data['lastname'],
        group_id=int(data['group_id'])
    )
    
    return jsonify({
        'message': 'Student created successfully',
        'student': {
            'id': student.id,
            'full_name': student.full_name,
            'group_id': student.group_id
        }
    }), 201


@api_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """Get a specific student by ID."""
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not (current_user_obj.is_admin() or current_user_obj.is_teacher()):
        return jsonify({'error': 'Teacher or admin access required'}), 403
    
    student = StudentService.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'student': {
            'id': student.id,
            'full_name': student.full_name,
            'group_id': student.group_id
        }
    }), 200


# ============================================
# Attendance Endpoints
# ============================================

@api_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    """Get attendance records with optional filters.
    
    Query params:
        student_id: int (optional)
        group_id: int (optional)
        date: YYYY-MM-DD (optional)
        start_date: YYYY-MM-DD (optional)
        end_date: YYYY-MM-DD (optional)
    
    Returns:
        {
            "attendance": [...]
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not (current_user_obj.is_admin() or current_user_obj.is_teacher()):
        return jsonify({'error': 'Teacher or admin access required'}), 403
    
    student_id = request.args.get('student_id', type=int)
    group_id = request.args.get('group_id', type=int)
    date_str = request.args.get('date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if student_id:
        records = AttendanceService.get_attendance_by_student(student_id)
        attendance = [
            {
                'id': r.id,
                'student_id': r.student_id,
                'attendance': r.attendance.isoformat() if r.attendance else None,
                'status': r.status,
                'notes': r.notes
            } for r in records
        ]
    elif start_date and end_date:
        from datetime import date
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        records = AttendanceService.search_by_date_range(start, end)
        attendance = [
            {
                'id': r[0],
                'student_id': r[1],
                'student_name': r[2],
                'attendance': r[3].isoformat() if r[3] else None,
                'status': r[4] if len(r) > 4 else 'present',
                'notes': r[5] if len(r) > 5 else None
            } for r in records
        ]
    elif group_id:
        records = AttendanceService.get_attendance_by_group(group_id)
        attendance = [
            {
                'id': r[0],
                'student_id': r[1],
                'student_name': r[2],
                'attendance': r[3].isoformat() if r[3] else None,
                'status': r[4] if len(r) > 4 else 'present',
                'notes': r[5] if len(r) > 5 else None
            } for r in records
        ]
    else:
        attendance = []
    
    return jsonify({'attendance': attendance}), 200


@api_bp.route('/attendance', methods=['POST'])
@jwt_required()
def log_attendance():
    """Log attendance for students (teacher only).
    
    Request body:
        {
            "student_ids": [1, 2, 3],
            "date": "YYYY-MM-DD" (optional, defaults to today),
            "status": "present|absent|excused|late" (optional, defaults to "present"),
            "notes": "string" (optional)
        }
    
    Or for bulk with per-student status:
        {
            "records": [
                {"student_id": 1, "status": "present", "notes": "..."},
                {"student_id": 2, "status": "absent", "notes": "sick"}
            ],
            "date": "YYYY-MM-DD" (optional)
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_teacher():
        return jsonify({'error': 'Teacher access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    from datetime import date as date_type
    attendance_date = date_type.today()
    if 'date' in data:
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    # Bulk mode: per-student status
    if 'records' in data:
        from app.models import ATTENDANCE_STATUSES
        records = []
        for rec in data['records']:
            if 'student_id' not in rec:
                return jsonify({'error': 'Each record must have student_id'}), 400
            if rec.get('status') and rec['status'] not in ATTENDANCE_STATUSES:
                return jsonify({'error': f"Invalid status '{rec['status']}'. Must be one of {ATTENDANCE_STATUSES}"}), 400
            records.append({
                'student_id': rec['student_id'],
                'status': rec.get('status', 'present'),
                'notes': rec.get('notes')
            })
        created, updated, skipped = AttendanceService.log_bulk_attendance(records, attendance_date=attendance_date)
        return jsonify({
            'message': 'Attendance logged',
            'created': created,
            'updated': updated,
            'skipped': skipped
        }), 201
    
    # Simple mode: all students get same status
    if 'student_ids' not in data:
        return jsonify({'error': 'student_ids or records required'}), 400
    
    status = data.get('status', 'present')
    notes = data.get('notes')
    created, skipped = AttendanceService.log_attendance(
        data['student_ids'], attendance_date=attendance_date, status=status, notes=notes
    )
    
    return jsonify({
        'message': 'Attendance logged',
        'created': created,
        'skipped': skipped
    }), 201


# ============================================
# Group Endpoints
# ============================================

@api_bp.route('/groups', methods=['GET'])
@jwt_required()
def get_groups():
    """Get all groups."""
    from app.models import Groups
    
    groups = Groups.query.all()
    
    return jsonify({
        'groups': [
            {
                'id': g.id,
                'marking': g.marking
            } for g in groups
        ]
    }), 200


@api_bp.route('/groups', methods=['POST'])
@jwt_required()
def create_group():
    """Create a new group (admin only).
    
    Request body:
        {
            "marking": "string"
        }
    """
    current_user_obj = User.query.get(get_jwt_identity())
    if not current_user_obj or not current_user_obj.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    if not data or 'marking' not in data:
        return jsonify({'error': 'marking required'}), 400
    
    from app.models import Groups
    
    # Check if group exists
    existing = Groups.query.filter_by(marking=data['marking']).first()
    if existing:
        return jsonify({'error': 'Group already exists'}), 400
    
    group = Groups(marking=data['marking'])
    db.session.add(group)
    db.session.commit()
    
    return jsonify({
        'message': 'Group created successfully',
        'group': {
            'id': group.id,
            'marking': group.marking
        }
    }), 201
