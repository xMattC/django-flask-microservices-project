#!/bin/sh

set -e

if [ "$ENABLE_SSL" = "true" ]; then
  envsubst '${LISTEN_PORT} ${APP_HOST} ${APP_PORT}' \
    < /etc/nginx/default-ssl.conf.tpl \
    > /etc/nginx/conf.d/default.conf
else
  envsubst '${LISTEN_PORT} ${APP_HOST} ${APP_PORT}' \
    < /etc/nginx/default-http.conf.tpl \
    > /etc/nginx/conf.d/default.conf
fi

nginx -g 'daemon off;'