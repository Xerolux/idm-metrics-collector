FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY idm_logger/ idm_logger/

# Create data directory for persistent storage (SQLite, secret key)
RUN mkdir -p /app/data
VOLUME /app/data

# Set working directory to data for persistence
WORKDIR /app/data

EXPOSE 5000

# Health check using Python instead of curl (no extra packages needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)" || exit 1

CMD ["python", "-m", "idm_logger.logger"]
