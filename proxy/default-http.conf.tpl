server {
    listen ${LISTEN_PORT};

    location /static/ {
        alias /vol/web/static/;
    }

    location / {
        proxy_pass http://${APP_HOST}:${APP_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}