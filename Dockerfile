# syntax=docker/dockerfile:1
# Dockerfile for EPD Color Display
# Single container with backend serving built frontend

# Build frontend
FROM docker.io/oven/bun:1-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/bun.lock* ./
RUN --mount=type=cache,target=/root/.bun/install/cache \
    bun install --frozen-lockfile
COPY frontend/ .
RUN bun run build

# Backend
FROM docker.io/python:3.11-slim

WORKDIR /app

# Install system dependencies for hardware support
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/pyproject.toml .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

# Install hardware dependencies (for Raspberry Pi deployment)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install gpiozero lgpio spidev || true

# Copy application code
COPY backend/app/ ./app/

# Copy frontend build
COPY --from=frontend-build /app/dist ./frontend/dist

# Create directories for data persistence
RUN mkdir -p /app/generated_images

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
