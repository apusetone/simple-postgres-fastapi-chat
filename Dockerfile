# Builder stage
FROM python:3.12 AS builder

RUN pip install --no-cache-dir pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN pdm export -o requirements.txt --prod \
    && pdm export -o requirements-dev.txt --dev

# Base stage
FROM python:3.12-slim AS base

WORKDIR /fastapi

RUN apt-get update \
    && apt-get -y install libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -U pip setuptools wheel

EXPOSE 8000
ENV APP_CONFIG_FILE=local
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--no-server-header", "--reload", "--reload-dir", "app"]

# Local development stage
FROM base AS local

COPY --from=builder /app/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Production stage
FROM base AS prod

COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/ /fastapi/app/
