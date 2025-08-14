# Stage 1: Build CSS assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY assets/css/input.css ./assets/css/input.css
COPY tailwind.config.js ./
COPY templates/ ./templates/
COPY assets/js/ ./assets/js/

# Build CSS
RUN npm run build

# Stage 2: Production Flask application
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Copy application files
COPY --chown=app:app run.py .
COPY --chown=app:app app/ ./app/
COPY --chown=app:app templates/ ./templates/
COPY --chown=app:app assets/ ./assets/

# Copy built CSS from builder stage
COPY --from=builder --chown=app:app /app/assets/css/output.css ./assets/css/output.css

# Expose port
EXPOSE 5000

# Health check
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=3)"

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
