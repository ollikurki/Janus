from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from app.models import User, Person, Student
from app.models import Groups

#Database query to be used by the add_studen() function in routes.py
#the student group_select() function could use something like this too instead of a global variable
def groups_query():
    groups_query = Groups.query.all()
    result = [(x.id, x.marking) for x in groups_query]
    return result

#Form for the login() function in routes.py
class LoginForm(FlaskForm):
    username = StringField('Käyttäjänimi', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    submit = SubmitField('Kirjaudu sisään')

#Form for the create_user() function in routes.py
class AdministrationForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[DataRequired(), Length(max=32, message='max 32 merkkiä')])
    lastname = StringField('Sukunimi', validators=[DataRequired(), Length(max=128, message='max 128 merkkiä')])
#    username = StringField('Käyttäjätunnus', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired(), Length(min=8, message='Vähintään 8 merkkiä')])
    password2 = PasswordField('Toista salasana', validators=[DataRequired(), EqualTo('password', message='Salasanojen täytyy olla sama')])
#pitää clearancessa muuttaa admin taso 0 -> jokin muu, esim 3.. ohjelma taitaa ymmärtää 0 "null"ina
    clearance = SelectField(u'Taso', choices=[("3", 'Admin'), ('1', 'Opettaja'), ('2', 'Oppilas')], coerce=int, validators=[DataRequired()])
    user_submit = SubmitField(label='Luo Käyttäjä')
    get_users = SubmitField(label='Hae käyttäjät')

#Checkin if the database already has a username that is to be added.
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Valitse muu käyttäjänimi.')

#Form for the add_student() function in routes.py
class StudentForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[DataRequired(), Length(max=32, message='max 32 merkkiä')])
    lastname = StringField('Sukunimi', validators=[DataRequired(), Length(max=128, message='max 128 merkkiä')])
    group = SelectField(u'Ryhmä', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Lisää oppilas')

#Form for the group_select() function in routes.py
class LogAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmä', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Valitse luokkaryhmä')

#Form for the attendance_check() function in routes.py
class CheckAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmähaku', coerce=int, validators=[DataRequired()])
    by_student = SubmitField(label='Nimijärjestyksessä')
    by_date = SubmitField(label='Päivämäärä laskien')
    by_name = SubmitField(label='Hae oppilas')
    student_name = StringField(u'Oppilas', validators=[Length(max=160, message='max 160 merkkiä')])
    specific_date_start = StringField(u'Alku päivämäärä', validators=[Length(max=12, message='max 12 merkkiä')])
    specific_date_end = StringField(u'Loppu päivämäärä', validators=[Length(max=12, message='max 12 merkkiä')])
    by_specific_date = SubmitField(label='Hae päivämäärä')

#Form for the attendance_selection() function in routes.py
class AttendanceForm(FlaskForm):
    attendance = SelectMultipleField(u'Oppilaat', coerce=int, validators=[DataRequired()])
    submit = SubmitField(label='Kirjaa läsnäolleeksi')

#Form for add_groups() function in routes.py
class GroupMarkingForm(FlaskForm):
    marking = StringField('Luokkaryhmä', validators=[DataRequired(), Length(max=16, message='max 16 merkkiä')])
    submit = SubmitField(label='Lisää luokkaryhmä')

#Form for the create_user() and check_user() functions in routes.py
class GetUserForm(FlaskForm):
    get_users = SubmitField(label='Hae kaikki käyttäjät')
    user_name = StringField(u'Käyttäjä', validators=[Length(max=161, message='max 161 merkkiä')])
    get_user = SubmitField(label='Hae käyttäjä')



