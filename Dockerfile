# Dockerfile for Railway/Render backend deployment (Optimized)
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-light.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only essential application code (exclude large data files)
COPY rag_api.py .
COPY src/ ./src/
COPY *.py .

# Create data directory structure but don't copy large files
RUN mkdir -p data

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Start command
CMD uvicorn rag_api_light:app --host 0.0.0.0 --port $PORT
