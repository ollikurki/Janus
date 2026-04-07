# Janus Student Attendance Management System - Architectural Plan

> **Last Updated:** April 7, 2026  
> **Status:** ✅ ALL PHASES COMPLETE | PHASE F INCEPTION

---

## Executive Summary

Janus is a Flask-based student attendance management system providing role-based access for Admins, Teachers, and Students. The application has been modernized to Flask 3, Bootstrap 5, and includes rate limiting, CSRF protection, and secure session handling. This document outlines the architectural vision for transforming Janus into a scalable, production-ready attendance management platform.

---

## 1. Current Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Janus.py (Entry)                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    app/__init__.py (Factory)                    │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌─────────┐  │
│  │   db     │ │  migrate │ │ login  │ │bootstrap│ │ limiter │  │
│  └──────────┘ └──────────┘ └────────┘ └────────┘ └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  routes/     │     │    models.py     │     │    forms.py     │
│  (6 blueprint)│     │  (User, Student) │     │  (15+ forms)    │
└──────────────┘     └──────────────────┘     └─────────────────┘
        │
        ▼
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  services/   │     │     errors.py    │     │    templates/   │
│  (6 services)│     │  (Error handlers)│     │    (24 .html)   │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

### 1.1 Technology Stack

| Component | Current | Modernized |
|-----------|---------|------------|
| Framework | Flask 2.x | **Flask 3.x** ✅ |
| ORM | Flask-SQLAlchemy | **Flask-SQLAlchemy 3.x** ✅ |
| Migrations | Flask-Migrate | **Flask-Migrate 4.x** ✅ |
| Frontend | Bootstrap 4 | **Bootstrap 5** ✅ |
| Auth | Flask-Login | **Flask-Login 0.6** ✅ |
| Rate Limiting | - | **flask-limiter** ✅ |
| Forms | WTForms | **WTForms 3.1** ✅ |
| Password Hashing | werkzeug | **werkzeug 3.x** ✅ |

---

## 2. Completed Work ✅

### Phase 1: Foundation Modernization ✅
- [x] Flask 3.x upgrade
- [x] Bootstrap 5 integration
- [x] Rate limiting on login (5/min)
- [x] CSRF protection via Flask-WTF
- [x] Secure session cookies
- [x] Password hashing with werkzeug
- [x] Type hints in models
- [x] Multi-database configuration (SQLite/MySQL/PostgreSQL)

### Phase 2: Core Features ✅
- [x] User authentication (login/logout)
- [x] Role-based access control (Admin/Teacher/Student)
- [x] User management (create, search, remove)
- [x] Student management
- [x] Group/class management
- [x] Attendance logging
- [x] Attendance checking and export
- [x] Password reset flow
- [x] Password change
- [x] Admin dashboard with stats
- [x] Custom error pages (400, 403, 404, 422, 500)
- [x] Audit logging for admin actions
- [x] Account lockout after failed attempts
- [x] Password expiration enforcement
- [x] Email notifications (stub + Flask-Mail ready)

### Phase 3: Blueprint Modularization ✅
- [x] Split monolithic `routes.py` into feature-based blueprints
- [x] Service layer introduction (user, student, attendance, export, email)
- [x] Database indexes
- [x] Query pagination (50 items/page)

### Phase 4: REST API ✅
- [x] JWT authentication with Flask-JWT-Extended
- [x] User management API (CRUD endpoints)
- [x] Student management API (CRUD endpoints)
- [x] Attendance API (log, query with filters)
- [x] Groups API (list, create)
- [x] API documentation (OpenAPI/Swagger)

### Phase 5: Feature Additions ✅
- [x] Email notifications (stub mode + Flask-Mail ready)
- [x] Student portal (attendance view)
- [x] Reporting & analytics
- [x] PDF export
- [x] Student excuse submissions
- [x] Breadcrumbs navigation
- [x] Active nav state highlighting

---

## 3. Known Issues & Technical Debt

### 3.1 Critical Issues

| Issue | Description | Fix Approach |
|-------|-------------|--------------|
| **Magic numbers for roles** | `clearance: 1=Teacher, 2=Student, 3=Admin` hardcoded everywhere | Create `UserRole` enum model |
| **Group is just a string** | `group` field on User is a string, Groups model exists but not used consistently | Normalize group association |
| **Username auto-gen** | `lastname.firstname` format is inflexible | Allow custom usernames |
| **Email auto-gen** | `username@janus.local` is unrealistic | Require real email input |

### 3.2 Missing Domain Concepts

| Concept | Current State | Needed |
|---------|--------------|--------|
| **Courses/Subjects** | Not implemented | Course model with teacher assignment |
| **Parent accounts** | Not implemented | Parent role with child linkage |
| **Substitute teachers** | Not implemented | Temporary teacher role |
| **Permissions system** | Just role checks | Granular permission model |
| **Departments** | Not implemented | Department hierarchy |

