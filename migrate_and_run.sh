#!/bin/sh
alembic upgrade head

gunicorn \
    app.main:app \
    -w 1 \
    -k uvicorn.workers.UvicornWorker \
    --access-logfile - \
    -b 0.0.0.0:8000
