# Time-tracking service (Flask)

Lightweight Flask microservice responsible for **time-tracking CRUD**.

This service:

* Owns time-tracking data and logic
* Uses `X-User-ID` for ownership
* Has its own database (`time-tracking-db`)
* Is completely independent from Django (`web/`)

---

## Tech Stack

- **Microservice Backend:** Python, Flask
- **API Documentation Layer:** Flask-Smorest — adds OpenAPI/Swagger docs and API route metadata
- **Request Validation / Serialization:** Marshmallow — schema-based request validation and API response serialization
- **Database Access:** SQLAlchemy — ORM for defining models and querying PostgreSQL
- **Database Migrations:** Flask-Migrate / Alembic — manages database schema changes
- **Database:** PostgreSQL
- **Infrastructure:** Docker, Docker Compose
- **Integration Pattern:** Django BFF → Flask microservice using `X-User-ID` request headers

---

## Running the Service

From the **repository root**:

### 1. Run the full system
```bash
docker compose up --build
```

### 2. Run ONLY the time-tracking service
```bash
docker compose up --build time-tracking
```

### Service URL

http://localhost:5001


### Service API Docs

http://localhost:5000/docs

---

## Health Checks

### Service health

```bash
curl http://localhost:5001/health
```

Expected:

```json
{"status": "ok"}
```
### DB health

```bash
curl http://localhost:5001/db-health
```

Expected:

```json
{"database": "ok"}
```

---

## Database & Migrations

### Start database only

```bash
docker compose up -d time-tracking-db
```

### Initialise migrations (run once)
```bash
docker compose run --rm time-tracking flask --app app.main:create_app db init
```

### Create a migration

```bash
docker compose run --rm time-tracking flask --app app.main:create_app db migrate -m "message"
```

### Apply migrations

```bash
docker compose run --rm time-tracking flask --app app.main:create_app db upgrade
```

### Quick diagnostic:
```bash
docker compose exec time-tracking -db psql -U time_tracking_user -d time_tracking_db -c "\dt"
docker compose exec time-tracking -db psql -U time_tracking_user -d time_tracking_db -c "select * from alembic_version;"
```

---
## Docker Notes

* Exposed on host port `5001`
* Runs internally on port `5000`

* Mounted volume for live reload:

```yaml
./services/time-tracking:/app
```

Flask runs via:

```bash
flask --app app.main:create_app run --host=0.0.0.0 --port=5000 --debug
```

---

## Tests & Linting

```bash
docker compose run --rm time-tracking python -m pytest
docker compose run --rm time-tracking flake8
docker compose run --rm time-tracking sh -c "python -m pytest && flake8"
```

