FROM python:3.12-slim

# Install gcc for building psutil
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from telemetry_server directory
COPY telemetry_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files from telemetry_server
COPY telemetry_server/ .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
