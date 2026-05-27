FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared/ ./shared/

# Build argument for service path
ARG SERVICE_PATH
ENV SERVICE_PATH=${SERVICE_PATH}

# Copy service code
COPY ${SERVICE_PATH}/ ./service/

# Set PYTHONPATH to include shared library
ENV PYTHONPATH=/app

# Expose port based on service
EXPOSE 8000

# Run the service
CMD ["sh", "-c", "python -m uvicorn service.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
