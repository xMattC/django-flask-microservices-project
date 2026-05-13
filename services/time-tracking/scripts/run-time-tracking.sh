#!/bin/sh

set -e

flask db upgrade

gunicorn \
    --bind 0.0.0.0:5001 \
    --workers 4 \
    --threads 2 \
    "app:create_app()"