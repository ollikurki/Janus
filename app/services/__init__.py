# Services package
# Business logic layer extracted from routes

from app.services.user_service import UserService
from app.services.student_service import StudentService
from app.services.attendance_service import AttendanceService
from app.services.export_service import ExportService
from app.services.email_service import EmailService, mail
from app.services.audit_service import AuditService

__all__ = [
    'UserService', 'StudentService', 'AttendanceService', 
    'ExportService', 'EmailService', 'mail', 'AuditService'
]
