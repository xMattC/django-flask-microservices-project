#!/bin/bash

set -e

# Move to repository root.
cd "$(dirname "$0")/../../.."

COMPOSE_FILES="-f docker-compose.yml -f docker-compose-deploy.yml"

reset_demo_data() {
    echo "[$(date)] Resetting demo data..."

    docker compose ${COMPOSE_FILES} exec -T web \
        python manage.py seed_demo_data --reset

    echo "[$(date)] Demo data reset complete."
}

install_cron() {
    SCRIPT_PATH="$(realpath "$0")"
    LOG_PATH="$HOME/demo_seed.log"

    CRON_JOB="0 2 * * * ${SCRIPT_PATH} >> ${LOG_PATH} 2>&1"

    echo "Installing cron job:"
    echo "${CRON_JOB}"

    (
        crontab -l 2>/dev/null | grep -vF "${SCRIPT_PATH}" || true
        echo "${CRON_JOB}"
    ) | crontab -

    echo "Cron job installed."
    echo "Demo data will reset every day at 02:00."
}

case "${1:-}" in
    --install-cron)
        install_cron
        ;;
    *)
        reset_demo_data
        ;;
esac