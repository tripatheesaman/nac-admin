# syntax=docker/dockerfile:1
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build deps for wheels
RUN apk add --no-cache \
    build-base \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    cargo

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip wheel -w /wheels -r requirements.txt

# Copy project
COPY . .

FROM python:3.13-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Runtime deps
RUN apk add --no-cache libstdc++ ca-certificates

# Install wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Entrypoint and static dir
RUN chmod +x /app/entrypoint.sh

# Collect static (ignore errors if DB not available during build)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]


