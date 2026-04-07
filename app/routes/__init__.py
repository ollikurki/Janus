# Routes package
# Split from monolithic routes.py into feature-based blueprints

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.attendance import attendance_bp
from app.routes.user import user_bp
from app.routes.api import api_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp', 'attendance_bp', 'user_bp', 'api_bp']
