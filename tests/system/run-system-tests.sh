#!/usr/bin/env bash

set -euo pipefail

COMPOSE_PROJECT_NAME=productivity-system
COMPOSE_FILES="-f tests/system/docker-compose.system.yml"
NETWORK_NAME="${COMPOSE_PROJECT_NAME}_default"

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

export DJANGO_SECRET_KEY=system-test-secret-key
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web
export CSRF_TRUSTED_ORIGINS=http://localhost,http://localhost:8000
export ENABLE_SSL=false

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cd "$PROJECT_ROOT"

cleanup() {
    printf "\nStopping services...\n\n"

    docker compose \
        -p "$COMPOSE_PROJECT_NAME" \
        $COMPOSE_FILES \
        down -v --remove-orphans
}

trap cleanup EXIT

printf "\nCleaning previous stack...\n\n"

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    down -v --remove-orphans || true

printf "\nStarting services...\n\n"

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    up -d --build

printf "\nRunning migrations...\n\n"

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    exec -T web \
    python manage.py migrate

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    exec -T projects \
    flask --app app.main:create_app db upgrade

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    exec -T time-tracking \
    flask --app app.main:create_app db upgrade

docker compose \
    -p "$COMPOSE_PROJECT_NAME" \
    $COMPOSE_FILES \
    exec -T tasks \
    flask --app app.main:create_app db upgrade

printf "\nBuilding system test image...\n\n"

docker build \
    -t productivity-system-tests \
    ./tests/system

printf "\nRunning system e2e tests...\n\n"

docker run --rm \
    --network "$NETWORK_NAME" \
    -e PROJECTS_SERVICE_URL=http://projects:5000/api \
    -e TIME_TRACKING_SERVICE_URL=http://time-tracking:5000/api \
    productivity-system-tests

printf "\nSystem tests completed successfully.\n"