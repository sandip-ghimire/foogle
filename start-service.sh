#!/bin/bash

(DJANGO_SETTINGS_MODULE=foogal.settings
DJANGO_WSGI_MODULE=foogal.wsgi

cd /app
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--workers 3 \
--bind=unix:/app/venv/gunicorn.sock \
--log-level=debug \
--timeout 120 \
--max-requests 5 \
--log-file=/var/log/gunicorn_error-log \
--access-logfile=/var/log/gunicorn_access-log \
--reload) &
nginx -g "daemon off;"