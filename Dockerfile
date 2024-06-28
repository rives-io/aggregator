FROM python:3.11.4-slim-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN apt-get -q update \
    && apt-get install -yq --no-install-recommends build-essential \
        libpq5 libpq-dev curl \
    && pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential libpq-dev \
    && apt-get autoremove -y --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

CMD gunicorn \
    app.main:app \
    -w 1 \
    -k uvicorn.workers.UvicornWorker \
    --access-logfile - \
    -b 0.0.0.0:8000
