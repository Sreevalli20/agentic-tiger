FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (dockerContext is ., so we're in backend/ directory)
COPY . .

# Copy corpus file from app directory to backend root (ensures it's available at both locations)
COPY app/corpus_production.jsonl ./corpus_production.jsonl
COPY app/corpus_production.jsonl ./app/corpus_production.jsonl

# Create necessary directories
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application with gunicorn for production (single worker for memory efficiency)
CMD ["gunicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout", "300", "--graceful-timeout", "60"]
