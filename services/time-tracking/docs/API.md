# Time Tracking Service API

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
| GET | `/api/health` | Health check endpoint. | Yes |
| GET | `/api/db-health` | Check the database connection. | Yes |
| POST | `/api/time-entries` | Create a new time entry. | Yes |
| GET | `/api/time-entries` | List all time entries. Can be filtered by project_id and running_only if provided. | Yes |
| GET | `/api/time-entries/{entry_id}` | Get a single time entry. | Yes |
| PATCH | `/api/time-entries/{entry_id}` | Update a finished time entry. | Yes |
| DELETE | `/api/time-entries/{entry_id}` | Delete a time entry. | Yes |
| PATCH | `/api/time-entries/{entry_id}/stop` | Stop a running time entry. | Yes |

## Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request, such as missing `X-User-ID` |
| 404 | Resource not found |
| 422 | Request body validation failed |
