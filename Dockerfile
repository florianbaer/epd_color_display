# Dockerfile for EPD Color Display
# Single container with backend serving built frontend

# Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for hardware support
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir .

# Install hardware dependencies (for Raspberry Pi deployment)
RUN pip install --no-cache-dir gpiozero lgpio spidev || true

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
