# django-flask-microservices-project

## Overview

Microservice-based time tracking system built with Django, Flask, PostgreSQL, Docker, and Docker Compose.

The system currently supports:

- User-facing Django BFF service
- Projects Flask microservice
- Time Tracking Flask microservice
- Independent PostgreSQL databases per service
- HTTP communication between services using internal Docker Compose service URLs
- User ownership propagation via `X-User-ID` headers

---

## Architecture

The system follows a **Backend-for-Frontend (BFF)** pattern.

### Active Services

- **web** — Django BFF
  Handles auth, UI, orchestration, and service-client integration.

- **projects** — Flask Projects Service
  Owns project data and project CRUD logic.

- **time-tracking** — Flask Time Tracking Service
  Owns time entries, clock-in/clock-out, and time-tracking CRUD logic.

### Databases

Each service owns its own database:

- `web-db`
- `projects-db`
- `time-tracking-db`

---

## Service URLs

### Host machine URLs

```text
Django web app:          http://localhost:8000
Projects service:        http://localhost:5000
Time-tracking service:   http://localhost:5001
```
API docs:

```text
Projects service:        http://localhost:5000/docs
Time-tracking service:   http://localhost:5001/docs
```

### Internal Docker URLs

Used when one container calls another:

```text
Projects service:        http://projects:5000
Time-tracking service:   http://time-tracking:5000
```



---

## Getting Started


```bash
docker compose up --build
```

---

## Database & Migrations

### First-time setup

Run this after cloning the project or after deleting Docker volumes.

```bash
docker compose up --build -d && \
docker compose run --rm web python manage.py migrate && \
docker compose run --rm projects flask --app app.main:create_app db init && \
docker compose run --rm projects flask --app app.main:create_app db migrate -m "Initial migration" && \
docker compose run --rm projects flask --app app.main:create_app db upgrade && \
docker compose run --rm time-tracking flask --app app.main:create_app db init && \
docker compose run --rm time-tracking flask --app app.main:create_app db migrate -m "Initial migration" && \
docker compose run --rm time-tracking flask --app app.main:create_app db upgrade
```

---

### Ongoing migration workflow

#### Django web service

```bash
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

#### Flask services


```bash
docker compose run --rm <service> flask --app app.main:create_app db migrate -m "message"
docker compose run --rm <service> flask --app app.main:create_app db upgrade
```

---
### Run all tests and linting

```bash
docker compose run --rm web sh -c "python manage.py test && flake8" && \
docker compose run --rm projects sh -c "pytest && flake8" && \
docker compose run --rm time-tracking sh -c "pytest && flake8"
```

---

## Useful Docker Commands

Stop containers

```bash
docker compose down
```

Stop containers and delete volumes (Warning: this deletes local database data.)

```bash
docker compose down -v
```

List volumes:

```bash
docker volume ls
```

Rebuild from scratch

```bash
docker compose down -v
docker compose up --build
```

---

## Development Notes

- `web` should call Flask services using internal Docker URLs.
- Host ports are only for browser/Postman access from your machine.
- Each service owns its own database and should not directly query another service's database.
- Cross-service ownership is passed using the `X-User-ID` request header.
