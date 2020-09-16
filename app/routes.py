from flask import render_template, flash, redirect, request, url_for
from app import app
from app.forms import LoginForm, AdministrationForm, StudentForm, LogAttendanceGroupSelectForm, CheckAttendanceGroupSelectForm, AttendanceForm, GroupMarkingForm, groups_query, GetUserForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Person, Student, Attendance, Groups
from werkzeug.urls import url_parse
from app import db
from datetime import datetime, date

#global variable list for the attendance system.. should be a different mechanism, but I just want to get the app to work first..
#maybe a dump file to replace this
student_list = []

#logging the current time for the user that is logged in
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(tz=None)
        db.session.commit()

#setting the base route for the pages
@app.route('/')

#defining the index page to be only for those that are logged in
@app.route('/index')
@login_required
def index():
    with open('version_history.txt') as file:
        content = file.read()
    return render_template('index.html', title='Koti', version=content)

#route for the login page
#login function that checks if the user is already logged in and redirecting them to the index page if so
#if the user is not logged in the login form is rendered and the user authenticated by checking the db
#loggin in the user using flask_login
#after loggin in the user is forwarded to the next page or the index page
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
#        if current_user.clearance == 0:
#            next_page = url_for('admin_main')
#        elif current_user.clearance == 1:
#            next_page = url_for('attendance_main')
#        else:
        next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Kirjaudu sisään', form=form)

#route and function for loggin out using flask_login
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')

#a user creation route and function as it was before testing new things
#@app.route('/create_user', methods=['GET', 'POST'])
#@login_required
#def create_user():
#    if current_user.is_authenticated:
#        form = AdministrationForm()
#        if form.validate_on_submit():
#            user = User(username=form.username.data, clearance=form.clearance.data, group=form.group.data)
#            user.set_password(form.password.data)
#            db.session.add(user)
#            db.session.flush()
#            person = Person(first_name=form.firstname.data, last_name=form.lastname.data, user_id=user.id)
#            db.session.add(person)
#            db.session.commit()
#            flash('Uusi käyttäjä luotu!')
#            return redirect('/create_user')
#        return render_template('user_management.html', title='Hallinto', form=form)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_main():
    if current_user.is_authenticated and current_user.clearance == 3:
#        if current_user.clearance == 0:
        return render_template('admin.html', title='Admin')
    else:
        flash('Luvaton pääsy!')
        return redirect('/')




#user creation route and function
#fetching the form data and submitting it to the db
#user data is flushed to the db before person data for the id of users to be available for insertion to user_id column
@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.is_authenticated and current_user.clearance == 3:
#        if current_user.clearance == 0:
        create_userform = AdministrationForm()
        check_userform = GetUserForm()
        if create_userform.user_submit.data and create_userform.validate():
            if create_userform.clearance.data == 1:
                group = 'Opettaja'
            elif create_userform.clearance.data == 2:
                group = 'Oppilas'
            elif create_userform.clearance.data == 3:
                group = 'Admin'
            user = User(username=create_userform.lastname.data+'.'+create_userform.firstname.data, clearance=create_userform.clearance.data, group=group)
            check_user = User.query.filter_by(username=create_userform.lastname.data+'.'+create_userform.firstname.data).first()
            if check_user is None:
                user.set_password(create_userform.password.data)
                db.session.add(user)
                db.session.flush()
                person = Person(first_name=create_userform.firstname.data, last_name=create_userform.lastname.data, user_id=user.id)
                db.session.add(person)
                db.session.commit()
                flash('Uusi käyttäjä luotu!')
                return redirect('/admin/create_user')
            else:
                flash('Hupsista, käyttäjätunnuksessa tai salasanassa on vikaa. Valitse jokin muu tunnus.')
                return redirect(url_for('create_user'))
        return render_template('user_management.html', title='Käyttäjänhallinta', create_userform=create_userform, check_userform=check_userform)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

@app.route('/admin/check_users', methods=['GET', 'POST'])
@login_required
def check_users():
    if current_user.is_authenticated and current_user.clearance == 3:
        create_userform = AdministrationForm()
        check_userform = GetUserForm()
        def list():
            if check_userform.get_users.data and check_userform.validate():
                users = db.session.query(User.id, User.username, User.group).order_by(User.id.asc())
                users_list = [(user.id, user.username, user.group) for user in users]
                return(users_list)
        user_list = list()
        return render_template('user_management.html', title='Käyttäjänhallinta', create_userform=create_userform, check_userform=check_userform, user_list=user_list)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

