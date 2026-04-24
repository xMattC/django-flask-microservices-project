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

## Development Workflow

Work is organised using GitHub Projects:

- **Planning** – tasks grouped by development phase
- **Work** – Kanban board for tracking progress
- **Roadmap** – timeline view of project phases

Each phase is tracked using GitHub milestones.

---

## Getting Started

### Build containers

```bash
docker compose build

## Getting Started

### Build the containers

```bash
docker compose build
```

### Run the application

```bash
docker compose up
```

### Access the app

Open your browser:

http://localhost:8000

---

## Running Django Commands

```bash
docker compose run --rm web python manage.py <command>
```

**Explanation:**

- `docker compose run` → runs a one-off command in a new container
- `--rm` → removes the container after execution
- `web` → service name
- `manage.py` → Django CLI
- `sh -c` → runs the command through a shell, enabling features like command chaining (&&)
---

## Common Commands

```bash
docker compose run --rm web python manage.py test

docker compose run --rm web python manage.py createsuperuser

docker compose run --rm web python manage.py makemigrations

docker compose run --rm web python manage.py migrate

docker compose run --rm web python manage.py shell

docker compose run --rm web flake8
```

###  Multiple Commands

```Bash
docker compose run --rm web sh -c "python manage.py test && flake8"
```

---

## Development (VS Code Dev Container)

1. Install the "Dev Containers" extension in VS Code
2. Open the project folder
3. Run: "Dev Containers: Reopen in Container"

This will start the development environment inside Docker.

### Workflow

- **Planning** – organise issues by phase and define scope
- **Work** – track active development using a Kanban board
- **Roadmap** – visualise progress and phases over time
