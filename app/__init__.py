from flask import Flask
from config import get_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap5()
limiter = Limiter(key_func=get_remote_address)
jwt = JWTManager()


def create_app(config_class=None):
    """Application factory for creating the Flask app."""
    app = Flask(__name__)
    
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Validate security configuration in production
    from config import _validate_security_config
    _validate_security_config()
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)
    
    login.login_view = 'auth.login'
    login.login_message = 'Please sign in to continue.'
    
    # Import models
    from app import models
    
    # Register user_loader for Flask-Login
    from app.models import load_user
    login.user_loader(load_user)
    
    # Setup logging
    setup_logging(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register blueprints (modular structure)
    from app.routes import main_bp, auth_bp, admin_bp, attendance_bp, user_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app


def setup_logging(app):
    """Configure application logging."""
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/Janus.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(message)s [in %(pathname)s:%(lineno)d]')
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Janus startup')


def register_cli_commands(app):
    """Register Flask CLI commands for database management."""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command('drop-db')
    def drop_db():
        """Drop all database tables."""
        db.drop_all()
        print('Database dropped.')
    
    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user."""
        from app.models import User, Person
        
        username = input('Username: ')
        password = input('Password: ')
        email = input('Email: ')
        
        admin = User(
            username=username,
            email=email,
            clearance=3,
            group='Admin'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.flush()
        
        person = Person(
            first_name='Admin',
            last_name='User',
            user_id=admin.id
        )
        db.session.add(person)
        db.session.commit()
        print(f'Admin user "{username}" created.')
