#!/bin/sh

set -eu

COMPOSE_FILES="-f docker-compose.yml -f docker-compose-deploy.yml"

export ENABLE_SSL=false

export WEB_DB_NAME=web_db
export WEB_DB_USER=web_user
export WEB_DB_PASSWORD=changeme

export PROJECTS_DB_NAME=projects_db
export PROJECTS_DB_USER=projects_user
export PROJECTS_DB_PASSWORD=changeme

export TIME_TRACKING_DB_NAME=time_tracking_db
export TIME_TRACKING_DB_USER=time_tracking_user
export TIME_TRACKING_DB_PASSWORD=changeme

export TASKS_DB_NAME=tasks_db
export TASKS_DB_USER=tasks_user
export TASKS_DB_PASSWORD=changeme

export DJANGO_SECRET_KEY=smoke-test-secret-key
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
export CSRF_TRUSTED_ORIGINS=http://localhost,http://localhost:8000

section() {
  echo ""
  echo "=================================================="
  echo "$1"
  echo "=================================================="
}

cleanup() {
  section "Stop platform stack"
  docker compose ${COMPOSE_FILES} down -v --remove-orphans || true
}

show_logs_and_exit() {
  echo ""
  echo "ERROR: $1"

  section "Container status"
  docker compose ${COMPOSE_FILES} ps || true

  section "Container logs"
  docker compose ${COMPOSE_FILES} logs --tail=150 || true

  exit 1
}

check_containers() {
  FAILED_CONTAINERS=$(docker compose ${COMPOSE_FILES} ps \
    --format '{{.Name}} {{.State}}' \
    | grep -E 'exited|restarting|dead' || true)

  if [ -n "$FAILED_CONTAINERS" ]; then
    echo "$FAILED_CONTAINERS"
    show_logs_and_exit "One or more containers failed after startup."
  fi
}

wait_for_url() {
  URL="$1"
  NAME="$2"
  MAX_ATTEMPTS="${3:-30}"

  ATTEMPT=1

  while [ "$ATTEMPT" -le "$MAX_ATTEMPTS" ]; do
    if curl -fsS "$URL" >/dev/null 2>&1; then
      echo "$NAME is ready: $URL"
      return 0
    fi

    check_containers

    echo "Waiting for $NAME... attempt $ATTEMPT/$MAX_ATTEMPTS"
    ATTEMPT=$((ATTEMPT + 1))
    sleep 2
  done

  show_logs_and_exit "$NAME did not become ready: $URL"
}

trap cleanup EXIT

section "Clean previous smoke stack"
docker compose ${COMPOSE_FILES} down -v --remove-orphans || true

section "Validate deployment Docker Compose config"
docker compose ${COMPOSE_FILES} config >/tmp/platform-smoke-compose.yml
cat /tmp/platform-smoke-compose.yml

section "Build all services"
docker compose ${COMPOSE_FILES} build

section "Start platform stack"
docker compose ${COMPOSE_FILES} up -d

section "Wait for service health endpoints"
wait_for_url "http://localhost:5000/api/health" "Projects service"
wait_for_url "http://localhost:5001/api/health" "Time tracking service"
wait_for_url "http://localhost:5002/api/health" "Tasks service"

section "Run database migrations"
docker compose ${COMPOSE_FILES} exec -T web python manage.py migrate
docker compose ${COMPOSE_FILES} exec -T projects flask --app app.main:create_app db upgrade
docker compose ${COMPOSE_FILES} exec -T time-tracking flask --app app.main:create_app db upgrade
docker compose ${COMPOSE_FILES} exec -T tasks flask --app app.main:create_app db upgrade

section "Verify database migration state"
docker compose ${COMPOSE_FILES} exec -T projects flask --app app.main:create_app db current
docker compose ${COMPOSE_FILES} exec -T time-tracking flask --app app.main:create_app db current
docker compose ${COMPOSE_FILES} exec -T tasks flask --app app.main:create_app db current

section "Run public health checks"
curl -fsS -o /dev/null http://localhost:8000
curl -fsS http://localhost:5000/api/health
curl -fsS http://localhost:5001/api/health
curl -fsS http://localhost:5002/api/health

section "Check for failed/restarting containers"
check_containers

section "Check running containers"
docker compose ${COMPOSE_FILES} ps

section "Platform startup smoke test passed"