# Audit Service
# Logging admin actions for security and compliance

from typing import Optional
from datetime import datetime, timezone
from app.models import AuditLog, User
from app import db


class AuditService:
    """Service for audit logging."""
    
    # Action types
    USER_CREATED = 'user.created'
    USER_DELETED = 'user.deleted'
    USER_LOGIN = 'user.login'
    USER_LOGIN_FAILED = 'user.login_failed'
    USER_LOGOUT = 'user.logout'
    PASSWORD_CHANGED = 'password.changed'
    PASSWORD_RESET_REQUESTED = 'password.reset_requested'
    PASSWORD_RESET_COMPLETED = 'password.reset_completed'
    STUDENT_CREATED = 'student.created'
    ATTENDANCE_LOGGED = 'attendance.logged'
    GROUP_CREATED = 'group.created'
    
    @staticmethod
    def log(
        action: str,
        user_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry.
        
        Args:
            action: Action type (use AuditService constants)
            user_id: ID of user performing action
            details: Additional details about the action
            ip_address: IP address of the request
        
        Returns:
            AuditLog: The created audit log entry
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @staticmethod
    def get_recent_logs(limit: int = 100) -> list:
        """Get recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
        
        Returns:
            list: Recent audit logs
        """
        return AuditLog.query.order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_logs_by_user(user_id: int, limit: int = 100) -> list:
        """Get audit logs for a specific user.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of logs to return
        
        Returns:
            list: Audit logs for the user
        """
        return AuditLog.query.filter_by(
            user_id=user_id
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_logs_by_action(action: str, limit: int = 100) -> list:
        """Get audit logs by action type.
        
        Args:
            action: Action type to filter by
            limit: Maximum number of logs to return
        
        Returns:
            list: Audit logs for the action
        """
        return AuditLog.query.filter_by(
            action=action
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()
