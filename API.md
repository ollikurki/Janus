# Janus API Documentation

> **API Version:** 1.0  
> **Base URL:** `/api/v1`  
> **Authentication:** JWT Bearer tokens  
> **Last Updated:** April 7, 2026

---

## Overview

The Janus REST API provides programmatic access to the attendance management system. It supports user authentication, student management, attendance tracking, and group management.

## Authentication

### Obtaining Tokens

Login with username and password to receive JWT access and refresh tokens:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "smith.john",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "smith.john",
    "clearance": 3,
    "group": "Admin"
  }
}
```

### Using Tokens

Include the access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

### Refreshing Tokens

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

---

## Endpoints

### Health Check

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | API health status | Public |

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T12:00:00"
}
```

---

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | User login | Public |
| POST | `/auth/refresh` | Refresh token | JWT (refresh) |
| POST | `/auth/logout` | User logout | JWT |

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

---

### Users (Admin Only)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users` | List users (paginated) | Admin |
| POST | `/users` | Create user | Admin |
| GET | `/users/<id>` | Get user by ID | Admin |
| DELETE | `/users/<id>` | Delete user by ID | Admin |

#### List Users

```http
GET /api/v1/users?page=1&per_page=50
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "smith.john",
      "email": "smith.john@janus.local",
      "group": "Admin"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 50,
  "pages": 1
}
```

#### Create User

```http
POST /api/v1/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "firstname": "John",
  "lastname": "Smith",
  "password": "SecurePass123!",
  "clearance": 3
}
```

**clearance values:** `1` = Teacher, `2` = Student, `3` = Admin

---

### Students

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/students` | List students (paginated) | Teacher+ |
| POST | `/students` | Add student | Admin |
| GET | `/students/<id>` | Get student by ID | Teacher+ |

#### List Students

```http
GET /api/v1/students?page=1&per_page=50
Authorization: Bearer <token>
```

**Response:**
```json
{
  "students": [
    {
      "id": 1,
      "full_name": "Jane Doe",
      "group_id": 1
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50,
  "pages": 2
}
```

#### Add Student

```http
POST /api/v1/students
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "firstname": "Jane",
  "lastname": "Doe",
  "group_id": 1
}
```

---

### Attendance

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/attendance` | List attendance (with filters) | Teacher+ |
| POST | `/attendance` | Log attendance | Teacher+ |

#### List Attendance

```http
GET /api/v1/attendance?group_id=1
Authorization: Bearer <token>
```

Optional query params: `group_id`, `start_date`, `end_date`

#### Log Attendance

```http
POST /api/v1/attendance
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "student_ids": [1, 2, 3],
  "date": "2026-04-07"
}
```

---

### Groups

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/groups` | List all groups | Auth |
| POST | `/groups` | Create group | Admin |

#### List Groups

```http
GET /api/v1/groups
Authorization: Bearer <token>
```

**Response:**
```json
{
  "groups": [
    {
      "id": 1,
      "marking": "Class 4A"
    }
  ]
}
```

#### Create Group

```http
POST /api/v1/groups
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "marking": "Class 4A"
}
```

---

## Error Responses

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

---

## Rate Limiting

- Login endpoint: **5 requests per minute**
- API endpoints: Configurable per deployment

---

## Notes

- All timestamps are in UTC (ISO 8601 format)
- Pagination defaults: 50 items per page, max 100
- JWT access tokens expire after 15 minutes
- JWT refresh tokens expire after 7 days
