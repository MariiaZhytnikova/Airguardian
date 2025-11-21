# ================================================================
# 🚀 Drone Monitoring System — Dockerfile (Poetry Based)
# ================================================================

FROM python:3.11-slim AS base

# System settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# ---------------------------------------------------------------
# 🧰 System Dependencies
# ---------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------
# 📦 Install Poetry
# ---------------------------------------------------------------
ENV POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.2 python3 -

ENV PATH="/root/.local/bin:$PATH"

# Prevent Poetry from creating a virtualenv inside the container
RUN poetry config virtualenvs.create false

WORKDIR /app

# ---------------------------------------------------------------
# 📄 Copy project metadata
# ---------------------------------------------------------------
COPY pyproject.toml poetry.lock* ./

# ---------------------------------------------------------------
# 🔧 Install Dependencies
# ---------------------------------------------------------------
RUN poetry install --no-interaction --no-ansi --no-root

# ---------------------------------------------------------------
# 📁 Copy application code
# ---------------------------------------------------------------
COPY . .

# ---------------------------------------------------------------
# 🚀 Default command (overridden by docker-compose)
# ---------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
