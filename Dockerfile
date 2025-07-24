# Adobe Hackathon 2025 Compliant Dockerfile
FROM python:3.10-slim

# Metadata for hackathon submission
LABEL maintainer="hackathon-participant"
LABEL version="1.0"
LABEL description="Adobe India Hackathon 2025 - PDF Document Intelligence"

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

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY collections/ ./collections/

# Create necessary directories with proper permissions
RUN mkdir -p /app/input /app/output /app/logs /app/models && \
    chown -R appuser:appuser /app

# Set Python environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ROUND=1A

# Switch to non-root user
USER appuser

# Health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import app.main; print('Health check passed')" || exit 1

# Expose port if needed (optional for hackathon)
# EXPOSE 8080

# Default command with proper error handling
CMD ["python", "-u", "app/main.py"]
