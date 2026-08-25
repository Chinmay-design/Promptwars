FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8080

CMD exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}
