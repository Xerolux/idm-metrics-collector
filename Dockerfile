FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY idm_logger/ idm_logger/
# Copy example config as default
COPY config.yaml.example config.yaml

EXPOSE 5000

CMD ["python", "-m", "idm_logger.logger"]
