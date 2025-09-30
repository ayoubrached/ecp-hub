# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (for building wheels like lxml, PyMuPDF if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    libglib2.0-0 \
    libxext6 \
    libxrender1 \
    libsm6 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Cloud Run expects the server to listen on PORT env var
EXPOSE 8080

# Copy credentials and env last (if present)
COPY .env ./.env
COPY client_secret.json ./client_secret.json

# Start FastAPI with Uvicorn; respect Cloud Run PORT or default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
