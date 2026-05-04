# Projects Service (Flask)

Lightweight Flask microservice responsible for **project CRUD**.

This service:

* Owns project data and logic
* Uses `X-User-ID` for ownership
* Has its own database (`projects-db`)
* Is completely independent from Django (`web/`)

---

## Running the Service

### 1. Run the full system (recommended)

From the **project root**:

```bash
docker compose up --build
```

This starts:

* Django (`web`)
* Projects service (`projects`)
* Databases (`db`, `projects-db`)

---

### 2. Run ONLY the projects service

```bash
docker compose up --build projects
```

Starts:

* `projects`
* `projects-db`

---

### 3. Stop everything

```bash
docker compose down
```

Reset DBs (deletes data):

```bash
docker compose down -v
```

---

## Service URL

http://localhost:5000

---


## Service API Docs

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

---

### Database health

```bash
curl http://localhost:5000/db-health
```

Expected:

```json
{"database": "ok"}
```

---

## Database & Migrations

### Start DB only

```bash
docker compose up -d projects-db
```

---

### Initialise migrations (run once first thime then ignore)

```bash
docker compose run --rm projects flask --app app.main:create_app db init
```

---

### Create a migration

```bash
docker compose run --rm projects flask --app app.main:create_app db migrate -m "message"
```

---

### Apply migrations

```bash
docker compose run --rm projects flask --app app.main:create_app db upgrade
```

---

### Notes

* DB must be running for migrations
* App does NOT need to be running
* Migration files are auto-generated (safe to exclude from linting)

---

## Docker Notes

* Runs on port `5000`
* Mounted volume for live reload:

```yaml
- ./services/projects:/app
```

* Flask runs via:

```bash
flask --app app.main:create_app run --host=0.0.0.0 --port=5000 --debug
```

---

## Tests & Linting

```bash
docker compose run --rm projects python -m pytest
docker compose run --rm projects flake8
docker compose run --rm projects sh -c "python -m pytest && flake8"
```

---

## Dev Notes

* Use service name for internal calls:

```
http://projects:5000
```

* Never use `localhost` between containers
* DB config comes from environment variables
* Models define DB schema → migrations apply it

