# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY . .

# Create session directory
RUN mkdir -p temp_sessions && chmod 777 temp_sessions

EXPOSE 8000

# Run application
CMD ["chainlit", "run", "app_c.py", "--host", "0.0.0.0", "--port", "8000", "--headless"]
