# Janus Test Suite

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_janus.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_janus.py` - Main application tests
  - `TestModels` - Database model tests
  - `TestRoutes` - Route/endpoint tests
  - `TestForms` - Form validation tests
  - `TestAttendanceExport` - Export functionality tests

## Fixtures

- `app` - Application instance for testing
- `client` - Test client for making requests
- `runner` - CLI test runner
