from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from app.models import User, Person, Student
from app.models import Groups


def groups_query():
    groups_query = Groups.query.all()
    result = [(x.id, x.marking) for x in groups_query]
    return result

#Creating a form for the login function with username and password validated to be required and an submit button.
class LoginForm(FlaskForm):
    username = StringField('Käyttäjänimi', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    submit = SubmitField('Kirjaudu sisään')

#Creating a form for the Admin users to add new users to the database.
#Clearance could be on it's own table to be queried from.
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

#Creating the form to add students.
class StudentForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[DataRequired(), Length(max=32, message='max 32 merkkiä')])
    lastname = StringField('Sukunimi', validators=[DataRequired(), Length(max=128, message='max 128 merkkiä')])
    group = SelectField(u'Ryhmä', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Lisää oppilas')

#, choices=[('PTtvtweb3', 'TvTptweb3'), ('testiweb', 'TvTptwebtesti')]
#Form for attendance logging to select a group which students are queried
class LogAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmä', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Valitse luokkaryhmä')

#Form for attendance checking by which group they belong to
class CheckAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmä', coerce=int, validators=[DataRequired()])
    by_student = SubmitField(label='Haku oppilaiden nimi järjestyksessä')
    by_date = SubmitField(label='Haku päivämäärän mukaan laskien')

#Form for logging attendance of students
class AttendanceForm(FlaskForm):
    attendance = SelectMultipleField(u'Oppilaat', coerce=int, validators=[DataRequired()])
    submit = SubmitField(label='Kirjaa läsnäolleeksi')

class GroupMarkingForm(FlaskForm):
    marking = StringField('Luokkaryhmä', validators=[DataRequired(), Length(max=16, message='max 16 merkkiä')])
    submit = SubmitField(label='Lisää luokkaryhmä')

class GetUserForm(FlaskForm):
    get_users = SubmitField(label='Hae käyttäjät')



