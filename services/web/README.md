# Web service (Django BFF)

Django Backend-for-Frontend responsible for **auth, UI, orchestration, and service-client integration**.

This service:

* Owns Django app data and user-facing logic
* Connects to its own database (`web-db`)
* Calls Flask microservices using internal Docker service URLs
* Passes `X-User-ID` headers to downstream services

---

## Tech Stack

- **Backend:** Python, Django
- **Database:** PostgreSQL
- **Database Migrations:** Django migrations
- **Service Clients:** Python `requests`
- **Infrastructure:** Docker, Docker Compose
- **Integration Pattern:** Django BFF → Flask microservices using `X-User-ID` request headers

---

## Running the Service

From the **project root**:

### 1. Run the full system

```bash
docker compose up --build
```

### 2. Run ONLY the web service

```bash
docker compose up --build web
```

### App URL

http://localhost:8000

---

## Database & Migrations

### Start database only

```bash
docker compose up -d web-db
```

### Create migrations

```bash
docker compose run --rm web python manage.py makemigrations
```

### Apply migrations

```bash
docker compose run --rm web python manage.py migrate
```

### Create superuser

```bash
docker compose run --rm web python manage.py createsuperuser
```

### Open Django shell

```bash
docker compose run --rm web python manage.py shell
```

---

## Docker Notes

* Exposed on host port `8000`
* Runs internally on port `8000`
* Uses `web-db` as its PostgreSQL service

Mounted volume for live reload:

```yaml
./services/web:/web
```

Django runs via:

```bash
python manage.py wait_for_db && python manage.py runserver 0.0.0.0:8000
```

---

## Tests & Linting

```bash
docker compose run --rm web python manage.py test
docker compose run --rm web flake8
docker compose run --rm web sh -c "python manage.py test && flake8"
```
