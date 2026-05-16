# Proxy Service

This directory contains the NGINX reverse proxy configuration for the Productivity Microservices Platform.

The proxy is responsible for routing external HTTP/HTTPS traffic to the Django web service and serving collected static files.

---

## Purpose

The proxy service provides:

- Reverse proxy routing to the Django web service
- Static file serving from the shared static volume
- Optional HTTPS configuration for production deployment
- Forwarded request headers for upstream application awareness

In this project, the Django web service remains the main application entry point. The proxy sits in front of it and handles incoming web traffic.

---

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Builds the NGINX proxy image |
| `default-http.conf.tpl` | HTTP-only NGINX configuration template |
| `default-ssl.conf.tpl` | HTTPS NGINX configuration template |
| `run.sh` | Selects the correct NGINX config at container startup |

---

## Runtime Configuration

The proxy uses environment variables to generate the final NGINX configuration when the container starts.

| Variable | Purpose | Default |
|---|---|---|
| `LISTEN_PORT` | Port NGINX listens on for HTTP traffic | `8000` |
| `APP_HOST` | Upstream Django service hostname | `web` |
| `APP_PORT` | Upstream Django service port | `8000` |
| `ENABLE_SSL` | Enables HTTPS configuration when set to `true` | unset / false |

---

## HTTP Mode

When `ENABLE_SSL` is not set to `true`, the proxy uses:

```text
default-http.conf.tpl
```
This mode:
- Listens on ${LISTEN_PORT}
- Serves /static/ files from /vol/web/static/
- Proxies all other requests to http://${APP_HOST}:${APP_PORT}

## HTTPS Mode

When `ENABLE_SSL`=true, the proxy uses:

```text
default-ssl.conf.tpl
```
This mode:

- Redirects HTTP traffic to HTTPS
- Serves HTTPS traffic on port 8443
- Uses Let's Encrypt certificate paths
- Proxies application requests to the Django web service

The current SSL configuration is intended for the deployed domain: `productivity-app.xmattc.com`

---
# Static Files

Static files are served directly by NGINX from: `/vol/web/static/`

This allows the Django application to focus on dynamic application behaviour while NGINX handles static asset delivery.

---