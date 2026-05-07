# django-flask-microservices-project

## Overview

This project is a microservice-based time tracking system designed to demonstrate modern backend architecture using Django, Flask, and FastAPI.

The system will allow users to:

- Create and manage projects
- Clock in and out of work sessions
- Track time across projects
- Manage tasks associated with projects
- View aggregated metrics and insights

The architecture follows a **backend-for-frontend (BFF)** pattern using Django, with domain-specific logic split across independent services.

---

## Architecture

The system will be composed of multiple services:

- **Django (Web / BFF)** *(later phase)*
  Handles authentication, user interaction, and orchestration between services

- **Projects Service (Flask)** *(later phase)*
  Manages project creation, updates, and lifecycle (active/archived)

- **Time Tracking Service (Flask)** *(later phase)*
  Handles clock-in/clock-out and time entry management

- **Tasks Service (Flask)** *(later phase)*
  Manages project tasks and status tracking

- **Metrics Service (FastAPI)** *(later phase)*
  Provides aggregated reporting and analytics

Each service owns its own data and communicates via HTTP APIs.

---


## 📦 Running Locally

### Prerequisites

Before running this project, ensure you have:

- Git (to clone the repository)
- Docker & Docker Compose (to run the application)

> If you're using Windows or macOS, install Docker Desktop which includes Docker Compose.

### 1. Clone Repository

```bash
git clone https://github.com/xMattC/..........
cd .............
```

### 2. Run migrations for all services:


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

### 3. Seed Data

```bash
TODO
```

### 4. Create Superuser

Run the following command to create a superuser (non-interactive):

```bash
docker-compose run --rm \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  -e DJANGO_SUPERUSER_PASSWORD=change-me \
  app python manage.py createsuperuser --noinput
```

Example local admin:
> Email: admin@example.com<br>
> Password: change-me<br>
> (Local development only)

### 5. Start Server

```bash
docker-compose up
```
---
### User Login

**web home:**
http://localhost:8000

### Accessing Admin

**Admin URL:**
http://localhost:8000/admin/

Login using the local admin credentials above.


---
### Run all Tests & Linting


```bash
clear && \
echo "Running all tests and linting across services..." && \
docker compose run --rm web python manage.py test ; \
docker compose run --rm projects pytest ; \
docker compose run --rm time-tracking pytest ; \
docker compose run --rm web flake8 ; \
docker compose run --rm projects flake8 ; \
docker compose run --rm time-tracking flake8
```

