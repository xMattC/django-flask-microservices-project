# django-flask-microservices-project

## Overview

This project is a backend template designed for building applications using a Django web service and Flask microservices.

This stage includes:
- Django running in Docker
- SQLite database (development only)

---

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