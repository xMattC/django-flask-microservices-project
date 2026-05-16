#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cd "$PROJECT_ROOT"

printf "\nStarting services...\n\n"
docker compose up -d --build

printf "\nRunning migrations...\n\n"
docker compose exec -T web python manage.py migrate

docker compose exec -T projects \
    flask --app app.main:create_app db upgrade

docker compose exec -T time-tracking \
    flask --app app.main:create_app db upgrade

printf "\nBuilding system test image...\n\n"
docker build \
    -t productivity-system-tests \
    ./tests/system

printf "\nRunning system e2e tests...\n\n"
docker run --rm \
    --network django-flask-microservices-project_default \
    -e PROJECTS_SERVICE_URL=http://projects:5000/api \
    -e TIME_TRACKING_SERVICE_URL=http://time-tracking:5000/api \
    productivity-system-tests