@app.route('/admin/remove_user/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_user(id):
    if current_user.is_authenticated and current_user.clearance == 3:
        user = db.session.query(User).filter(User.id == id).first()
        person = db.session.query(Person).filter(Person.user_id == id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('check_users'))
        create_userform = AdministrationForm()
        check_userform = GetUserForm()
        return render_template('user_management.html', title='Käyttäjänhallinta', create_userform=create_userform, check_userform=check_userform)

#route to add a student and function for it
#fetching the form data and submitting it to the db
#student is fluched to the db first so that the id can be fetched for student_id
@app.route('/admin/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.is_authenticated and current_user.clearance == 3:
#        groups_query = Groups.query.all()
#        if current_user.clearance == 0: 
        form = StudentForm()
#        form.group.choices = [(x.id, x.marking) for x in groups_query]
        form.group.choices = groups_query()
        if form.validate_on_submit():
            student = Student(group_id=form.group.data, full_name=form.firstname.data+' '+form.lastname.data)
            db.session.add(student)
            db.session.flush()
            person = Person(first_name=form.firstname.data, last_name=form.lastname.data, student_id=student.id)
            db.session.add(person)
            db.session.commit()
            flash('Uusi oppilas lisätty!')
            return redirect('/admin/add_student')
        return render_template('student_management.html', title='Lisää oppilas', form=form)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

@app.route('/add_groups', methods=['GET', 'POST'])
@login_required
def add_groups():
    if current_user.is_authenticated and current_user.clearance ==3:
        form = GroupMarkingForm()
        if form.validate_on_submit():
            marking = Groups(marking=form.marking.data)
            db.session.add(marking)
            db.session.commit()
            flash('Luokkaryhmä lisätty!')
        return render_template('add_groups.html', title='Lisää ryhmiä', form=form)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance_main():
    if current_user.is_authenticated and current_user.clearance == 1:
#        if current_user.clearance == 1:
        return render_template('attendance.html', title='Läsnäolo hallinta')
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

#the first page on attendance logging
#required the group to be selected and generates the student list for the second page by it
#global variable use is not really great.. a better way should be used, maybe an external file to dump and fetch the data
@app.route('/attendance/group_select', methods=['GET', 'POST'])
@login_required
def group_select():
    if current_user.is_authenticated and current_user.clearance == 1:
        form = LogAttendanceGroupSelectForm()
        form.group_select.choices = groups_query()
        if form.validate_on_submit():
            students = Student.query.filter_by(group_id=form.group_select.data).all()
            global student_list
            student_list=[(i.id, i.full_name) for i in students]
            return redirect('/attendance/log_attendance')
        return render_template('group_select.html', title='Läsnäolo', form=form)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

#the second page on attendance logging
#inserts the student_list global variable to the form to be used as the choises
@app.route('/attendance/log_attendance', methods=['GET', 'POST'])
@login_required
def attendance_selection():
    if current_user.is_authenticated and current_user.clearance == 1:
#        if current_user.clearance == 1:
        form = AttendanceForm()
        form.attendance.choices = student_list
        if form.validate_on_submit():
            attendance_list = form.attendance.data
            attendance_to_insert = [Attendance(student_id=i, attendance=date.today()) for i in attendance_list]
#            attendance_try = Attendance([{'student_id': i} for i in attendance_list])
#            attendance_data = Attendance(attendance=date.today())
            db.session.bulk_save_objects(attendance_to_insert)
#            db.session.add(attendance_data)
            db.session.commit()
            flash('Läsnäolot merkattu!')
        return render_template('log_attendance.html', title='Kirjaa läsnäolo', form=form, sizelength=len(student_list))
    else:
        flash('Luvaton pääsy!')
        return redirect('/')

@app.route('/attendance/check_attendance', methods=['GET', 'POST'])
@login_required
def attendance_check():
    if current_user.is_authenticated and current_user.clearance == 1:
        form = CheckAttendanceGroupSelectForm()
        form.group_select.choices = groups_query()
        def list():
            if form.validate_on_submit():
#                students = Student.query.filter_by(group=form.group_select.data).all()
#                students_list=[(i.id) for i in students]
#                attendance_date = [Attendance.query.filter_by(student_id=i) for i in students_list]
#                student_names=[(i.full_name) for i in students]
#                conv = student_names + attendance_date
                if form.by_date.data:
                    conv = db.session.query(Attendance.id, Student.id, Student.full_name, Attendance.attendance).join(Attendance).filter(Student.id == Attendance.student_id, Student.group_id == form.group_select.data).order_by(Attendance.id.desc())
                    flash('Läsnäolot järjestetty laskeutuen päivämäärällä!')
                    return conv
                elif form.by_student.data:
                    conv = db.session.query(Attendance.id, Student.id, Student.full_name, Attendance.attendance).join(Attendance).filter(Student.id == Attendance.student_id, Student.group_id == form.group_select.data).order_by(Student.full_name)
                    flash('Länäolot järjestetty nimijärjestykseen!')
                    return conv
        list = list()
        return render_template('check_attendance.html', title="Läsnäolo tarkistus", form=form, list=list)
    else:
        flash('Luvaton pääsy!')
        return redirect('/')
    

#the user page, just for the fun of it I guess. Might be populated better in the future.
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title="Käyttäjä", user=user)

#adding an route for admin manual, so that in the future it can be made a little cleaner,
#if there is more manuals added and the software moved
#the function could be just the authentication check and under that the clearance check if/elif
@app.route('/manual')
@login_required
def manual():
    if current_user.is_authenticated and current_user.clearance == 3:
        return redirect("/static/Admin_manual.pdf")
    elif current_user.is_authenticated and current_user.clearance == 1:
        return redirect("/static/Opettaja_manual.pdf")
    else:
        flash('Luvaton pääsy!')
        return redirect('/')
