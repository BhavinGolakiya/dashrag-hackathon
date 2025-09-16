# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1         PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1         POETRY_VIRTUALENVS_CREATE=false

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends         build-essential         gcc         curl         libpq-dev         netcat-openbsd         && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
# Copy the most common dependency file names; if your repo uses a different path, adjust here.
COPY requirements.txt* /app/
RUN if [ -f /app/requirements.txt ]; then pip install -r /app/requirements.txt; fi

# Copy project
#COPY . /app

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Collect static at runtime (volume)
ENV DJANGO_SETTINGS_MODULE=hackathon_ai_dashboard.settings
ENV PORT=8000
EXPOSE 8000

# Entrypoint handles DB wait, migrations, collectstatic, then launches gunicorn
COPY entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh

# Create a non-root user 'app' with home dir /app
RUN addgroup --system app && adduser --system --ingroup app app

# Make sure working dir is owned by app
RUN chown -R app:app /app

# RUN mkdir -p /app/staticfiles /app/data /app/.cache/huggingface/transformers && \
#     chown -R app:app /app/staticfiles /app/data /app/.cache

RUN mkdir -p /app/staticfiles /app/data /app/.cache/huggingface/transformers && \
    (chown -R app:app /app/staticfiles /app/data /app/.cache || true)

#USER app

CMD ["/entrypoint.sh"]
