FROM nginxinc/nginx-unprivileged:1-alpine

LABEL maintainer="xMattC"

COPY ./default-http.conf.tpl /etc/nginx/default-http.conf.tpl
COPY ./default-ssl.conf.tpl /etc/nginx/default-ssl.conf.tpl
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=web
ENV APP_PORT=8000

USER root

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

USER nginx

CMD ["/run.sh"]