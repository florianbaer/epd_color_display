FROM python:3.13-slim

# Install system dependencies for GPIO/SPI
RUN apt-get update && apt-get install -y \
    gcc \
    swig \
    libgpiod2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.109.0 \
    uvicorn>=0.27.0 \
    google-genai>=0.2.0 \
    pillow>=12.1.0 \
    python-dotenv>=1.0.0 \
    apscheduler>=3.10.0 \
    gpiozero>=2.0.1 \
    lgpio>=0.2.2.0 \
    spidev>=3.8

# Create directories
RUN mkdir -p generated_images templates

# Expose port 80
EXPOSE 80

# Run uvicorn on port 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
