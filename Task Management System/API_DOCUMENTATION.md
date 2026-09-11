# Task Management System API Documentation

## 1. Overview

Base URL:

```text
http://127.0.0.1:8000
```

Interactive documentation is available at:

```text
GET /docs

```

All protected endpoints require a bearer access token:

```http
Authorization: Bearer <access_token>
```

The API uses stateless JWT access tokens. There is no refresh-token endpoint and no database token table.

## 2. Authentication

### Register

```http
POST /auth/register
Content-Type: application/json
```

Request:

```json
{
  "name": "User One",
  "email": "user@example.com",
  "phone": "1234567890",
  "password": "Strong@123"
}
```

The public registration flow creates a regular user. The `role` value is not taken from the public request.

Success: `201 Created`

Duplicate email: `409 Conflict`

```json
{
  "detail": "Email is already registered"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json
```

Request:

```json
{
  "email": "user@example.com",
  "password": "Strong@123"
}
```

Success: `200 OK`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User One",
    "role": "user",
    "phone": "1234567890",
    "is_active": true,
    "created_at": "2026-09-12T10:00:00"
  }
}
```

### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

Invalidates the current user's access-token version in memory.

### Get profile

```http
GET /auth/profile
Authorization: Bearer <access_token>
```

### Update profile

```http
PUT /auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json
```

All fields are optional:

```json
{
  "email": "new-email@example.com",
  "name": "Updated Name",
  "phone": "9876543210"
}
```

Emails are normalized and must be unique. Duplicate email: `409 Conflict`.

### Change password

```http
PUT /auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "current_password": "Strong@123",
  "new_password": "NewStrong@123"
}
```

`current_password` is optional in the current implementation. `new_password` must satisfy the password-strength rules.

## 3. Users

All `/users` endpoints are admin-only.

### List users

```http
GET /users
Authorization: Bearer <admin_access_token>
```

### Get user

```http
GET /users/{user_id}
Authorization: Bearer <admin_access_token>
```

### Create user

```http
POST /users
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

Request:

```json
{
  "name": "Managed User",
  "email": "managed@example.com",
  "phone": "1234567890",
  "password": "Strong@123",
  "role": "user"
}
```

Allowed roles: `user`, `admin`.

Duplicate email: `409 Conflict` with `Email is already registered`.

### Update user