### 3.3 Security Enhancements Needed

| Feature | Status | Priority |
|---------|--------|----------|
| JWT blocklisting (logout) | Not implemented | Medium |
| Redis session storage | Not implemented | Medium |
| IP allowlisting | Not implemented | Low |
| 2FA support | Not implemented | Medium |
| Password history | Not implemented | Low |

### 3.4 UX Improvements

| Feature | Status | Priority |
|---------|--------|----------|
| Audit log viewer UI | Logs created but no UI | Medium |
| Bulk attendance (absent + reason) | Only "present" marking | High |
| Real-time notifications | Not implemented | Low |
| Localization (i18n) | Finnish text hardcoded | Low |
| User profile pictures | Not implemented | Low |

---

## 4. Recommended Architectural Improvements

### 4.1 Phase F: Role & Permission System Refactor

**Goal:** Replace magic numbers with proper types and add granular permissions

#### Step 1: Create UserRole Model
```python
class UserRole(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(32), unique=True)  # 'admin', 'teacher', 'student', 'parent', 'substitute'
    display_name: str = db.Column(db.String(64))  # 'Administrator', 'Teacher', etc.
    priority: int = db.Column(db.Integer)  # For role hierarchy
```

#### Step 2: Create Permission Model
```python
class Permission(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(64), unique=True)  # 'users.create', 'attendance.view'
    description: str = db.Column(db.String(128))

class RolePermission(db.Model):
    role_id = db.Column(db.Integer, ForeignKey('user_role.id'))
    permission_id = db.Column(db.Integer, ForeignKey('permission.id'))
```

#### Step 3: Update User Model
```python
# Replace clearance with foreign key
role_id: int = db.Column(db.Integer, ForeignKey('user_role.id'))
role = db.relationship('UserRole', backref='users')

# Keep is_admin(), is_teacher(), is_student() as helpers
def is_admin(self) -> bool:
    return self.role and self.role.name == 'admin'
```

#### Benefits:
- Easy to add new roles without code changes
- Role hierarchy via `priority` field
- Granular permissions instead of role checks
- Self-documenting through `display_name`

---

### 4.2 Phase G: Course & Schedule System

**Goal:** Add courses/subjects with scheduled attendance times

#### New Models
```python
class Course(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(128))
    code: str = db.Column(db.String(16))  # e.g., 'MATH101'
    teacher_id = db.Column(db.Integer, ForeignKey('user.id'))
    group_id = db.Column(db.Integer, ForeignKey('groups.id'))
    schedule: JSON = db.Column(JSON)  # {'day': 'monday', 'hour': 9}

class CourseAttendance(db.Model):
    # Links course schedule to actual attendance
    id: int = db.Column(db.Integer, primary_key=True)
    course_id: int = db.Column(db.Integer, ForeignKey('course.id'))
    student_id: int = db.Column(db.Integer, ForeignKey('student.id'))
    scheduled_date: datetime = db.Column(db.Date)
    status: str = db.Column(db.String(16))  # 'present', 'absent', 'excused'
```

#### Benefits:
- Scheduled courses instead of ad-hoc attendance
- Automatic attendance reminders
- Better reporting by course
- Support for multiple teachers per course

---

### 4.3 Phase H: Parent & Family Accounts

**Goal:** Allow parents to monitor children's attendance

#### New Models
```python
class Family(db.Model):
    """Family grouping for parent-child relationships."""
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(128))

class StudentGuardian(db.Model):
    """Links students to their guardians."""
    student_id: int = db.Column(db.Integer, ForeignKey('student.id'))
    guardian_id: int = db.Column(db.Integer, ForeignKey('user.id'))
    relationship: str = db.Column(db.String(32))  # 'mother', 'father', 'guardian'
    notification_preferences: JSON = db.Column(JSON)
```

#### Features:
- Parents see all children in one view
- Email/SMS notifications for absences
- Excuse approval workflow
- Attendance alerts

---

### 4.4 Phase I: Enhanced Security

**Goal:** Production-grade security features

#### JWT Blocklisting
```python
class TokenBlocklist(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    jti: str = db.Column(db.String(64), unique=True)  # JWT ID
    revoked_at: datetime = db.Column(db.DateTime)
    expires_at: datetime = db.Column(db.DateTime)
```

#### Redis Session Storage
- Replace in-memory session storage with Redis
- Enables horizontal scaling
- Session revocation capability

#### Password History
```python
class PasswordHistory(db.Model):
    user_id: int = db.Column(db.Integer, ForeignKey('user.id'))
    password_hash: str = db.Column(db.String(256))
    created_at: datetime = db.Column(db.DateTime)
```

---

