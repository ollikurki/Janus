# Contributing to Janus

Thank you for your interest in contributing to Janus!

---

## Getting Started

### Prerequisites

- Python 3.11+
- SQLite (dev), MySQL/PostgreSQL (production)
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ollikurki/Janus.git
cd Janus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask init-db
flask create-admin
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_janus.py -v
```

### Running Locally

```bash
# Development mode
python Janus.py

# Or with Flask CLI
export FLASK_APP=Janus.py
flask run --debug
```

The application will be available at `http://localhost:5000`

---

## Project Structure

```
Janus/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms form classes
│   ├── errors.py            # Error handlers
│   ├── routes/              # Blueprint route modules
│   │   ├── main.py         # Dashboard routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── admin.py        # Admin routes
│   │   ├── attendance.py    # Attendance routes
│   │   ├── user.py         # User profile routes
│   │   └── api.py          # REST API routes
│   ├── services/            # Business logic layer
│   │   ├── user_service.py
│   │   ├── student_service.py
│   │   ├── attendance_service.py
│   │   ├── export_service.py
│   │   ├── email_service.py
│   │   └── audit_service.py
│   └── templates/           # Jinja2 templates
├── tests/                   # Test suite
├── config.py               # Configuration classes
├── Janus.py                # Application entry point
└── requirements.txt        # Python dependencies
```

---

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Add docstrings to all public functions and classes
- Maximum line length: 88 characters (Black formatter)

### Form Validation

- Use WTForms validators for all user input
- Validate on both client and server side
- Return meaningful error messages

### Database

- Use SQLAlchemy ORM for all database operations
- Add database indexes for frequently queried columns
- Use migrations for schema changes (Flask-Migrate)

### Security

- Never commit secrets or credentials
- Use environment variables for sensitive configuration
- Sanitize all user input before database queries
- Use parameterized queries (SQLAlchemy handles this)

### Git Commits

- Use clear, descriptive commit messages
- Start with verb: "Add feature", "Fix bug", "Update documentation"
- Reference issues when applicable: "Fix login bug (#123)"

---

## Pull Request Process

### 1. Branch Naming

```
feature/short-description
bugfix/short-description
docs/short-description
refactor/short-description
```

### 2. Before Submitting

- [ ] Code follows PEP 8 style
- [ ] Type hints added where applicable
- [ ] Functions have docstrings
- [ ] Tests added/updated for new features
- [ ] Documentation updated if needed
- [ ] No debug statements or TODO comments left

### 3. PR Description Template

```markdown
## Summary
Brief description of changes

## Changes Made
- Change 1
- Change 2

## Testing
How was this tested?

## Related Issues
Fixes #123
```

---

## Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Screenshots if applicable

---

## Suggesting Features

Open an issue with:
- Clear feature description
- Use case / motivation
- Potential implementation approaches
- Any relevant examples or references

---

## Questions?

For questions, open an issue or contact the maintainers.

---

## License

By contributing, you agree that your contributions will be licensed under the project's license.
