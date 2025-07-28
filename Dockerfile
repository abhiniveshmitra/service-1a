# Adobe Hackathon 2025 - Service 1A: PDF Outline Extraction
FROM python:3.10-slim

# Metadata for Service 1A
LABEL maintainer="hackathon-participant"
LABEL version="1.0"
LABEL description="Adobe India Hackathon 2025 - Service 1A: PDF Outline Extraction"

# Set working directory
WORKDIR /app

# Install system dependencies required for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with no cache to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy ONLY Service 1A application code
COPY app/ ./app/

# Create necessary directories for Service 1A with proper permissions
RUN mkdir -p /app/input /app/output /app/logs && \
    chown -R appuser:appuser /app

# Set Python environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE=1A
ENV ROUND=round1a

# Switch to non-root user
USER appuser

# Expose port if needed (optional for hackathon)
# EXPOSE 8080

# Default command for Service 1A
CMD ["python", "-u", "app/main.py"]
