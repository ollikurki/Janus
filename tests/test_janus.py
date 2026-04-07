import pytest
from app import create_app, db
from app.models import User, Person, Student, Groups


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('TestingConfig')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


class TestModels:
    """Test database models."""
    
    def test_user_password_hashing(self, app):
        """Test password hashing works."""
        with app.app_context():
            user = User(username='testuser', clearance=1, group='Teacher')
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
            
            assert user.check_password('testpassword123')
            assert not user.check_password('wrongpassword')
    
    def test_user_roles(self, app):
        """Test role helper methods."""
        with app.app_context():
            admin = User(username='admin', clearance=3, group='Admin')
            teacher = User(username='teacher', clearance=1, group='Teacher')
            student = User(username='student', clearance=2, group='Student')
            
            assert admin.is_admin()
            assert not admin.is_teacher()
            assert not admin.is_student()
            
            assert teacher.is_teacher()
            assert not teacher.is_admin()
            
            assert student.is_student()
            assert not student.is_admin()


class TestRoutes:
    """Test application routes."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_login_page_loads(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client, app):
        """Test login with invalid credentials."""
        with app.app_context():
            user = User(username='testuser', clearance=1, group='Teacher')
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, client, app):
        """Test logout redirects to index."""
        with app.app_context():
            user = User(username='testuser', clearance=1, group='Teacher')
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
        
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


class TestForms:
    """Test form validation."""
    
    def test_login_form_validation(self, app):
        """Test login form requires fields."""
        with app.app_context():
            from app.forms import LoginForm
            
            form = LoginForm(data={})
            assert not form.validate()
            assert 'Username' in form.errors
            assert 'Password' in form.errors
    
    def test_password_mismatch(self, app):
        """Test password confirmation validation."""
        with app.app_context():
            from app.forms import AdministrationForm
            
            form = AdministrationForm(data={
                'firstname': 'John',
                'lastname': 'Doe',
                'password': 'password123',
                'password2': 'differentpassword',
                'clearance': 1
            })
            assert not form.validate()
            assert 'password2' in form.errors


class TestAttendanceExport:
    """Test attendance export functionality."""
    
    def test_export_requires_auth(self, client):
        """Test export endpoint requires authentication."""
        response = client.get('/attendance/export')
        # Should redirect to login
        assert response.status_code == 302
