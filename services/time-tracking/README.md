# Time-tracking service (Flask)

Lightweight Flask microservice responsible for **time-tracking CRUD**.

This service:

* Owns time-tracking data and logic
* Uses `X-User-ID` for ownership
* Has its own database (`time-tracking-db`)
* Is completely independent from Django (`web/`)

---

## Running the Service

From the **project root**:

### 1. Run the full system
```bash
docker compose up --build
```

### 2. Run ONLY the time-tracking service
```bash
docker compose up --build time-tracking
```


### 3. Stop everything
```bash
docker compose down
```

## Service URL

http://localhost:5001

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

