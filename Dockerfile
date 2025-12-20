FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 fareglitch && chown -R fareglitch:fareglitch /app
USER fareglitch

# Expose API port
EXPOSE 8000

# Default command - use PORT env var from Railway
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
