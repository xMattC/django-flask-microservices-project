server {
    listen 8000;
    server_name productivity-app.xmattc.com;

    return 301 https://$host$request_uri;
}

server {
    listen 8443 ssl;
    server_name productivity-app.xmattc.com;

    ssl_certificate /etc/letsencrypt/live/productivity-app.xmattc.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/productivity-app.xmattc.com/privkey.pem;

    location /static/ {
        alias /vol/web/static/;
    }

    location / {
        proxy_pass http://${APP_HOST}:${APP_PORT};

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}