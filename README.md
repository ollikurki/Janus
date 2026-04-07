# Janus - Student Attendance Management System

> **⚠️ NOTICE: This project has been completely modernized using AI assistance.**  
> The original codebase was significantly refactored and modernized with Flask 3, Bootstrap 5, modular blueprints, service layer, REST API, and many new features. If you were looking for the old version, this is a full rewrite.

A Flask-based web application for managing student attendance in educational settings.

## Features

- **User Management**: Admin can create teachers and students
- **Attendance Tracking**: Teachers can log and check student attendance
- **Group/Class Organization**: Organize students into groups
- **Role-Based Access**: Admin, Teacher, and Student roles
- **Password Reset**: Secure password reset functionality
- **CSV Export**: Export attendance data to CSV
- **REST API**: Health check endpoint for monitoring
- **Rate Limiting**: Protection against brute force attacks

## Tech Stack

- **Backend**: Flask 3.x, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite (dev), MySQL/PostgreSQL (production)
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Security**: flask-limiter, session security, CSRF protection
- **Testing**: pytest, pytest-flask

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Janus
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Initialize Database

```bash
flask init-db
flask create-admin
```

### 5. Run the Application

```bash
python Janus.py
```

The application will be available at `http://localhost:5000`

## Docker Setup

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Using Docker Directly

```bash
docker build -t janus .
docker run -p 5000:5000 janus
```

## User Roles

| Role | Clearance | Permissions |
|------|-----------|-------------|
| Admin | 3 | User/student/group management, export data |
| Teacher | 1 | Log and check attendance, export data |
| Student | 2 | (Future feature) |

## CLI Commands

```bash
flask init-db          # Initialize database tables
flask drop-db          # Drop all tables
flask create-admin     # Create admin user
```

## REST API

Health check endpoint:
```bash
curl http://localhost:5000/api/v1/health
```

## Project Structure

```
Janus/
├── app/
│   ├── __init__.py    # App factory, extensions
│   ├── models.py      # Database models
│   ├── routes.py      # Application routes
│   ├── forms.py       # WTForms forms
│   ├── errors.py      # Error handlers
│   └── templates/     # Jinja2 templates
├── tests/             # Test suite
├── config.py          # Configuration classes
├── Janus.py           # Entry point
├── requirements.txt   # Dependencies
├── Dockerfile        # Docker configuration
└── docker-compose.yml # Docker Compose setup
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Security Features

- Rate limiting on login (5 attempts per minute)
- Session security (HTTP-only, SameSite cookies)
- Password hashing with werkzeug
- CSRF protection via Flask-WTF
- Role-based access control

## License

See LICENSE file.
