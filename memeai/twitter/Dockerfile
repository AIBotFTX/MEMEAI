# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=600 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/usr/local" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    POETRY_NO_INTERACTION=1 \
    PIP_INDEX_URL=https://pypi.org/simple \
    PIP_EXTRA_INDEX_URL=https://pypi.doubanio.com/simple \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using the official installer
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

# Copy only dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies including development dependencies for hot reload
RUN poetry install --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy the initial application code (will be overridden by volume mount)
COPY memeai /app/memeai/

# Create necessary directories
RUN mkdir -p /app/logs

# Create a non-root user
RUN useradd -m -u 1000 twitter_user \
    && chown -R twitter_user:twitter_user /app

# Switch to non-root user
USER twitter_user

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with hot reload
RUN python memeai/agents/init_agent.py

CMD ["poetry", "run", "uvicorn", "memeai.twitter.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]