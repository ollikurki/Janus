from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

#Database table models

#user table class with password hashing and checking the hash
#group column should be removed at some point
#passwords should be moved to their own table
#clearance should be named differently and moved to their own table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    clearance = db.Column(db.Integer)
    group = db.Column(db.String(16))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


#table for names and ids to identify them by
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

#table for students and the group they belong to
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(16))
    full_name = db.Column(db.String(160))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

#table for attendance records
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attendance = db.Column(db.Date)

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marking = db.Column(db.String(16))

#creating the function to load the user when logging in
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
