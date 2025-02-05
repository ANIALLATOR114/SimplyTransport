# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Create non-root user early
RUN useradd -m appuser

# Set working directory
WORKDIR /app

# Install system dependencies including curl for healthcheck and postgres dev packages
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create and set ownership of necessary directories
RUN mkdir -p static && chown -R appuser:appuser /app

# Copy only the necessary application code
COPY SimplyTransport SimplyTransport/
COPY migrations migrations/
COPY .env .


# Set ownership of application files
RUN chown -R appuser:appuser /app/SimplyTransport /app/migrations /app/.env

# Switch to non-root user
USER appuser

# Command to run the application using uvicorn
CMD ["uvicorn", "SimplyTransport.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--env-file", ".env"] 