### 4.5 Phase J: Bulk Operations & Import

**Goal:** Efficient batch operations for attendance

#### Features:
- CSV bulk import for students
- Bulk attendance marking (present/absent/excused)
- Excel export with formatting
- Attendance notes/comments per record

---

## 5. Implementation Roadmap

### Phase F: Role & Permission System 🔲 INCEPTION
1. [ ] Create `UserRole` model with seed data
2. [ ] Create `Permission` model with seed data
3. [ ] Create `RolePermission` join table
4. [ ] Update `User` model to use `role_id`
5. [ ] Update all role checks to use new system
6. [ ] Update forms to use role names instead of numbers
7. [ ] Update API to return role names
8. [ ] Write migration for existing data

### Phase G: Course & Schedule System 🔲 BACKLOG
1. [ ] Create `Course` model
2. [ ] Create `CourseAttendance` model
3. [ ] Add course management UI
4. [ ] Add scheduled attendance views
5. [ ] Attendance report by course

### Phase H: Parent & Family Accounts 🔲 BACKLOG
1. [ ] Create `Family` model
2. [ ] Create `StudentGuardian` model
3. [ ] Add parent role
4. [ ] Add guardian notification preferences
5. [ ] Parent dashboard showing children's attendance

### Phase I: Enhanced Security 🔲 BACKLOG
1. [ ] Implement JWT blocklisting
2. [ ] Add Redis session backend
3. [ ] Add password history
4. [ ] Add IP allowlisting option
5. [ ] Add 2FA support (TOTP)

### Phase J: Bulk Operations 🔲 BACKLOG
1. [ ] CSV student import
2. [ ] Bulk attendance marking
3. [ ] Enhanced Excel export
4. [ ] Attendance notes field

### Phase K: Documentation 🔲 BACKLOG
1. [ ] Update README.md with current feature set and setup instructions
2. [ ] Sync API.md with all implemented endpoints
3. [ ] Add inline documentation to service classes
4. [x] Create CONTRIBUTING.md with contribution guidelines
5. [ ] Document deployment procedures

---

## 6. File Structure (Target)

```
Janus/
├── Janus.py                      # Application entry point
├── run.py                        # Development runner
├── config.py                     # Configuration classes
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── mypy.ini                      # Type checking config
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Local development stack
├── .github/
│   └── workflows/
│       └── test.yml              # CI pipeline
├── app/
│   ├── __init__.py               # App factory
│   ├── extensions.py             # Extension initialization
│   ├── routes/
│   │   ├── __init__.py           # Blueprint registration
│   │   ├── main.py              # Dashboard routes
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin routes
│   │   ├── attendance.py         # Attendance routes
│   │   ├── user.py              # User profile routes
│   │   ├── course.py            # Course management (NEW)
│   │   └── api.py               # REST API routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User, UserRole, Permission
│   │   ├── student.py           # Student, Family, Guardian
│   │   ├── attendance.py        # Attendance, CourseAttendance
│   │   ├── course.py            # Course (NEW)
│   │   └── group.py             # Groups
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── admin_forms.py
│   │   └── attendance_forms.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── attendance_service.py
│   │   ├── course_service.py    # NEW
│   │   └── export_service.py
│   ├── templates/
│   │   └── ...                   # 25+ HTML templates
│   ├── static/
│   │   └── ...                   # CSS, JS, PDFs
│   └── errors.py                 # Error handlers
├── logs/                         # Application logs
├── tests/
│   ├── unit/
│   ├── integration/
│   └── robot/
│       └── full_tests/
└── migrations/                   # Flask-Migrate
```

---

## 7. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Code modularity | Feature-based blueprints + services ✅ | Complete |
| Test coverage | Basic | 80%+ |
| API readiness | Full REST API ✅ | Complete |
| Session storage | In-memory (Redis in compose) | Complete |
| Email notifications | Stub + Flask-Mail ready ✅ | Functional |
| Student portal | Full implementation ✅ | Complete |
| Docker support | Complete ✅ | Complete |
| Audit logging | Implemented ✅ | Complete |
| Account lockout | Implemented ✅ | Complete |
| Password expiry | Enforced on change password ✅ | Enforced on login |
| Reporting & Analytics | Implemented ✅ | Complete |
| PDF Export | Implemented ✅ | Complete |
| Excuse submissions | Implemented ✅ | Complete |
| Breadcrumbs/Active nav | Implemented ✅ | Complete |
| Role system | Magic numbers | Type-safe enum |
| Course system | None | Implemented |
| Parent accounts | None | Implemented |
| Granular permissions | Role-based | Permission-based |

---

*This plan is a living document and should be updated as the project evolves.*

> **Last Updated:** April 7, 2026  
> **Status:** ✅ ALL PHASES COMPLETE

---

