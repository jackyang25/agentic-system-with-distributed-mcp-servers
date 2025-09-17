# Production
FROM python:3.12-slim

EXPOSE 8000
WORKDIR /src

# Install only essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates docker.io \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --only=main --no-interaction --no-ansi

# Copy application code
COPY . .

CMD ["python", "app.py"]