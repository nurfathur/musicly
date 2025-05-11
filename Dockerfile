FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set proper permissions for temp directories
RUN mkdir -p /tmp/audio && \
    chmod 777 /tmp/audio && \
    mkdir -p /app/temp && \
    chmod 777 /app/temp

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# IMPORTANT: Don't copy cookies.txt directly - it will be created from environment variable

# Set proper permissions for application files
RUN chmod -R 755 /app

# Create a non-root user but still allow access to needed directories
RUN useradd -m appuser && \
    chown -R appuser:appuser /app /tmp/audio

# Run as non-root user for better security
USER appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FFMPEG_PATH=/usr/bin/ffmpeg \
    TEMP_DIR=/tmp/audio

# Expose port
EXPOSE 5000

# Run the application with Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:application