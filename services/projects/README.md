# Projects Service (Flask)

Lightweight Flask microservice responsible for **project CRUD**.

This service:

* Owns project data and logic
* Uses `X-User-ID` for ownership
* Is completely independent from Django (`web/`)

---

## 🚀 Running the Service

### 1. Run the full system (recommended)

From the **project root**:

```bash
docker compose up --build
```

This starts:

* Django (`web`)
* Projects service (`projects`)
* Database (`db`)

---

### 2. Run ONLY the projects service

```bash
docker compose up --build projects
```

This is useful for:

* Fast iteration
* API testing in isolation
* Debugging

---

### 3. Stop everything

```bash
docker compose down
```

---

## Service URL

When running:
http://localhost:5000

---

## Quick Test (Health Check)

```bash
curl http://localhost:5000/health
```

Expected:

```json
{"status": "ok"}
```




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

## Running Tests & linting

```bash
docker compose run --rm projects python -m pytest

docker compose run --rm projects flake8

docker compose run --rm projects sh -c "python -m pytest && flake8"
```

