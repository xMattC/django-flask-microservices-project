#!/bin/sh

set -e

flask db upgrade

gunicorn \
    --bind 0.0.0.0:5002 \
    --workers 4 \
    --threads 2 \
    "app:create_app()"