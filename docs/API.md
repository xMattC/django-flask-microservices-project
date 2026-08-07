# API Documentation

This document provides a consolidated overview of the API services in the Productivity Microservices Platform. Each Flask microservice also maintains its own service-level API documentation and Swagger UI.


| Service | Responsibility | Local URL | Swagger UI | Service API Docs |
|---|---|---|---|---|
| Projects Service | Project CRUD and ownership | `http://localhost:5000` | `http://localhost:5000/docs` | [API.md](../services/projects/docs/API.md) |
| Time Tracking Service | Time entry and tracking workflows | `http://localhost:5001` | `http://localhost:5001/docs` | [API.md](../services/time-tracking/docs/API.md) |
| Tasks Service | Task CRUD and task lifecycle workflows | `http://localhost:5002` | `http://localhost:5002/docs` | [API.md](../services/tasks/docs/API.md) |


Downstream Flask API services receive authenticated user context from the Django BFF using:

``` text
X-User-ID: <user-id>
```

Requests missing required user context should return `400 Bad Request`.

------------------------------------------------------------------------

# Projects Service API

### Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/api/health` | Health check endpoint. | Yes |
| GET | `/api/db-health` | Check the database connection. | Yes |
| POST | `/api/projects` | Create a new project for the authenticated user. | Yes |
| GET | `/api/projects` | Return all projects owned by the authenticated user. | Yes |
| GET | `/api/projects/{project_id}` | Return a single project owned by the authenticated user. | Yes |
| PATCH | `/api/projects/{project_id}` | Update a project owned by the authenticated user. | Yes |
| DELETE | `/api/projects/{project_id}` | Delete a project owned by the authenticated user. | Yes |

### Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request, such as missing `X-User-ID` |
| 404 | Resource not found |
| 422 | Request body validation failed |

------------------------------------------------------------------------

# Time Tracking Service API

### Endpoints

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

### Error responses

| Status | Meaning |
|---|---|
| 400 | Bad request, such as missing `X-User-ID` |
| 404 | Resource not found |
| 422 | Request body validation failed |

------------------------------------------------------------------------

# Tasks Service API

## Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/api/health` | Health check endpoint. | No |
| GET | `/api/db-health` | Check the database connection. | Yes |
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
(todo)

------------------------------------------------------------------------

