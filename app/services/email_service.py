# Email Service
# Email notifications for password reset and other alerts

import os
from typing import Optional
from flask import Flask
from flask_mail import Mail, Message


mail = Mail()


def init_mail(app: Flask) -> None:
    """Initialize Flask-Mail with app configuration."""
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', '')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@janus.local')
    mail.init_app(app)


class EmailService:
    """Service for sending email notifications."""
    
    @staticmethod
    def send_password_reset_email(to_email: str, username: str, reset_url: str) -> bool:
        """Send password reset email to user.
        
        Args:
            to_email: User's email address
            username: User's username
            reset_url: Password reset URL
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not EmailService._is_configured():
            print(f"[EMAIL STUB] Password reset email to {to_email}: {reset_url}")
            return True  # Stub mode - pretend success
        
        try:
            msg = Message(
                subject="Password Reset Request - Janus",
                recipients=[to_email],
                body=f"""
Hello {username},

You requested a password reset for your Janus account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email.

Best regards,
Janus Attendance Management System
                """
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
    
    @staticmethod
    def send_welcome_email(to_email: str, username: str) -> bool:
        """Send welcome email to new user.
        
        Args:
            to_email: User's email address
            username: User's username
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not EmailService._is_configured():
            print(f"[EMAIL STUB] Welcome email to {to_email}")
            return True
        
        try:
            msg = Message(
                subject="Welcome to Janus - Attendance Management System",
                recipients=[to_email],
                body=f"""
Hello {username},

Welcome to Janus Attendance Management System!

Your account has been created successfully. You can now log in using your credentials.

If you have any questions, please contact your administrator.

Best regards,
Janus Attendance Management System
                """
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
    
    @staticmethod
    def _is_configured() -> bool:
        """Check if email is properly configured."""
        return bool(os.environ.get('MAIL_SERVER'))
