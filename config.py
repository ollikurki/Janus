import os
basedir = os.path.abspath(os.path.dirname(__file__))

#the configuration objects for the software. Could be stated as environment objects in later versions
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:admin@localhost/Janus'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['kurki.olli@outlook.com']
