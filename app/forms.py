from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, SelectMultipleField, DateField, EmailField, TextAreaField, IntegerField
)
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length, Email, Optional
from app.models import User, Person, Student
from app.models import Groups


def groups_query():
    """Query all groups for form choices."""
    groups = Groups.query.all()
    return [(g.id, g.marking) for g in groups]


class LoginForm(FlaskForm):
    """Login form for user authentication."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AdministrationForm(FlaskForm):
    """Form for creating new users (admin only)."""
    firstname = StringField(
        'First Name',
        validators=[DataRequired(), Length(max=32, message='Maximum 32 characters')]
    )
    lastname = StringField(
        'Last Name',
        validators=[DataRequired(), Length(max=128, message='Maximum 128 characters')]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='At least 8 characters required')
        ]
    )
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    clearance = SelectField(
        'Role',
        choices=[("3", 'Admin'), ('1', 'Teacher'), ('2', 'Student')],
        coerce=int,
        validators=[DataRequired()]
    )
    user_submit = SubmitField(label='Create User')
    get_users = SubmitField(label='Search Users')


class StudentForm(FlaskForm):
    """Form for adding new students."""
    firstname = StringField(
        'First Name',
        validators=[DataRequired(), Length(max=32)]
    )
    lastname = StringField(
        'Last Name',
        validators=[DataRequired(), Length(max=128)]
    )
    group = SelectField('Group', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Student')


class LogAttendanceGroupSelectForm(FlaskForm):
    """Form for selecting group to log attendance."""
    group_select = SelectField('Group', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Select Group')


class CheckAttendanceGroupSelectForm(FlaskForm):
    """Form for checking attendance records."""
    group_select = SelectField('Group Search', coerce=int, validators=[DataRequired()])
    by_student = SubmitField(label='By Name')
    by_date = SubmitField(label='By Date')
    by_name = SubmitField(label='Search Student')
    student_name = StringField('Student Name', validators=[Length(max=160)])
    specific_date_start = DateField('Start Date')
    specific_date_end = DateField('End Date')
    by_specific_date = SubmitField(label='Search by Date Range')


class AttendanceForm(FlaskForm):
    """Form for recording attendance."""
    attendance = SelectMultipleField('Students', coerce=int, validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('excused', 'Excused'),
            ('late', 'Late')
        ],
        default='present',
        validators=[DataRequired()]
    )
    notes = TextAreaField('Notes', validators=[Length(max=500)], render_kw={"placeholder": "Optional notes"})
    submit = SubmitField(label='Mark Attendance')


class GroupMarkingForm(FlaskForm):
    """Form for creating groups."""
    marking = StringField(
        'Group Name',
        validators=[DataRequired(), Length(max=16, message='Maximum 16 characters')]
    )
    submit = SubmitField(label='Add Group')


class ExcuseForm(FlaskForm):
    """Form for submitting attendance excuse."""
    student_name = StringField(
        'Student Name',
        validators=[DataRequired(), Length(max=160)]
    )
    date_from = DateField('From Date', validators=[DataRequired()])
    date_to = DateField('To Date', validators=[DataRequired()])
    reason = TextAreaField(
        'Reason for Absence',
        validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField('Submit Excuse')


class ReportForm(FlaskForm):
    """Form for generating attendance reports."""
    group_select = SelectField('Group', coerce=int, validators=[Optional()])
    days = IntegerField(
        'Days to Include',
        default=30,
        validators=[Optional()]
    )
    submit = SubmitField('Generate Report')


class GetUserForm(FlaskForm):
    """Form for searching users."""
    get_users = SubmitField(label='Get All Users')
    user_name = StringField('Username', validators=[Length(max=161)])
    get_user = SubmitField(label='Search User')


class ChangePasswordForm(FlaskForm):
    """Form for changing password while logged in."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=8, message='At least 8 characters required')
        ]
    )
    new_password2 = PasswordField(
        'Repeat New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')]
    )
    submit = SubmitField('Change Password')


class BulkAttendanceForm(FlaskForm):
    """Form for bulk attendance marking with per-student status.

    This form is built dynamically in the route handler — the fields below
    are only the static parts. Per-student status/notes fields are added at
    render time via FieldList or directly in the template.
    """
    attendance_date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Save Attendance')


class PasswordResetRequestForm(FlaskForm):
    """Form for requesting password reset."""
    email = EmailField(
        'Email Address',
        validators=[DataRequired(), Email(message='Invalid email address')]
    )
    submit = SubmitField('Request Password Reset')


class PasswordResetForm(FlaskForm):
    """Form for resetting password with token."""
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=8, message='At least 8 characters required')
        ]
    )
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Reset Password')



