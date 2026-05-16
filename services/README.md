
# Services Overview

This project uses a simplified microservice architecture. In larger production systems, services are often separated into independent repositories with their own CI/CD pipelines, infrastructure management, and orchestration platforms such as Kubernetes. For practicality, this project uses a monorepo structure with Docker Compose managing local development and deployment workflows.

Despite sharing a repository, each service is designed as a self-contained application with clear ownership boundaries. Services maintain their own application code, tests, Docker configuration, dependencies, and database ownership, and communicate exclusively through HTTP APIs rather than direct database access.

This structure aims to preserve core microservice principles while reducing infrastructure complexity. The services could be separated into independently deployed applications in the future with minimal architectural changes.

---
## Web — Django BFF

The Web service acts as the backend-for-frontend (BFF) layer.

Responsible for:

- Authentication
- Session management
- UI rendering
- Service orchestration
- Communication with downstream microservices

Owns:
- `web-db`

### Authentication & User Context

The Django Web service is responsible for authenticating users.

Authenticated user identity is forwarded to downstream services
using the `X-User-ID` request header.

---

## Projects — Flask Projects Service

Responsible for:

- Project CRUD
- Project lifecycle management
- Project ownership

Owns:
- `projects-db`

---
### Time Tracking — Flask Time Tracking Service

Responsible for:

- Clock-in / clock-out
- Time entry management
- Work duration tracking

Owns:
- `time-tracking-db`

---

### Tasks — Flask Task Service

Responsible for:

- Tasks CRUD
- Tasks state (to-do, in-progress, done)


Owns:
- `tasks-db`

---

## Internal Communication

Services communicate over Docker networking using service names.

Example:

```text
web -> http://projects:5000
web -> http://time-tracking:5000
```

Local Development URLs

```text
Django web app:          http://localhost:8000
Projects service:        http://localhost:5000
Time-tracking service:   http://localhost:5001
Tasks service:           http://localhost:5002
```

 API Docs

```text
Projects service:        http://localhost:5000/docs
Time-tracking service:   http://localhost:5001/docs
Tasks service:           http://localhost:5002/docs
```

---
## Development

- Each service owns its own database.
- Services must communicate via HTTP APIs.
- Services should not directly query another service's database.
- User ownership is passed using the X-User-ID request header.

### Run all Tests & Linting


```bash
# ------------------------------------------------------------------
# Clear local dev
# ------------------------------------------------------------------
docker compose down --remove-orphans
docker compose build --no-cache web
docker compose build --no-cache projects
docker compose build --no-cache time-tracking
docker compose build --no-cache tasks

# ------------------------------------------------------------------
# Run all Unit/Intergration tests
# ------------------------------------------------------------------
printf "\nRunning all unit tests...\n\n"
docker compose run --rm web python manage.py test && printf "\n---\n" && \
docker compose run --rm projects pytest && printf "\n---\n" && \
docker compose run --rm time-tracking pytest && printf "\n---\n" && \
docker compose run --rm tasks pytest && printf "\n---\n"

# ------------------------------------------------------------------
# Run all linting
# ------------------------------------------------------------------
printf "\nRunning all linting...\n\n"
docker compose run --rm web flake8 && printf "\n---\n" && \
docker compose run --rm projects flake8 && printf "\n---\n" && \
docker compose run --rm time-tracking flake8 && printf "\n---\n" && \
docker compose run --rm tasks flake8 && printf "\n---\n"

# ------------------------------------------------------------------
# System End to End test
# ------------------------------------------------------------------
./tests/system/run-system-tests.sh

# ------------------------------------------------------------------
# Smoke test
# ------------------------------------------------------------------
./tests/smoke/smoke-tests.sh
```