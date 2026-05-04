# Projects Service API

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
| GET | `/api/health` | Return a basic service health check. | No |
| GET | `/api/db-health` | Return a database connectivity health check. | No |
| POST | `/api/projects` | Create a new project for the authenticated user. | Yes |
| GET | `/api/projects` | Return all projects owned by the authenticated user. | Yes |
| GET | `/api/projects/{project_id}` | Return a single project owned by the authenticated user. | Yes |
| PATCH | `/api/projects/{project_id}` | Update a project owned by the authenticated user. | Yes |
| DELETE | `/api/projects/{project_id}` | Delete a project owned by the authenticated user. | Yes |

## Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request, such as missing `X-User-ID` |
| 404 | Resource not found |
| 422 | Request body validation failed |
