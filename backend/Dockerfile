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

# Copy application code
COPY . .

# Ensure corpus file exists at expected locations
# The corpus should be at backend/corpus_production.jsonl in the repo
RUN if [ -f app/corpus_production.jsonl ]; then \
      cp app/corpus_production.jsonl corpus_production.jsonl; \
    elif [ -f corpus_production.jsonl ]; then \
      cp corpus_production.jsonl app/corpus_production.jsonl; \
    fi

# Create necessary directories
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application with uvicorn for production (better async support)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
