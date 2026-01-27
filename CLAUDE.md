# CLAUDE.md - AI Assistant Guide for IDM Metrics Collector

> **Purpose**: This document provides comprehensive guidance for AI assistants (like Claude) working with the IDM Metrics Collector codebase. It covers architecture, conventions, workflows, and best practices.

**Last Updated**: 2026-01-27
**Version**: 1.0.1

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Directory Structure](#directory-structure)
4. [Development Workflows](#development-workflows)
5. [Key Conventions & Patterns](#key-conventions--patterns)
6. [Testing Guidelines](#testing-guidelines)
7. [Docker & Deployment](#docker--deployment)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Important Files & Their Roles](#important-files--their-roles)
10. [Common Tasks](#common-tasks)
11. [Security Considerations](#security-considerations)
12. [Frontend Guidelines](#frontend-guidelines)
13. [Backend Guidelines](#backend-guidelines)
14. [Integration Points](#integration-points)
15. [Gotchas & Special Considerations](#gotchas--special-considerations)

---

## Project Overview

### What is IDM Metrics Collector?

**IDM Metrics Collector v1.0.1** is a professional, Docker-based monitoring, control, and automation solution for IDM heat pumps and compatible systems (Nibe, Luxtronik, Daikin). It provides:

- **Real-time monitoring** via Modbus TCP protocol
- **Long-term analysis** using VictoriaMetrics time-series database
- **Intelligent alerting** with ML-based anomaly detection (River/scikit-learn)
- **Complete heat pump control** through a modern Vue 3 dashboard
- **Multi-channel notifications** (Telegram, Discord, Email, Signal, MQTT, ntfy)
- **Multi-heatpump support** (manage multiple units from one interface)

### Core Technologies

- **Backend**: Python 3.12, Flask, pymodbus, scikit-learn, River
- **Frontend**: Vue 3, Vite, PrimeVue, Chart.js, Tailwind CSS 4
- **Database**: SQLite (config/alerts), VictoriaMetrics (time-series)
- **Deployment**: Docker (multi-stage builds), Docker Compose
- **CI/CD**: GitHub Actions (multi-arch builds: amd64, arm64, arm/v7)

---

## Architecture & Technology Stack

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
├─────────────────┬──────────────┬──────────────┬─────────────┤
│   idm-logger    │ victoriametr.│  ml-service  │ watchtower  │
│  (Main App)     │  (Time-Series│  (Anomaly    │ (Auto       │
│                 │   Database)  │  Detection)  │  Updates)   │
│  ┌───────────┐  │              │              │             │
│  │  Flask    │  │              │              │             │
│  │  Web API  │◄─┼──────────────┼──────────────┤             │
│  └─────┬─────┘  │              │              │             │
│        │        │              │              │             │
│  ┌─────▼─────┐  │              │              │             │
│  │  Modbus   │  │              │              │             │
│  │  Client   │◄─┼─Heat Pump    │              │             │
│  └───────────┘  │  (Navigator  │              │             │
│                 │   2.0)       │              │             │
│  ┌───────────┐  │              │              │             │
│  │ Scheduler │  │              │              │             │
│  │ & Alerts  │  │              │              │             │
│  └───────────┘  │              │              │             │
│                 │              │              │             │
│  ┌───────────┐  │              │              │             │
│  │   Vue 3   │  │              │              │             │
│  │ Dashboard │  │              │              │             │
│  │ (Static)  │  │              │              │             │
│  └───────────┘  │              │              │             │
└─────────────────┴──────────────┴──────────────┴─────────────┘
         │                │              │
         │                │              │
         ▼                ▼              ▼
    Port 5008       Port 8428      Internal Only
```

### Technology Stack Details

#### Backend (Python 3.12)

| Package | Version | Purpose |
|---------|---------|---------|
| **flask** | ≥3.1.2 | Web framework & REST API |
| **waitress** | ≥3.0.2 | Production WSGI server |
| **pymodbus** | ≥3.11.4 | Modbus TCP protocol |
| **scikit-learn** | ≥1.4.0 | ML preprocessing & models |
| **river** | 0.23.0 | Streaming ML (Hoeffding trees) |
| **paho-mqtt** | ≥2.1.0 | MQTT client for HA integration |
| **cryptography** | ≥46.0.3 | Fernet AES encryption |
| **flask-socketio** | ≥5.4.0 | WebSocket support |
| **schedule** | ≥1.2.2 | Job scheduling |
| **numpy** | ≥1.26.0 | Numerical operations |
| **pandas** | ≥2.0.0 | Data analysis |

#### Frontend (Vue 3)

| Package | Version | Purpose |
|---------|---------|---------|
| **vue** | ^3.5.27 | Progressive JS framework |
| **vite** | ^7.3.1 | Build tool & dev server |
| **vue-router** | ^4.6.4 | Client-side routing |
| **pinia** | ^3.0.4 | State management |
| **chart.js** | ^4.5.1 | Chart rendering |
| **vue-chartjs** | ^5.3.3 | Vue wrapper for Chart.js |
| **primevue** | ^4.5.4 | UI component library |
| **tailwindcss** | ^4.1.18 | Utility-first CSS |
| **socket.io-client** | ^4.8.1 | WebSocket client |
| **gridstack** | ^12.4.2 | Drag-drop dashboard layout |
| **vue-i18n** | ^11.2.8 | Internationalization |
| **axios** | ^1.13.2 | HTTP client |

#### Infrastructure

- **VictoriaMetrics**: Time-series database (1 year retention)
- **Docker Compose**: Multi-container orchestration
- **Watchtower**: Automatic container updates (daily 3:00 AM)
- **signal-cli**: Signal messaging support (v0.12.8)

---

## Directory Structure

```
idm-metrics-collector/
│
├── frontend/                          # Vue 3 application
│   ├── src/
│   │   ├── components/                # 43 Vue components
│   │   │   ├── ChartCard.vue         # Multi-series line charts
│   │   │   ├── GaugeCard.vue         # Tachometer panels
│   │   │   ├── StatCard.vue          # Large number displays
│   │   │   ├── DashboardManager.vue  # Dashboard CRUD
│   │   │   └── ...
│   │   ├── views/                     # 10 main pages
│   │   │   ├── Dashboard.vue         # Main monitoring (drag-drop, zoom)
│   │   │   ├── Control.vue           # Heat pump control
│   │   │   ├── Schedule.vue          # Weekly schedules
│   │   │   ├── Config.vue            # Configuration UI (64 KB)
│   │   │   ├── Alerts.vue            # Alert management
│   │   │   └── ...
│   │   ├── stores/                    # Pinia state
│   │   │   ├── auth.js               # Authentication state
│   │   │   ├── heatpumps.js          # Multi-heatpump data
│   │   │   └── ui.js                 # UI state
│   │   ├── router/                    # Vue Router config
│   │   ├── locales/                   # i18n (en.json, de.json)
│   │   ├── utils/                     # Helper functions
│   │   └── assets/                    # Static assets
│   ├── vite.config.js                 # Vite build config
│   └── package.json                   # Frontend deps
│
├── idm_logger/                        # Python backend (~12,579 LOC)
│   ├── __main__.py                    # CLI entry point
│   ├── logger.py                      # Main orchestration
│   ├── web.py                         # Flask API (300+ endpoints)
│   ├── modbus.py                      # Modbus TCP protocol
│   ├── config.py                      # Config mgmt (encrypted)
│   ├── db.py                          # SQLite interface
│   ├── alerts.py                      # Alert engine
│   ├── scheduler.py                   # Task scheduling
│   ├── metrics.py                     # VictoriaMetrics publisher
│   ├── dashboard_config.py            # Dashboard persistence
│   ├── templates.py                   # Pre-built dashboards
│   ├── sensor_addresses.py            # Modbus register mappings
│   ├── expressions_parser.py          # Math expression eval
│   ├── technician_auth.py             # Temporary access codes
│   ├── update_manager.py              # Self-updating
│   ├── model_updater.py               # ML model management
│   ├── migrations.py                  # Database migrations
│   ├── mqtt.py                        # MQTT publisher
│   ├── signal_notifications.py        # Signal protocol
│   ├── notifications/                 # 6 notification backends
│   │   ├── base.py                    # Base interface
│   │   ├── telegram.py                # Telegram bot
│   │   ├── discord.py                 # Discord webhooks
│   │   ├── email.py                   # SMTP email
│   │   ├── signal.py                  # Signal CLI
│   │   └── __init__.py
│   ├── manufacturers/                 # Hardware drivers
│   │   ├── idm/                       # IDM Navigator 2.0
│   │   ├── nibe/                      # Nibe S-Series
│   │   ├── luxtronik/                 # Alpha Innotec, Bosch, Roth
│   │   ├── daikin/                    # Daikin Altherma 3
│   │   └── base.py
│   ├── static/                        # Built frontend (auto-generated)
│   └── templates/                     # HTML email templates
│
├── ml_service/                        # ML anomaly detection
│   ├── main.py                        # ML service entry point
│   ├── Dockerfile                     # ML container
│   ├── requirements.txt               # ML deps
│   └── utils/
│
├── telemetry_server/                  # Telemetry aggregation
│   ├── app.py                         # Telemetry endpoint
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── tests/                             # Test suite (31 files)
│   ├── test_*.py                      # Unit tests
│   ├── verify_*.py                    # Integration tests
│   └── test_alerts/
│
├── docs/                              # Documentation
│   ├── MANUAL.md                      # User manual
│   ├── MQTT_SETUP.md
│   ├── SOLAR_INTEGRATION.md
│   ├── COMMUNITY_AI_CONCEPT.md
│   └── screenshots/
│
├── .github/workflows/                 # CI/CD
│   ├── ci.yml                         # Tests & linting
│   ├── docker-image.yml               # Multi-arch builds
│   ├── docker-ml-service.yml          # ML container
│   └── docker-arm64-manual.yml        # ARM64 builds
│
├── Dockerfile                         # Main app container
├── docker-compose.yml                 # Stack orchestration
├── requirements.txt                   # Python deps
├── pytest.ini                         # Pytest config
├── VERSION                            # Current version
├── README.md                          # Project documentation
├── FEATURES.md                        # Feature docs
└── CLAUDE.md                          # This file
```

---

## Development Workflows

### Local Development Setup

#### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **pnpm 9+**
- **Docker & Docker Compose**
- **Git**

#### Backend Development

```bash
# Clone repository
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector

# Install Python dependencies
pip install -r requirements.txt

# Run backend locally (development mode)
python -m idm_logger.logger

# The backend will start on http://localhost:5000
```

#### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Start dev server (hot-reload)
pnpm run dev
# Dev server: http://localhost:5173
# Proxies API calls to backend at localhost:5000

# Build for production
pnpm run build
# Output: ../idm_logger/static/

# Lint code
pnpm run lint

# Format code
pnpm run format
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_alerts.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=idm_logger

# Frontend linting
cd frontend
pnpm run lint
```

#### Docker Development

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f idm-logger

# Rebuild after code changes
docker compose up -d --build

# Stop services
docker compose down

# Remove volumes (fresh start)
docker compose down -v
```

---

## Key Conventions & Patterns

### Code Style

#### Python (Backend)

- **Formatter**: Ruff (configured in CI)
- **Linting**: Ruff lint
- **Line Length**: 120 characters
- **Imports**: Sorted, grouped (stdlib, third-party, local)
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

**Example:**

```python
# Good
def get_sensor_data(sensor_id: int) -> dict:
    """Fetch sensor data from Modbus."""
    return modbus_client.read_register(sensor_id)

# Bad
def GetSensorData(sensorID):
    return ModbusClient.ReadRegister(sensorID)
```

#### JavaScript/Vue (Frontend)

- **Formatter**: Prettier
- **Linting**: ESLint with Vue plugin
- **Line Length**: 100 characters
- **Naming**:
  - Components: `PascalCase` (ChartCard.vue)
  - Variables/functions: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Composition API**: Preferred over Options API
- **Script Setup**: Use `<script setup>` syntax

**Example:**

```vue
<!-- Good -->
<script setup>
import { ref, computed } from 'vue'

const sensorData = ref([])
const filteredData = computed(() => sensorData.value.filter(d => d.active))
</script>

<!-- Bad -->
<script>
export default {
  data() {
    return { sensor_data: [] }
  }
}
</script>
```

### File Organization

#### Backend Module Structure

```python
# Standard module structure
"""
Module docstring describing purpose.
"""

# Imports
import os
from typing import Optional

from flask import Flask
import pymodbus

from idm_logger.config import Config

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Classes
class ModbusClient:
    """Modbus TCP client for heat pumps."""

    def __init__(self, host: str, port: int = 502):
        self.host = host
        self.port = port

    def connect(self) -> bool:
        """Establish connection to heat pump."""
        pass

# Functions
def parse_register(data: bytes) -> int:
    """Parse Modbus register data."""
    pass
```

#### Frontend Component Structure

```vue
<template>
  <!-- Template markup -->
</template>

<script setup>
// Imports
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Props & Emits
const props = defineProps({
  sensorId: String,
  showControls: Boolean
})

const emit = defineEmits(['update', 'error'])

// Reactive state
const data = ref(null)

// Computed
const isValid = computed(() => data.value !== null)

// Methods
const fetchData = async () => {
  // Implementation
}

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* Component-specific styles */
</style>
```

### API Design Patterns

#### REST Endpoints

**Naming Convention:**
- Collection: `/api/sensors` (GET, POST)
- Resource: `/api/sensors/{id}` (GET, PUT, DELETE)
- Action: `/api/sensors/{id}/activate` (POST)

**Response Format:**

```python
# Success
{
    "success": True,
    "data": {...},
    "message": "Operation completed"
}

# Error
{
    "success": False,
    "error": "Error description",
    "details": {...}  # Optional
}
```

#### Error Handling

```python
# Backend
from flask import jsonify

@app.route('/api/sensor/<int:sensor_id>')
def get_sensor(sensor_id):
    try:
        sensor = db.get_sensor(sensor_id)
        if not sensor:
            return jsonify({
                'success': False,
                'error': 'Sensor not found'
            }), 404

        return jsonify({
            'success': True,
            'data': sensor
        })
    except Exception as e:
        logger.error(f"Error fetching sensor: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
```

```javascript
// Frontend
try {
  const response = await axios.get(`/api/sensor/${sensorId}`)
  if (response.data.success) {
    sensorData.value = response.data.data
  } else {
    console.error('Error:', response.data.error)
  }
} catch (error) {
  console.error('Request failed:', error)
}
```

---

## Testing Guidelines

### Test Organization

- **Location**: All tests in `tests/` directory
- **Naming**: `test_*.py` for test files
- **Structure**: One test file per module
- **Markers**: Use pytest markers for categorization

### Test Categories

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test module interactions
3. **End-to-End Tests**: Test full workflows (Playwright)

### Writing Tests

```python
# tests/test_modbus.py
import pytest
from idm_logger.modbus import ModbusClient

@pytest.fixture
def modbus_client():
    """Create test Modbus client."""
    return ModbusClient('192.168.1.100', 502)

def test_connect_success(modbus_client):
    """Test successful connection."""
    assert modbus_client.connect() is True

def test_read_register(modbus_client):
    """Test reading register."""
    modbus_client.connect()
    value = modbus_client.read_register(1000)
    assert isinstance(value, int)

@pytest.mark.parametrize("register,expected", [
    (1000, 0),
    (1001, 1),
    (1002, 2),
])
def test_multiple_registers(modbus_client, register, expected):
    """Test reading multiple registers."""
    modbus_client.connect()
    value = modbus_client.read_register(register)
    assert value == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_modbus.py

# Run tests matching pattern
pytest -k "modbus"

# Run with coverage
pytest --cov=idm_logger --cov-report=html

# Run in verbose mode
pytest -v

# Stop on first failure
pytest -x
```

---

## Docker & Deployment

### Multi-Stage Dockerfile

The main `Dockerfile` uses a two-stage build:

1. **Stage 1 (frontend-build)**: Build Vue frontend
   - Base: `node:22-slim`
   - Install pnpm, dependencies
   - Build frontend → `/app/idm_logger/static/`

2. **Stage 2 (runtime)**: Python application
   - Base: `python:3.12-slim`
   - Install system deps (build-essential, libssl-dev, JRE)
   - Install Python deps
   - Download signal-cli (v0.12.8)
   - Copy backend code + built frontend
   - Expose port 5000
   - Health check: `/api/health` endpoint

### Building Images

```bash
# Build locally
docker build -t idm-metrics-collector:local .

# Build with version
docker build --build-arg APP_VERSION=1.0.1 -t idm-metrics-collector:1.0.1 .

# Build for specific platform
docker buildx build --platform linux/amd64 -t idm-metrics-collector:amd64 .
docker buildx build --platform linux/arm64 -t idm-metrics-collector:arm64 .
```

### Docker Compose Services

```yaml
# idm-logger: Main application
- Port 5008 → 5000
- Volume: idm-data:/app/data
- Depends on: victoriametrics

# victoriametrics: Time-series DB
- Port 8428
- Volume: vm-data:/storage
- Retention: 1 year

# ml-service: Anomaly detection
- No exposed port (internal)
- Volume: ml-model-data:/app/data
- Depends on: victoriametrics, idm-logger

# watchtower: Auto-updates
- Schedule: Daily 3:00 AM
- Cleanup: Remove old images
- Scope: idm-updates label
```

### Environment Variables

**Required:**

```bash
IDM_HOST=192.168.178.103          # Heat pump IP
IDM_PORT=502                       # Modbus port
METRICS_URL=http://victoriametrics:8428/write
INTERNAL_API_KEY=change_me_secure_key
```

**Optional:**

```bash
MQTT_ENABLED=false
MQTT_BROKER=mqtt.example.com
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_USE_TLS=false
MQTT_TOPIC_PREFIX=idm/heatpump
```

### Data Persistence

**Volumes:**

- `idm-data`: SQLite database, config, logs
- `vm-data`: VictoriaMetrics time-series data
- `ml-model-data`: ML model state

**Backup:**

```bash
# Backup volumes
docker run --rm -v idm-logger-data:/data -v $(pwd):/backup ubuntu tar czf /backup/idm-backup.tar.gz /data

# Restore volumes
docker run --rm -v idm-logger-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/idm-backup.tar.gz -C /
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main`
- Pull requests to `main`

**Jobs:**

**backend-test:**
1. Checkout code
2. Setup Python 3.12
3. Install dependencies
4. Ruff lint & format check
5. Setup Node & pnpm
6. Build frontend
7. Run pytest

**frontend-check:**
1. Checkout code
2. Setup Node 20 & pnpm 9
3. Install dependencies
4. ESLint linting
5. Vite build

#### 2. Docker Image Build (`docker-image.yml`)

**Triggers:**
- Release tags
- Manual dispatch
- Push to `main`

**Multi-Platform Builds:**
- **Releases**: amd64, arm64, arm/v7
- **Main branch**: amd64 only

**Registries:**
- GitHub Container Registry (ghcr.io)
- Docker Hub

**Versioning:**
- Release: `v1.0.1` → `1.0.1`, `latest`
- Main: `1.0.1.abc1234` (version + short SHA)

#### 3. ML Service Build (`docker-ml-service.yml`)

Builds separate anomaly detection container with ML dependencies.

#### 4. ARM64 Manual Build (`docker-arm64-manual.yml`)

Manual workflow for ARM64-specific builds (Raspberry Pi).

### Release Process

1. Update `VERSION` file
2. Update `CHANGELOG.md`
3. Commit changes
4. Create git tag: `git tag v1.0.1`
5. Push tag: `git push origin v1.0.1`
6. GitHub Actions automatically builds and publishes multi-arch images
7. Watchtower updates running instances (next 3:00 AM)

---

## Important Files & Their Roles

### Backend Core Files

| File | Purpose | Lines of Code |
|------|---------|---------------|
| **logger.py** | Main entry point, orchestrates all services | ~500 |
| **web.py** | Flask API, 300+ endpoints, WebSocket server | ~2,500 |
| **modbus.py** | Modbus TCP protocol, register caching | ~800 |
| **config.py** | Config management with AES encryption | ~400 |
| **db.py** | SQLite interface for alerts, schedules, dashboards | ~600 |
| **alerts.py** | Alert engine (threshold, status, ML-based) | ~500 |
| **scheduler.py** | Cron-like task scheduling | ~300 |
| **metrics.py** | VictoriaMetrics publisher with downsampling | ~250 |
| **dashboard_config.py** | Dashboard persistence & templates | ~700 |

### Frontend Core Files

| File | Purpose | Components |
|------|---------|------------|
| **Dashboard.vue** | Main monitoring dashboard | Drag-drop, zoom, charts |
| **Control.vue** | Heat pump control interface | Mode, temp, actions |
| **Config.vue** | Configuration UI (64 KB) | All settings |
| **ChartCard.vue** | Multi-series line charts | Dual Y-axes, zoom |
| **GaugeCard.vue** | Tachometer panels | COP, efficiency |
| **StatCard.vue** | Large number displays | Trend, target |

### Configuration Files

| File | Purpose |
|------|---------|
| **docker-compose.yml** | Container orchestration |
| **Dockerfile** | Multi-stage app build |
| **vite.config.js** | Frontend build config |
| **requirements.txt** | Python dependencies |
| **frontend/package.json** | Frontend dependencies |
| **pytest.ini** | Test configuration |
| **VERSION** | Current version number |

---

## Common Tasks

### Adding a New API Endpoint

1. **Define route in `web.py`:**

```python
@app.route('/api/my-endpoint', methods=['GET', 'POST'])
@login_required
def my_endpoint():
    """My new endpoint."""
    try:
        data = request.get_json()
        # Process data
        result = process_data(data)

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Error in my_endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

2. **Add frontend integration:**

```javascript
// stores/myStore.js or component
import axios from 'axios'

export async function fetchMyData() {
  try {
    const response = await axios.get('/api/my-endpoint')
    if (response.data.success) {
      return response.data.data
    }
  } catch (error) {
    console.error('Error fetching data:', error)
    throw error
  }
}
```

3. **Add tests:**

```python
# tests/test_my_endpoint.py
def test_my_endpoint(client):
    """Test my new endpoint."""
    response = client.get('/api/my-endpoint')
    assert response.status_code == 200
    assert response.json['success'] is True
```

### Adding a New Vue Component

1. **Create component file:**

```bash
touch frontend/src/components/MyNewComponent.vue
```

2. **Component structure:**

```vue
<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
  </div>
</template>

<script setup>
import { ref, defineProps } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: String
})
</script>

<style scoped>
.my-component {
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 0.5rem;
}
</style>
```

3. **Use in parent:**

```vue
<template>
  <MyNewComponent
    title="Example"
    description="This is my new component"
  />
</template>

<script setup>
import MyNewComponent from '@/components/MyNewComponent.vue'
</script>
```

### Adding a New Sensor/Register

1. **Update `sensor_addresses.py`:**

```python
SENSORS = {
    'my_new_sensor': {
        'address': 3000,
        'type': 'int16',
        'unit': '°C',
        'description': 'My new temperature sensor',
        'category': 'temperature'
    }
}
```

2. **Add to Modbus polling in `modbus.py`:**

```python
def read_all_sensors(self):
    """Read all sensor values."""
    values = {}
    for sensor_name, config in SENSORS.items():
        try:
            value = self.read_register(config['address'])
            values[sensor_name] = value
        except Exception as e:
            logger.error(f"Error reading {sensor_name}: {e}")
    return values
```

3. **Publish to metrics:**

```python
# metrics.py
def publish_sensor_data(sensor_data):
    """Publish sensor data to VictoriaMetrics."""
    metrics = []
    for sensor_name, value in sensor_data.items():
        metrics.append({
            'metric': f'idm_heatpump_{sensor_name}',
            'value': value,
            'timestamp': int(time.time())
        })
    send_to_vm(metrics)
```

### Running Database Migrations

1. **Create migration in `migrations.py`:**

```python
def migrate_v1_0_1():
    """Migration for v1.0.1."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        ALTER TABLE alerts
        ADD COLUMN priority TEXT DEFAULT 'medium'
    """)

    conn.commit()
    conn.close()
```

2. **Register migration:**

```python
MIGRATIONS = {
    '1.0.1': migrate_v1_0_1
}
```

3. **Run automatically on startup** (handled in `logger.py`)

### Creating a Dashboard Template

1. **Add to `templates.py`:**

```python
DASHBOARD_TEMPLATES = {
    'my_template': {
        'name': 'My Custom Dashboard',
        'description': 'Custom monitoring dashboard',
        'panels': [
            {
                'type': 'chart',
                'title': 'Temperature Overview',
                'queries': [
                    {'label': 'Outside', 'query': 'idm_heatpump_temp_outside'},
                    {'label': 'Flow', 'query': 'idm_heatpump_temp_flow'}
                ],
                'gridPos': {'x': 0, 'y': 0, 'w': 6, 'h': 4}
            }
        ]
    }
}
```

2. **Use in frontend:**

```javascript
// Dashboard.vue
const loadTemplate = async (templateId) => {
  const response = await axios.get(`/api/dashboard/templates/${templateId}`)
  if (response.data.success) {
    dashboard.value = response.data.data
  }
}
```

---

## Security Considerations

### Authentication & Authorization

- **Password hashing**: Werkzeug PBKDF2 (min 6 characters)
- **Session management**: HTTPOnly, SameSite=Lax cookies
- **Login required**: `@login_required` decorator on protected routes
- **Technician codes**: Time-limited (6 hours) temporary access

### Data Encryption

- **Config encryption**: Fernet (AES-128) for sensitive settings
- **HTTPS**: Recommended for production deployments
- **Secrets**: Never commit to version control

### Input Validation

```python
# web.py
def validate_ip_address(ip):
    """Validate IP address format."""
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        raise ValueError('Invalid IP address')

    parts = ip.split('.')
    if any(int(part) > 255 for part in parts):
        raise ValueError('Invalid IP address')

    return ip

@app.route('/api/config/modbus', methods=['POST'])
@login_required
def update_modbus_config():
    """Update Modbus configuration."""
    data = request.get_json()

    # Validate inputs
    ip = validate_ip_address(data.get('host'))
    port = int(data.get('port', 502))

    if not 1 <= port <= 65535:
        return jsonify({'success': False, 'error': 'Invalid port'}), 400

    # Update config
    config.set('modbus_host', ip)
    config.set('modbus_port', port)

    return jsonify({'success': True})
```

### Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    default_limits=["200 per minute"]
)

@app.route('/api/sensitive-endpoint')
@limiter.limit("10 per minute")
def sensitive_endpoint():
    """Rate-limited endpoint."""
    pass
```

### Security Headers

```python
@app.after_request
def set_security_headers(response):
    """Set security headers."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### Network Security

- **IP Whitelist/Blacklist**: Configurable in UI
- **Firewall**: Docker network isolation
- **MQTT TLS**: Optional TLS for MQTT connections

---

## Frontend Guidelines

### Vue 3 Composition API

**Preferred Pattern:**

```vue
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store access
const authStore = useAuthStore()
const router = useRouter()

// Props
const props = defineProps({
  sensorId: {
    type: String,
    required: true
  }
})

// Reactive state
const data = ref(null)
const loading = ref(false)

// Computed properties
const isValid = computed(() => data.value !== null)

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/sensor/${props.sensorId}`)
    data.value = response.data.data
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

// Watchers
watch(() => props.sensorId, () => {
  fetchData()
})

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>
```

### State Management (Pinia)

```javascript
// stores/sensors.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useSensorsStore = defineStore('sensors', () => {
  // State
  const sensors = ref([])
  const loading = ref(false)

  // Getters
  const activeSensors = computed(() =>
    sensors.value.filter(s => s.active)
  )

  // Actions
  async function fetchSensors() {
    loading.value = true
    try {
      const response = await axios.get('/api/sensors')
      sensors.value = response.data.data
    } catch (error) {
      console.error('Error fetching sensors:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    sensors,
    loading,
    activeSensors,
    fetchSensors
  }
})
```

### Component Communication

**Props Down, Events Up:**

```vue
<!-- Parent.vue -->
<template>
  <ChildComponent
    :data="parentData"
    @update="handleUpdate"
  />
</template>

<script setup>
import { ref } from 'vue'

const parentData = ref({ value: 42 })

const handleUpdate = (newValue) => {
  parentData.value = newValue
}
</script>

<!-- ChildComponent.vue -->
<template>
  <button @click="emitUpdate">Update</button>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  data: Object
})

const emit = defineEmits(['update'])

const emitUpdate = () => {
  emit('update', { value: props.data.value + 1 })
}
</script>
```

### Styling with Tailwind CSS 4

```vue
<template>
  <div class="p-4 bg-surface-card rounded-lg shadow-md">
    <h2 class="text-xl font-bold text-surface-900 dark:text-surface-50">
      Title
    </h2>
    <p class="mt-2 text-surface-600 dark:text-surface-400">
      Description
    </p>
  </div>
</template>

<style scoped>
/* Use CSS variables for theming */
.custom-class {
  background: var(--surface-card);
  color: var(--text-color);
}
</style>
```

### Internationalization (i18n)

```vue
<template>
  <div>
    <h1>{{ $t('dashboard.title') }}</h1>
    <p>{{ $t('dashboard.description', { count: 42 }) }}</p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

// Change language
const switchLanguage = () => {
  locale.value = locale.value === 'en' ? 'de' : 'en'
}
</script>
```

```json
// locales/en.json
{
  "dashboard": {
    "title": "Dashboard",
    "description": "You have {count} active sensors"
  }
}

// locales/de.json
{
  "dashboard": {
    "title": "Dashboard",
    "description": "Sie haben {count} aktive Sensoren"
  }
}
```

---

## Backend Guidelines

### Flask Patterns

#### Blueprint Organization

```python
# web.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/sensors')
def get_sensors():
    """Get all sensors."""
    pass

# Register blueprint
app.register_blueprint(api_bp)
```

#### Request Validation

```python
from flask import request, jsonify
from functools import wraps

def validate_json(*expected_args):
    """Decorator to validate JSON request data."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                }), 400

            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({
                    'success': False,
                    'error': f'Missing fields: {", ".join(missing)}'
                }), 400

            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/sensor', methods=['POST'])
@validate_json('name', 'address', 'type')
def create_sensor():
    """Create new sensor."""
    data = request.get_json()
    # Process validated data
    pass
```

#### Database Access

```python
# db.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Get database connection context manager."""
    conn = sqlite3.connect('data/idm.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensors")
    sensors = cursor.fetchall()
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Usage
logger.info("Starting sensor polling")
logger.warning("High temperature detected: %.1f°C", temp)
logger.error("Failed to connect to heat pump: %s", error)
```

### Modbus Protocol

```python
from pymodbus.client import ModbusTcpClient

class ModbusClient:
    """Modbus TCP client for heat pumps."""

    def __init__(self, host: str, port: int = 502):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host, port=port)
        self.connected = False

    def connect(self) -> bool:
        """Connect to heat pump."""
        try:
            self.connected = self.client.connect()
            return self.connected
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def read_register(self, address: int) -> int:
        """Read single register."""
        if not self.connected:
            self.connect()

        try:
            result = self.client.read_holding_registers(address, 1)
            if result.isError():
                raise Exception(f"Modbus error: {result}")
            return result.registers[0]
        except Exception as e:
            logger.error(f"Read error: {e}")
            raise

    def write_register(self, address: int, value: int) -> bool:
        """Write single register."""
        if not self.connected:
            self.connect()

        try:
            result = self.client.write_register(address, value)
            return not result.isError()
        except Exception as e:
            logger.error(f"Write error: {e}")
            return False
```

### Async Operations

```python
import asyncio
from typing import List

async def fetch_sensor_data(sensor_id: int) -> dict:
    """Fetch sensor data asynchronously."""
    await asyncio.sleep(0.1)  # Simulate I/O
    return {'id': sensor_id, 'value': 42}

async def fetch_all_sensors(sensor_ids: List[int]) -> List[dict]:
    """Fetch multiple sensors concurrently."""
    tasks = [fetch_sensor_data(sid) for sid in sensor_ids]
    return await asyncio.gather(*tasks)

# Usage
sensor_data = asyncio.run(fetch_all_sensors([1, 2, 3, 4, 5]))
```

---

## Integration Points

### VictoriaMetrics

**Write Data:**

```python
import requests
import time

def publish_metrics(metrics: list):
    """Publish metrics to VictoriaMetrics."""
    url = 'http://victoriametrics:8428/write'

    lines = []
    for metric in metrics:
        name = metric['metric']
        value = metric['value']
        timestamp = metric.get('timestamp', int(time.time()))
        tags = ','.join(f"{k}={v}" for k, v in metric.get('tags', {}).items())

        line = f"{name}"
        if tags:
            line += f",{tags}"
        line += f" {value} {timestamp}000000000"  # Nanoseconds
        lines.append(line)

    data = '\n'.join(lines)

    response = requests.post(url, data=data)
    response.raise_for_status()
```

**Query Data:**

```python
def query_metrics(query: str, start: int, end: int) -> list:
    """Query metrics from VictoriaMetrics."""
    url = 'http://victoriametrics:8428/api/v1/query_range'

    params = {
        'query': query,
        'start': start,
        'end': end,
        'step': '60s'
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data['data']['result']
```

### MQTT (Home Assistant)

```python
import paho.mqtt.client as mqtt

class MQTTPublisher:
    """MQTT publisher for Home Assistant integration."""

    def __init__(self, broker: str, port: int = 1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.connected = False

    def connect(self, username: str = None, password: str = None):
        """Connect to MQTT broker."""
        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        """Connection callback."""
        self.connected = rc == 0
        logger.info(f"MQTT connected: {self.connected}")

    def publish_sensor(self, sensor_name: str, value: float, unit: str):
        """Publish sensor value."""
        topic = f"idm/heatpump/{sensor_name}"
        payload = {
            'value': value,
            'unit': unit,
            'timestamp': time.time()
        }

        self.client.publish(topic, json.dumps(payload), retain=True)
```

### ML Service Communication

**Alert Notification:**

```python
def send_ml_alert(alert_data: dict):
    """Send ML-detected anomaly alert to main app."""
    url = 'http://idm-logger:5000/api/alerts/ml'
    headers = {'X-API-Key': os.getenv('INTERNAL_API_KEY')}

    response = requests.post(url, json=alert_data, headers=headers)
    response.raise_for_status()
```

**Model Status:**

```python
def get_ml_status() -> dict:
    """Get ML service status."""
    url = 'http://ml-service:8080/status'

    response = requests.get(url, timeout=5)
    return response.json()
```

### WebSocket Communication

**Backend (Flask-SocketIO):**

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to sensor updates."""
    sensor_id = data.get('sensor_id')
    emit('subscribed', {'sensor_id': sensor_id})

def broadcast_sensor_update(sensor_id: int, value: float):
    """Broadcast sensor update to all clients."""
    socketio.emit('sensor_update', {
        'sensor_id': sensor_id,
        'value': value,
        'timestamp': time.time()
    })
```

**Frontend (socket.io-client):**

```javascript
import { io } from 'socket.io-client'

const socket = io('http://localhost:5008')

socket.on('connect', () => {
  console.log('Connected to WebSocket')
  socket.emit('subscribe', { sensor_id: 1 })
})

socket.on('sensor_update', (data) => {
  console.log('Sensor update:', data)
  updateSensorValue(data.sensor_id, data.value)
})

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket')
})
```

---

## Gotchas & Special Considerations

### EEPROM Write Protection

**Problem**: Excessive writes to heat pump EEPROM can cause hardware failure.

**Solution**: Implement write cooldown and warnings.

```python
class ModbusClient:
    def __init__(self):
        self.last_write = {}
        self.write_cooldown = 300  # 5 minutes

    def write_register(self, address: int, value: int) -> bool:
        """Write with cooldown protection."""
        now = time.time()
        last = self.last_write.get(address, 0)

        if now - last < self.write_cooldown:
            raise Exception(
                f"Write cooldown active. "
                f"Wait {self.write_cooldown - (now - last):.0f}s"
            )

        result = self.client.write_register(address, value)
        if not result.isError():
            self.last_write[address] = now

        return not result.isError()
```

### Frontend Build Output

**Important**: Vite builds to `../idm_logger/static/`, not `dist/`.

```javascript
// vite.config.js
export default defineConfig({
  base: '/static/',
  build: {
    outDir: '../idm_logger/static',
    emptyOutDir: true
  }
})
```

### Docker Volume Permissions

**Problem**: Permission errors when accessing mounted volumes.

**Solution**: Ensure proper ownership in Dockerfile.

```dockerfile
# Create data directory with correct permissions
RUN mkdir -p /app/data && chown -R nobody:nogroup /app/data
USER nobody
```

### Multi-Heatpump Session Management

**Consideration**: When managing multiple heat pumps, maintain separate Modbus connections and session states.

```python
class HeatPumpManager:
    """Manage multiple heat pump connections."""

    def __init__(self):
        self.clients = {}

    def add_heatpump(self, hp_id: str, host: str, port: int):
        """Add heat pump connection."""
        self.clients[hp_id] = ModbusClient(host, port)
        self.clients[hp_id].connect()

    def read_sensor(self, hp_id: str, address: int) -> int:
        """Read sensor from specific heat pump."""
        if hp_id not in self.clients:
            raise ValueError(f"Heat pump {hp_id} not found")

        return self.clients[hp_id].read_register(address)
```

### VictoriaMetrics Retention

**Default**: 1 year retention in docker-compose.yml.

```yaml
victoriametrics:
  command:
    - "-retentionPeriod=1y"  # Change as needed
```

**Disk Space**: Monitor disk usage, especially for high-frequency polling.

### Signal CLI Setup

**Requirement**: Signal CLI requires phone number registration.

```bash
# Register Signal account (run in container)
docker exec -it idm-logger signal-cli -u +491234567890 register
docker exec -it idm-logger signal-cli -u +491234567890 verify CODE
```

### Chart.js Memory Leaks

**Problem**: Chart.js instances can leak memory if not properly destroyed.

**Solution**: Destroy charts before component unmount.

```vue
<script setup>
import { ref, onBeforeUnmount } from 'vue'

const chartInstance = ref(null)

onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
})
</script>
```

### Time Zone Handling

**Backend**: All timestamps in UTC.

```python
import datetime

now_utc = datetime.datetime.utcnow()
timestamp = int(now_utc.timestamp())
```

**Frontend**: Convert to local time for display.

```javascript
import { format } from 'date-fns'

const localTime = new Date(timestamp * 1000)
const formatted = format(localTime, 'yyyy-MM-dd HH:mm:ss')
```

### ML Model Training

**Consideration**: ML models require sufficient data before making predictions.

```python
# ml_service/main.py
MIN_DATA_POINTS = 100

if len(training_data) < MIN_DATA_POINTS:
    logger.info(f"Insufficient data: {len(training_data)}/{MIN_DATA_POINTS}")
    return None  # Skip prediction
```

### Modbus Register Caching

**Optimization**: Cache frequently read registers to reduce Modbus traffic.

```python
class CachedModbusClient:
    """Modbus client with register caching."""

    def __init__(self, cache_ttl: int = 60):
        self.cache = {}
        self.cache_ttl = cache_ttl

    def read_register(self, address: int) -> int:
        """Read register with caching."""
        now = time.time()

        if address in self.cache:
            value, timestamp = self.cache[address]
            if now - timestamp < self.cache_ttl:
                return value

        value = self.client.read_holding_registers(address, 1).registers[0]
        self.cache[address] = (value, now)
        return value
```

---

## Best Practices for AI Assistants

### When Modifying Code

1. **Always read files before editing**: Use Read tool to understand current implementation
2. **Maintain existing patterns**: Follow established code style and conventions
3. **Test changes**: Run pytest after backend changes, pnpm run build after frontend changes
4. **Update documentation**: Modify relevant .md files if adding features
5. **Consider security**: Validate inputs, avoid SQL injection, protect sensitive data

### When Adding Features

1. **Check existing implementations**: Similar features may already exist
2. **Follow architecture**: Backend logic in Python, UI logic in Vue
3. **Add tests**: Create test cases in `tests/` directory
4. **Update types**: Ensure type hints for Python, proper TypeScript usage
5. **Document**: Add docstrings, comments for complex logic

### When Debugging

1. **Check logs**: Application logs are in `idm_logger/log_handler.py`
2. **Review Docker logs**: `docker compose logs -f idm-logger`
3. **Test locally**: Run outside Docker for faster iteration
4. **Use debugger**: pdb for Python, Vue DevTools for frontend
5. **Validate data**: Check Modbus registers, database contents, API responses

### When Reviewing Code

1. **Security**: Check for injection vulnerabilities, exposed secrets
2. **Performance**: Avoid N+1 queries, excessive API calls
3. **Error handling**: Ensure proper try/catch, user-friendly messages
4. **Code quality**: Follow linting rules, maintain readability
5. **Testing**: Verify test coverage for new code

---

## Additional Resources

### Internal Documentation

- **User Manual**: `docs/MANUAL.md`
- **MQTT Setup**: `docs/MQTT_SETUP.md`
- **Solar Integration**: `docs/SOLAR_INTEGRATION.md`
- **Multi-Heatpump**: `docs/MULTI_HEATPUMP_IMPLEMENTATION.md`
- **Features**: `FEATURES.md`
- **Changelog**: `CHANGELOG.md`

### External Links

- **GitHub Repository**: https://github.com/Xerolux/idm-metrics-collector
- **Docker Hub**: https://hub.docker.com/r/xerolux/idm-metrics-collector
- **Issue Tracker**: https://github.com/Xerolux/idm-metrics-collector/issues

### Key Libraries Documentation

- **Flask**: https://flask.palletsprojects.com/
- **Vue 3**: https://vuejs.org/guide/
- **pymodbus**: https://pymodbus.readthedocs.io/
- **VictoriaMetrics**: https://docs.victoriametrics.com/
- **Chart.js**: https://www.chartjs.org/docs/
- **PrimeVue**: https://primevue.org/
- **Pinia**: https://pinia.vuejs.org/

---

## Quick Reference Commands

```bash
# Development
pnpm run dev                    # Start frontend dev server
python -m idm_logger.logger     # Run backend
pytest -v                       # Run tests with verbose output

# Docker
docker compose up -d            # Start all services
docker compose down             # Stop all services
docker compose logs -f          # Follow logs
docker compose restart          # Restart services

# Build
pnpm run build                  # Build frontend
docker build -t idm:local .     # Build Docker image

# Testing
pytest                          # Run all tests
pytest -k "modbus"             # Run tests matching pattern
pytest --cov                    # Run with coverage

# Linting
ruff check .                    # Lint Python code
ruff format .                   # Format Python code
cd frontend && pnpm run lint    # Lint frontend

# Git
git status                      # Check status
git add .                       # Stage changes
git commit -m "message"         # Commit
git push origin main            # Push to remote

# Version management
cat VERSION                     # Check current version
echo "1.0.2" > VERSION         # Update version
```

---

## Version History

- **1.0.1** (2026-01-27): Initial CLAUDE.md creation
  - Comprehensive documentation for AI assistants
  - Architecture overview and guidelines
  - Development workflows and best practices

---

**For questions or updates to this document, please create an issue or pull request on GitHub.**