```http
PUT /users/{user_id}
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

Possible fields:

```json
{
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "phone": "9876543210",
  "role": "user",
  "is_active": true
}
```

Duplicate email: `409 Conflict`.

### Deactivate user

```http
DELETE /users/{user_id}
Authorization: Bearer <admin_access_token>
```

The user is deactivated rather than physically deleted.

## 4. Tasks

Regular users and admins can create tasks. A task is created without an assignee.

### Create task

```http
POST /tasks
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "title": "Prepare report",
  "description": "Prepare the monthly report",
  "priority": "high",
  "due_date": "2026-09-20T10:00:00"
}
```

Allowed priorities: `low`, `medium`, `high`, `critical`.

### List tasks

```http
GET /tasks?page=1&limit=20&sort_by=created_at&sort_order=desc
Authorization: Bearer <access_token>
```

Optional query parameters:

- `status`: `todo`, `in_progress`, `completed`, `cancelled`
- `priority`: `low`, `medium`, `high`, `critical`
- `assigned_user_id`
- `search`
- `page`: minimum `1`
- `limit`: `1` to `100`
- `sort_by`: `created_at`, `due_date`, `priority`, `status`, `title`
- `sort_order`: `asc` or `desc`

Regular users see tasks they created or tasks currently assigned to them. Admins see all tasks.

### Get task

```http
GET /tasks/{task_id}
Authorization: Bearer <access_token>
```

Accessible to the creator, current assignee, or an admin.

### Update task details

```http
PUT /tasks/{task_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "title": "Updated report",
  "description": "Updated task details",
  "due_date": "2026-09-21T10:00:00"
}
```

This endpoint does not accept `assigned_to_id`, `status`, or `priority`. Those fields have dedicated endpoints. Extra fields return `422 Unprocessable Entity`.

The creator or an admin can update task details. The assigned user can update only status and priority through their dedicated endpoints.

### Assign or reassign task

```http
PUT /tasks/{task_id}/assign
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "assigned_to_id": 4
}
```

Only the task creator or an admin can assign or reassign. The target user must be active.

First assignment response:

```json
{
  "message": "Task ID 5 assigned to user ID 4",
  "task": {}
}
```

Same-user assignment response:

```json
{
  "message": "Task ID 5 is already assigned to user ID 4",
  "task": {}
}
```

Reassignment response:

```json
{
  "message": "Task ID 5 reassigned from user ID 3 to user ID 4",
  "task": {}
}
```

### Change status

```http
PUT /tasks/{task_id}/status?status=in_progress
Authorization: Bearer <access_token>
```

Allowed statuses: `todo`, `in_progress`, `completed`, `cancelled`.

Allowed transitions:

- `todo` -> `in_progress` or `cancelled`
- `in_progress` -> `todo`, `completed`, or `cancelled`
- `completed` -> no further changes
- `cancelled` -> no further changes

The creator, current assignee, or an admin can change status.

### Change priority

```http
PUT /tasks/{task_id}/priority
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "priority": "critical"
}
```

The creator, current assignee, or an admin can change priority.

### Delete task

```http
DELETE /tasks/{task_id}
Authorization: Bearer <access_token>
```

Only the creator or an admin can delete a task.

## 5. Comments

The task creator, current assignee, or an admin can access task comments. Closed tasks cannot be commented on.

### Add comment

```http
POST /tasks/{task_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json
```

Request:

```json
{
  "content": "Progress update"
}
```

Comment length: 1 to 5000 characters.

### List comments

```http
GET /tasks/{task_id}/comments
Authorization: Bearer <access_token>
```

### Update comment

```http
PUT /comments/{comment_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

Only the comment author or an admin can update it.

### Delete comment

```http
DELETE /comments/{comment_id}
Authorization: Bearer <access_token>
```

Only the comment author or an admin can delete it.

## 6. Attachments

Allowed file extensions:

- `.pdf`
- `.jpg`, `.jpeg`, `.png`
- `.doc`, `.docx`
- `.txt`

Maximum size: `10 MB` by default.

### Upload attachment

```http
POST /tasks/{task_id}/attachments
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Form-data field:

```text
file: <file>
```

The task creator, current assignee, or an admin can upload attachments.

### List attachments

```http
GET /tasks/{task_id}/attachments
Authorization: Bearer <access_token>
```

### Delete attachment

```http
DELETE /attachments/{attachment_id}
Authorization: Bearer <access_token>
```

The task creator, current assignee, or an admin can delete attachments for an accessible task.

## 7. Notifications

Notifications are generated for:

- Initial task assignment: `task_assigned`
- Task reassignment: `task_reassigned`
- Task status change: `status_changed`
- New comment: `comment_added`
- Task completion: `task_completed`

### List notifications

```http
GET /notifications
Authorization: Bearer <access_token>
```

Users see only their own notifications.

### Mark notification as read

```http
PUT /notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

### Mark all notifications as read

```http
PUT /notifications/read-all
Authorization: Bearer <access_token>
```

## 8. Dashboards

### User dashboard

```http
GET /dashboard/user
Authorization: Bearer <access_token>
```

Returns counts for the current user's created or currently assigned tasks, including pending, completed, overdue, and critical tasks.

### Admin dashboard

```http
GET /dashboard/admin
Authorization: Bearer <admin_access_token>
```

Admin-only metrics include total users, total tasks, status counts, critical tasks, and overdue tasks.

## 9. Audit logs

Audit logs are admin-only.

### List audit logs

```http
GET /audit-logs
Authorization: Bearer <admin_access_token>
```

### Get audit log

```http
GET /audit-logs/{log_id}
Authorization: Bearer <admin_access_token>
```

## 10. Common responses

- `201 Created`: resource created successfully
- `400 Bad Request`: invalid business action, assignment, or status transition
- `401 Unauthorized`: missing, invalid, expired, or revoked access token
- `403 Forbidden`: authenticated user lacks permission
- `404 Not Found`: requested resource does not exist
- `409 Conflict`: duplicate email or other uniqueness conflict
- `413 Request Entity Too Large`: uploaded file exceeds the configured limit
- `422 Unprocessable Entity`: request validation failed or contains forbidden fields
