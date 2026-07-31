# Tasks Service API

Version: `v1`

Base URL:

```text
/api
```

Swagger UI:

```text
/docs
```

## Authentication

Project endpoints require:

```text
X-User-ID: <user-id>
```

## Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/api/health` | Health check endpoint. | No |
| POST | `/api/tasks` | Create a new task. | Yes |
| GET | `/api/tasks` | Get all tasks for the current user. | Yes |
| GET | `/api/tasks/{task_id}` | Get a specific task. | Yes |
| PATCH | `/api/tasks/{task_id}` | Update a task owned by the authenticated user. | Yes |
| DELETE | `/api/tasks/{task_id}` | Delete a task owned by the authenticated user. | Yes |

## Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request, such as missing `X-User-ID` |
| 404 | Resource not found |
| 422 | Request body validation failed |
