# Projects service (Flask)

Lightweight Flask microservice responsible for **Projects CRUD**.

This service:

* Owns Projects data and logic
* Uses `X-User-ID` for ownership
* Has its own database (`projects-db`)
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

### 2. Run ONLY the Projects service
```bash
docker compose up --build projects
```

### Service URL

http://localhost:5000


### Service API Docs

http://localhost:5000/docs

---

## Health Checks

### Service health

```bash
curl http://localhost:5000/health
```

Expected:

```json
{"status": "ok"}
```
### DB health

```bash
curl http://localhost:5000/db-health
```

Expected:

```json
{"database": "ok"}
```

---

## Database & Migrations

### Start database only

```bash
docker compose up -d projects-db
```

### Initialise migrations (run once)
```bash
docker compose run --rm projects flask --app app.main:create_app db init
```

### Create a migration

```bash
docker compose run --rm projects flask --app app.main:create_app db migrate -m "message"
```

### Apply migrations

```bash
docker compose run --rm projects flask --app app.main:create_app db upgrade
```

---
## Docker Notes

* Exposed on host port `5000`
* Runs internally on port `5000`

* Mounted volume for live reload:

```yaml
./services/projects:/app
```

Flask runs via:

```bash
flask --app app.main:create_app run --host=0.0.0.0 --port=5000 --debug
```

---

## Tests & Linting

```bash
docker compose run --rm Projects python -m pytest
docker compose run --rm Projects flake8
docker compose run --rm Projects sh -c "python -m pytest && flake8"
```

