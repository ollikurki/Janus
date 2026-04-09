from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
import secrets


class User(UserMixin, db.Model):
    """User account model with role-based access."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True)
    email: str = db.Column(db.String(120), index=True)
    password_hash: str = db.Column(db.String(256))
    
    # Role-based access: 1=Teacher, 2=Student, 3=Admin
    clearance: int = db.Column(db.Integer, default=1, index=True)
    group: str = db.Column(db.String(16))
    last_seen: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Password reset tokens
    reset_token: str = db.Column(db.String(64), nullable=True, index=True)
    reset_token_expires: datetime = db.Column(db.DateTime, nullable=True)
    
    # Password security
    password_changed_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Account lockout
    failed_login_attempts: int = db.Column(db.Integer, default=0)
    locked_until: datetime = db.Column(db.DateTime, nullable=True)
    
    # Activity tracking
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    persons = db.relationship('Person', cascade='all, delete-orphan', backref='user')
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.clearance == 3
    
    def is_teacher(self) -> bool:
        """Check if user is a teacher."""
        return self.clearance == 1
    
    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.clearance == 2
    
    def generate_reset_token(self) -> str:
        """Generate a secure password reset token."""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.now(timezone.utc)
        return self.reset_token
    
    def verify_reset_token(self, token: str) -> bool:
        """Verify if reset token is valid and not expired."""
        if self.reset_token != token:
            return False
        if self.reset_token_expires < datetime.now(timezone.utc):
            return False
        return True
    
    def clear_reset_token(self) -> None:
        """Clear the reset token after use."""
        self.reset_token = None
        self.reset_token_expires = None
    
    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        if datetime.now(timezone.utc) > self.locked_until:
            # Lock has expired, unlock the account
            self.locked_until = None
            self.failed_login_attempts = 0
            return False
        return True
    
    def increment_failed_attempts(self) -> None:
        """Increment failed login counter and lock if threshold reached."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 10:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    def unlock(self) -> None:
        """Manually unlock the account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def check_password_expiry(self, days: int = 90) -> bool:
        """Check if password has expired.
        
        Args:
            days: Number of days until password expires (default 90)
        
        Returns:
            bool: True if password has expired
        """
        expiry_date = self.password_changed_at + timedelta(days=days)
        return datetime.now(timezone.utc) > expiry_date
    
    def update_password_changed_at(self) -> None:
        """Update the password changed timestamp."""
        self.password_changed_at = datetime.now(timezone.utc)


class AuditLog(db.Model):
    """Audit log for tracking admin actions."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action: str = db.Column(db.String(128), nullable=False)
    details: str = db.Column(db.String(512), nullable=True)
    ip_address: str = db.Column(db.String(45), nullable=True)
    timestamp: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    user = db.relationship('User', backref='audit_logs')


class Person(db.Model):
    """Person model - links users to their personal information."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    first_name: str = db.Column(db.String(32), nullable=False)
    last_name: str = db.Column(db.String(128), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_id: int = db.Column(db.Integer, db.ForeignKey('student.id'))


class Student(db.Model):
    """Student model with group association."""
    
    id: int = db.Column(db.Integer, primary_key=True)
    group: str = db.Column(db.String(16))
    full_name: str = db.Column(db.String(160), index=True)
    group_id: int = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    attendance_records = db.relationship('Attendance', cascade='all, delete-orphan', backref='student')


class Attendance(db.Model):
    """Attendance record model.

    Status values:
        'present'  - Student was present
        'absent'   - Student was absent (unexcused)
        'excused'  - Student was absent with a valid excuse
        'late'     - Student arrived late
    """

    __table_args__ = (
        db.Index('idx_attendance_date', 'attendance'),
        db.Index('idx_attendance_student_date', 'student_id', 'attendance'),
        db.Index('idx_attendance_status', 'status'),
    )
    
    id: int = db.Column(db.Integer, primary_key=True)
    student_id: int = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    attendance: datetime = db.Column(db.Date, nullable=False, index=True)
    status: str = db.Column(db.String(16), default='present', nullable=False)
    notes: str = db.Column(db.String(500), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Groups(db.Model):
    """Group/class model for organizing students."""
    
    __table_args__ = (
        db.Index('idx_groups_marking', 'marking'),
    )
    
    id: int = db.Column(db.Integer, primary_key=True)
    marking: str = db.Column(db.String(16), unique=True, nullable=False, index=True)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    students = db.relationship('Student', cascade='all, delete-orphan', backref='group')


class Excuse(db.Model):
    """Attendance excuse model for student absences."""
    
    __table_args__ = (
        db.Index('idx_excuse_student', 'student_id'),
        db.Index('idx_excuse_dates', 'date_from', 'date_to'),
    )
    
    id: int = db.Column(db.Integer, primary_key=True)
    student_id: int = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date_from: datetime = db.Column(db.Date, nullable=False)
    date_to: datetime = db.Column(db.Date, nullable=False)
    reason: str = db.Column(db.String(500), nullable=False)
    status: str = db.Column(db.String(16), default='pending')  # pending, approved, rejected
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('Student', backref='excuses')


# ── Valid attendance statuses ──────────────────────────────────────────────────

ATTENDANCE_STATUSES = ('present', 'absent', 'excused', 'late')


def load_user(id: str) -> User:
    """Load user by ID for Flask-Login."""
    return User.query.get(int(id))
