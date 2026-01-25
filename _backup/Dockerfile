FROM docker.io/python:3.13-slim

# Install system dependencies for GPIO/SPI
RUN apt-get update && apt-get install -y \
    gcc \
    swig \
    libgpiod2 \
    liblgpio-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject.toml first for dependency installation
COPY pyproject.toml .

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir .

# Copy rest of project files
COPY . .

# Create directories
RUN mkdir -p generated_images templates

# Expose port 80
EXPOSE 80

# Run uvicorn on port 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
