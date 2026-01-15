# Stage 1: Build Frontend
FROM node:22-slim AS frontend-build
WORKDIR /app
# Copy frontend source
COPY frontend/ ./frontend/
# Ensure output directory structure exists (Vite builds to ../idm_logger/static)
RUN mkdir -p idm_logger/static
WORKDIR /app/frontend
# Install dependencies and build
ENV CI=true
RUN npm install -g pnpm && pnpm install && pnpm build

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
ARG SIGNAL_CLI_VERSION=0.12.8

RUN --mount=type=cache,target=/root/.cache/pip \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    default-jre-headless \
    tar \
    && pip install --no-cache-dir -r requirements.txt \
    && curl -fsSL -o /tmp/signal-cli.tar.gz \
        https://github.com/AsamK/signal-cli/releases/download/v${SIGNAL_CLI_VERSION}/signal-cli-${SIGNAL_CLI_VERSION}.tar.gz \
    && tar -xzf /tmp/signal-cli.tar.gz -C /opt \
    && ln -s /opt/signal-cli-${SIGNAL_CLI_VERSION}/bin/signal-cli /usr/local/bin/signal-cli \
    && rm /tmp/signal-cli.tar.gz \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*


# Copy application backend
COPY idm_logger/ idm_logger/

# Copy built frontend artifacts from build stage
COPY --from=frontend-build /app/idm_logger/static/ idm_logger/static/

# Create data directory for persistent storage (SQLite, secret key)
RUN mkdir -p /app/data
VOLUME /app/data

# Set DATA_DIR environment variable for persistence
ENV DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Health check using Python instead of curl (no extra packages needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)" || exit 1

CMD ["python", "-m", "idm_logger.logger"]
