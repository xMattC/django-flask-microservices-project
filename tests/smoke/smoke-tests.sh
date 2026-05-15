#!/bin/sh

set -e

COMPOSE_FILES="-f docker-compose.yml -f docker-compose-deploy.yml"

export ENABLE_SSL=false

cleanup() {
  echo ""
  echo "=================================================="
  echo "Stop platform stack"
  echo "=================================================="

  docker compose ${COMPOSE_FILES} down --remove-orphans
}

trap cleanup EXIT

echo ""
echo "=================================================="
echo "Validate deployment Docker Compose config"
echo "=================================================="

docker compose ${COMPOSE_FILES} config

echo ""
echo "=================================================="
echo "Build all services"
echo "=================================================="

docker compose ${COMPOSE_FILES} build

echo ""
echo "=================================================="
echo "Start platform stack"
echo "=================================================="

docker compose ${COMPOSE_FILES} up -d

echo ""
echo "=================================================="
echo "Wait for containers to stabilise"
echo "=================================================="

sleep 8

echo ""
echo "=================================================="
echo "Check for failed/restarting containers"
echo "=================================================="

FAILED_CONTAINERS=$(docker compose ${COMPOSE_FILES} ps \
  --format '{{.Name}} {{.State}}' \
  | grep -E 'exited|restarting|dead' || true)

if [ -n "$FAILED_CONTAINERS" ]; then
  echo ""
  echo "ERROR: One or more containers failed after startup:"
  echo "$FAILED_CONTAINERS"

  echo ""
  echo "=================================================="
  echo "Container logs"
  echo "=================================================="

  docker compose ${COMPOSE_FILES} logs --tail=100

  exit 1
fi

echo ""
echo "=================================================="
echo "Check running containers"
echo "=================================================="

docker compose ${COMPOSE_FILES} ps

echo ""
echo "=================================================="
echo "Run database migrations"
echo "=================================================="

docker compose ${COMPOSE_FILES} run --rm web python manage.py migrate

docker compose ${COMPOSE_FILES} run --rm projects flask --app app.main:create_app db upgrade

docker compose ${COMPOSE_FILES} run --rm time-tracking flask --app app.main:create_app db upgrade

docker compose ${COMPOSE_FILES} run --rm tasks flask --app app.main:create_app db upgrade

echo ""
echo "=================================================="
echo "Run health checks"
echo "=================================================="

curl -fsS -o /dev/null http://localhost
curl -fsS http://localhost:5000/api/health
curl -fsS http://localhost:5001/api/health
curl -fsS http://localhost:5002/api/health

echo ""
echo "=================================================="
echo "Platform startup smoke test passed"
echo "=================================================="