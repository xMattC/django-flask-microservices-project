# Services Overview

This directory contains all backend application services used by the system.

---
## Web — Django BFF

The Web service acts as the backend-for-frontend (BFF) layer.

Responsible for:

- Authentication
- Session management
- UI rendering
- Service orchestration
- Calling downstream microservices

Owns:
- `web-db`


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
```

 API Docs

```text
Projects service:        http://localhost:5000/docs
Time-tracking service:   http://localhost:5001/docs
```

---
### Development Rules

- Each service owns its own database.
- Services must communicate via HTTP APIs.
- Services should not directly query another service's database.
- User ownership is passed using the X-User-ID request header.

### Run all Tests & Linting


```bash
# clear local dev:
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d

# All-tests:
printf "\nRunning all tests...\n\n"
docker compose run --rm web python manage.py test && printf "\n---\n" && \
docker compose run --rm projects pytest && printf "\n---\n" && \
docker compose run --rm time-tracking pytest && printf "\n---\n"

# All-linting:
printf "\nRunning all linting...\n\n"
docker compose run --rm web flake8 && printf "\n---\n" && \
docker compose run --rm projects flake8 && printf "\n---\n" &&\
docker compose run --rm time-tracking flake8 && printf "\n---\n"
```