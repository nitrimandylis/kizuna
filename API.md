# Kizuna Platform API Documentation

## Overview

The Kizuna Platform provides a RESTful API for accessing events, clubs, and user data.

**Base URL:** `/api`

**Authentication:** Most user actions require session-based authentication via the web interface.

---

## Events API

### Get Events by Month

Retrieves all published events for a specific month.

```
GET /api/events
```

**Query Parameters:**

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| year      | int    | Yes      | Year (e.g., 2024)              |
| month     | int    | Yes      | Month number (1-12)            |

**Response:**

```json
[
  {
    "id": 1,
    "title": "Community Service Day",
    "date": "2024-03-15",
    "cas_type": "Service",
    "location": "Main Hall"
  }
]
```

**Example:**

```bash
curl "https://your-domain.com/api/events?year=2024&month=3"
```

---

## Authentication Endpoints

### Register User

```
POST /auth/register
```

**Form Data:**

| Field     | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| username  | string | Yes      | 3-80 characters, alphanumeric  |
| email     | string | Yes      | Valid email address            |
| password  | string | Yes      | Minimum 8 characters           |
| confirm_password | string | Yes | Must match password      |

**Response:** Redirects to login page with success message.

---

### Login

```
POST /auth/login
```

**Form Data:**

| Field     | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| username  | string | Yes      | Username or email              |
| password  | string | Yes      | User password                  |
| remember  | string | No       | "on" for remember me           |

**Response:** Redirects to home page on success.

---

### Logout

```
GET /auth/logout
```

**Requires:** Authentication

**Response:** Redirects to home page.

---

### Forgot Password

```
POST /auth/forgot-password
```

**Form Data:**

| Field | Type   | Required | Description                    |
|-------|--------|----------|--------------------------------|
| email | string | Yes      | Registered email address       |

**Response:** Redirects to login page.

---

### Reset Password

```
POST /auth/reset-password/<token>
```

**URL Parameters:**

| Parameter | Type   | Description                      |
|-----------|--------|----------------------------------|
| token     | string | Password reset token from email  |

**Form Data:**

| Field            | Type   | Required | Description                 |
|------------------|--------|----------|-----------------------------|
| password         | string | Yes      | New password (min 8 chars)  |
| confirm_password | string | Yes      | Must match password         |

---

## Event Endpoints

### List Events

```
GET /events/
```

**Query Parameters:**

| Parameter | Type   | Description                        |
|-----------|--------|------------------------------------|
| page      | int    | Page number (default: 1)           |
| type      | string | Filter by CAS type (Creativity/Activity/Service) |
| q         | string | Search query                       |

---

### Event Detail

```
GET /events/<event_id>
```

**URL Parameters:**

| Parameter | Type | Description     |
|-----------|------|-----------------|
| event_id  | int  | Event ID        |

---

### Register for Event

```
POST /events/<event_id>/register
```

**Requires:** Authentication, CSRF token

**Response:** Redirects to event detail page.

---

### Unregister from Event

```
POST /events/<event_id>/unregister
```

**Requires:** Authentication, CSRF token

**Response:** Redirects to event detail page.

---

## Club Endpoints

### List Clubs

```
GET /clubs/
```

**Query Parameters:**

| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| page      | int    | Page number (default: 1) |
| q         | string | Search query             |

---

### Club Detail

```
GET /clubs/<club_id>
```

**URL Parameters:**

| Parameter | Type | Description   |
|-----------|------|---------------|
| club_id   | int  | Club ID       |

---

## Profile Endpoints

### View Profile

```
GET /profile/
```

**Requires:** Authentication

---

### Edit Profile

```
POST /profile/edit
```

**Requires:** Authentication, CSRF token

**Form Data:**

| Field | Type   | Required | Description          |
|-------|--------|----------|----------------------|
| email | string | Yes      | New email address    |

---

### Change Password

```
POST /profile/change-password
```

**Requires:** Authentication, CSRF token

**Form Data:**

| Field            | Type   | Required | Description          |
|------------------|--------|----------|----------------------|
| current_password | string | Yes      | Current password     |
| new_password     | string | Yes      | New password         |
| confirm_password | string | Yes      | Must match new       |

---

## Admin Endpoints

All admin endpoints require admin privileges.

### Dashboard

```
GET /admin/
```

**Requires:** Admin role

---

### Event Management

| Method | Endpoint                    | Description          |
|--------|----------------------------|----------------------|
| GET    | /admin/events              | List all events      |
| GET    | /admin/events/create       | Create event form    |
| POST   | /admin/events/create       | Create event         |
| GET    | /admin/events/<id>/edit    | Edit event form      |
| POST   | /admin/events/<id>/edit    | Update event         |
| POST   | /admin/events/<id>/delete  | Delete event         |

---

### Club Management

| Method | Endpoint                   | Description          |
|--------|---------------------------|----------------------|
| GET    | /admin/clubs              | List all clubs       |
| GET    | /admin/clubs/create       | Create club form     |
| POST   | /admin/clubs/create       | Create club          |
| GET    | /admin/clubs/<id>/edit    | Edit club form       |
| POST   | /admin/clubs/<id>/edit    | Update club          |
| POST   | /admin/clubs/<id>/delete  | Delete club          |

---

### User Management

| Method | Endpoint                          | Description            |
|--------|-----------------------------------|------------------------|
| GET    | /admin/users                      | List all users         |
| POST   | /admin/users/<id>/toggle-admin    | Toggle admin status    |

---

## Error Responses

### 404 Not Found

Returned when a requested resource does not exist.

### 403 Forbidden

Returned when user lacks permission for an action.

### 500 Internal Server Error

Returned when an unexpected error occurs.

---

## Rate Limiting

The following endpoints have rate limiting:

| Endpoint            | Limit           | Window    |
|--------------------|-----------------|-----------|
| /auth/register     | 5 requests      | 1 hour    |
| /auth/login        | 10 requests     | 5 minutes |
| /auth/forgot-password | 3 requests   | 1 hour    |
| /auth/reset-password  | 5 requests   | 5 minutes |

---

## CSRF Protection

All POST, PUT, and DELETE requests require a CSRF token. Include the token in a hidden form field:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

Or include it in the request header:

```
X-CSRFToken: <token>
```

---

## Content Types

- HTML responses: `text/html`
- API responses: `application/json`

---

## Version

API Version: 1.0.0

Last Updated: 2024
