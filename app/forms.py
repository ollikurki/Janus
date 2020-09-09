from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from app.models import User, Person, Student


#Creating a form for the login function with username and password validated to be required and an submit button.
class LoginForm(FlaskForm):
    username = StringField('Käyttäjänimi', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    submit = SubmitField('Kirjaudu sisään')

#Creating a form for the Admin users to add new users to the database.
#Clearance could be on it's own table to be queried from.
class AdministrationForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[DataRequired()])
    lastname = StringField('Sukunimi', validators=[DataRequired()])
#    username = StringField('Käyttäjätunnus', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired(), Length(min=8, message='Vähintään 8 merkkiä')])
    password2 = PasswordField('Toista salasana', validators=[DataRequired(), EqualTo('password', message='Salasanojen täytyy olla sama')])
    clearance = SelectField(u'Taso', choices=[('0', 'Admin'), ('1', 'Opettaja'), ('2', 'Oppilas')], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Luo Käyttäjä')

#Checkin if the database already has a username that is to be added.
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Valitse muu käyttäjänimi.')

#Creating the form to add students.
class StudentForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[DataRequired()])
    lastname = StringField('Sukunimi', validators=[DataRequired()])
    group = StringField('Ryhmä')
    submit = SubmitField('Lisää oppilas')

#Form for attendance logging to select a group which students are queried
class LogAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmä', choices=[('PTtvtweb3', 'TvTptweb3'), ('testiweb', 'TvTptwebtesti')], validators=[DataRequired()])
    submit = SubmitField('Valitse luokkaryhmä')

#Form for attendance checking by which group they belong to
class CheckAttendanceGroupSelectForm(FlaskForm):
    group_select = SelectField(u'Ryhmä', choices=[('PTtvtweb3', 'TvTptweb3'), ('testiweb', 'TvTptwebtesti')], validators=[DataRequired()])
    by_student = SubmitField(label='Haku oppilaiden nimi järjestyksessä')
    by_date = SubmitField(label='Haku päivämäärän mukaan laskien')

class AttendanceForm(FlaskForm):
    attendance = SelectMultipleField(u'Oppilaat', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Kirjaa läsnäolleeksi')