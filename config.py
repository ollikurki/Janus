import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

#the configuration objects for the software. Could be stated as environment objects in later versions
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.environ.get('DATABASE_USER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['kurki.olli@outlook.com']
