# Dockerfile for Railway/Render backend deployment (Hybrid RAG System)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag_api.py .
COPY src/ ./src/
COPY *.py .

# Create data directory structure
RUN mkdir -p data/scraped data/scraped_dpmptsp data/scraped_ptsp_indonesia

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Start command - use production version for faster startup
CMD ["python", "rag_api_production.py"]
