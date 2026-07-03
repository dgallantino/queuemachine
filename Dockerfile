# syntax=docker/dockerfile:1

# ---- Frontend assets (vendor + Tailwind CSS) ----
FROM node:20-alpine AS assets
WORKDIR /src

COPY package.json ./
COPY tailwind.config.js ./
COPY scripts/vendor_frontend.sh scripts/
COPY queue_app/static/queue_app/core/css/tailwind.src.css queue_app/static/queue_app/core/css/
COPY queue_app/templates queue_app/templates/

RUN apk add --no-cache bash curl \
    && npm install \
    && npm run build

# ---- Application ----
FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        ffmpeg \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

COPY . .

COPY --from=assets /src/queue_app/static/queue_app/vendor queue_app/static/queue_app/vendor
COPY --from=assets /src/queue_app/static/queue_app/core/css/tailwind.css queue_app/static/queue_app/core/css/tailwind.css

RUN chmod +x deploy/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
