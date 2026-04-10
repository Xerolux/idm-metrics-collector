# CLAUDE.md — IDM Metrics Collector

This file provides AI assistant guidance for the IDM Metrics Collector codebase.

---

## Project Overview

**IDM Metrics Collector** is a full-stack IoT platform for monitoring and controlling IDM Navigator 2.0 heat pumps. It combines:

- Python/Flask backend for Modbus TCP communication, metrics, and control
- Vue 3 + Vite SPA for dashboards and configuration
- PyTorch-based ML service for anomaly detection
- VictoriaMetrics for time-series storage
- MQTT publishing, multi-channel notifications, WebSocket streaming

**Version:** 1.0.6
**Primary Language:** Python (backend) + JavaScript/Vue (frontend)
**No TypeScript** — pure JS throughout the frontend.

---

## Repository Structure

```
idm-metrics-collector/
├── idm_logger/           # Main Python backend (Flask)
│   ├── __main__.py       # Module entry point
│   ├── logger.py         # Main orchestrator (polling loop)
│   ├── web.py            # Flask app, REST API, WebSocket server
│   ├── modbus.py         # Modbus TCP client
│   ├── metrics.py        # VictoriaMetrics writer
│   ├── mqtt.py           # MQTT publisher
│   ├── scheduler.py      # Weekly schedule management
│   ├── alerts.py         # Alert logic and triggering
│   ├── config.py         # Configuration (YAML + SQLite)
│   ├── db.py             # SQLite ORM
│   ├── notifications/    # Email, Discord, Telegram, Signal
│   ├── websocket_handler.py
│   ├── backup.py
│   ├── update_manager.py
│   ├── telemetry.py
│   ├── technician_auth.py
│   └── static/           # Built frontend assets (Vite output)
├── frontend/             # Vue 3 + Vite SPA
│   ├── src/
│   │   ├── main.js       # Vue app entry
│   │   ├── App.vue
│   │   ├── router/       # Vue Router
│   │   ├── stores/       # Pinia (auth.js, ui.js)
│   │   ├── views/        # 9 pages (Dashboard, Control, Schedule, etc.)
│   │   ├── components/   # 40+ reusable components
│   │   ├── utils/        # api.js, websocket.js, chartConfig.js, etc.
│   │   └── locales/      # i18n: en.json, de.json
│   ├── vite.config.js    # Builds → ../idm_logger/static/
│   ├── eslint.config.js  # ESLint 9 flat config
│   └── package.json
├── ml_service/           # PyTorch anomaly detection (FastAPI/Flask)
│   ├── main.py           # HTTP server + ML polling loop
│   ├── models.py         # Autoencoder model
│   ├── service.py        # Data collection & scoring
│   └── config.py
├── telemetry_server/     # Central telemetry aggregation (FastAPI)
│   ├── app.py
│   ├── tests/
│   └── requirements.txt
├── tests/                # All backend tests (pytest)
├── grafana/              # Grafana dashboard provisioning
├── docs/                 # Documentation, architecture, modbus registers
├── scripts/              # Utility scripts (bump_version.py, etc.)
├── docker-compose.yml    # 4 services: idm-logger, victoriametrics, ml-service, grafana
├── Dockerfile            # 2-stage: Node build → Python runtime
├── requirements.txt      # Python dependencies
├── pytest.ini
├── config.yaml.example
└── VERSION               # Current version string
```

---

## Development Workflows

### Python Backend

**Run locally:**
```bash
python -m idm_logger.logger
```

**Linting (Ruff — required by CI):**
```bash
ruff check .
ruff format .
```

**Tests:**
```bash
pytest
# or for a specific file:
pytest tests/test_webserver.py -v
```

All linting and tests must pass before merging. The CI runs `ruff check`, `ruff format`, and `pytest` automatically.

### Frontend

**Install dependencies (uses pnpm):**
```bash
cd frontend
pnpm install
```

**Development server:**
```bash
pnpm dev
```

**Build (outputs to `../idm_logger/static/`):**
```bash
pnpm build
```

**Lint:**
```bash
pnpm lint
```

### Full Stack (Docker Compose)

```bash
docker compose up -d
```

Services:
- `idm-logger` → port 5008 (maps to 5000 inside)
- `victoriametrics` → port 8428
- `ml-service` → port 8080 (internal only)
- `grafana` → port 3001 (commented out by default)

### Docker Build

Multi-arch (amd64, arm64, arm/v7):
```bash
./scripts/build_docker.sh
```

Or directly:
```bash
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 .
```

---

## CI/CD

All workflows are in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push/PR to main | Lint (Ruff + ESLint) + pytest + Vite build |
| `release.yml` | `v*` tags, manual | Multi-arch Docker build (main + ML + telemetry) → GHCR + Docker Hub |
| `wiki-sync.yml` | push to main | Sync docs/ to GitHub Wiki |

**Before pushing:** always run `ruff check .` and `pytest` locally to avoid CI failures.

---

## Key Conventions

### Python Backend

- **Python 3.12** minimum.
- **Ruff** is the linter/formatter (not flake8, not black). Configuration inherits from `pyproject.toml` or ruff defaults.
- **No type hints required** — the codebase is dynamically typed.
- **Flask patterns:** REST endpoints in `web.py`, WebSocket events in `websocket_handler.py`.
- **Database:** SQLite via `db.py`. Add new tables/columns there. No ORM framework — raw SQL with `sqlite3`.
- **Configuration:** All config flows through `config.py`. Reads from `config.yaml` + environment variables + SQLite for persistent user settings.
- **Modbus:** Address mappings are in `sensor_addresses.py` and `const.py`. Circuits are labeled A–G.
- **Retry logic:** Use the helpers in `retry_utils.py` for network calls.
- **Logging:** Use Python's `logging` module. Logs are buffered in memory by `log_handler.py` for the web log viewer.
- **Notifications:** Add new channels by subclassing `notifications/base.py`.
- **Security:** Sensitive values (passwords, API keys) must be encrypted using the `cryptography` (Fernet) utilities. Never log secrets.

### Frontend (Vue 3)

- **No TypeScript** — pure JavaScript with Vue 3 Composition API.
- **Always use `<script setup>` syntax** for new components.
- **Pinia** for state (`stores/auth.js`, `stores/ui.js`). Do not use Vuex.
- **API calls** go through `utils/api.js` (Axios client with auth interceptors). Never call `fetch` directly.
- **WebSocket** via `utils/websocket.js` (Socket.io client wrapper).
- **i18n:** All user-visible strings must be translated. Add keys to both `locales/en.json` and `locales/de.json`. Use `$t('key')` in templates.
- **PrimeVue** for UI components (Aura theme preset). Tailwind CSS for layout.
- **Chart.js** for all charts — reuse the config patterns from `utils/chartConfig.js`.
- **ESLint 9 flat config** (`eslint.config.js`) — run `pnpm lint` to check. `no-unused-vars` is a warning, not error.
- **Multi-word component names** rule is disabled — single-word component names are acceptable.
- **Build output:** The Vite build writes to `../idm_logger/static/`. Do not manually modify files there; always rebuild.

### ML Service

- **PyTorch** autoencoder for anomaly detection.
- Configure via environment variables (see `docker-compose.yml` for full list).
- Model state persists to `/app/data/` volume.
- Key env vars: `ANOMALY_THRESHOLD`, `ALARM_CONSECUTIVE_HITS`, `WARMUP_UPDATES`, `AE_HIDDEN_DIM`, `AE_LATENT_DIM`.

### Testing

- **pytest** for all Python tests (`tests/` directory).
- Test files named `test_*.py`, test functions `test_*`.
- Integration tests that need a live Modbus device are in `manual_test_*.py` — these are not run in CI.
- No frontend test runner is configured — frontend is validated by build + lint only.
- Telemetry server has its own tests in `telemetry_server/tests/`.

---

## Architecture Notes

### Data Flow

```
IDM Heat Pump (Modbus TCP)
    └─► modbus.py (polling every 60s)
        ├─► metrics.py → VictoriaMetrics (time-series)
        ├─► mqtt.py → MQTT broker
        ├─► websocket_handler.py → Browser (real-time)
        └─► alerts.py → notifications/ (email/discord/telegram/signal)

ml_service/
    └─► polls VictoriaMetrics
        └─► detects anomalies → alerts back to idm-logger API
```

### Flask App (`web.py`)

- Serves Vue SPA from `idm_logger/static/` for all non-API routes.
- REST API under `/api/*` with Flasgger/Swagger docs at `/apidocs`.
- Rate limiting on sensitive endpoints via Flask-Limiter.
- WebSocket via Flask-SocketIO (shared WSGI app with waitress).
- ProxyFix middleware enabled — deploy behind a reverse proxy (nginx, Traefik).

### Configuration System

1. `config.yaml` (file) — base configuration
2. Environment variables — override specific values (useful in Docker)
3. SQLite (`db.py`) — persistent user preferences changed via UI

The `config.py` module merges these in priority order.

### Versioning

- Version in `VERSION` file (e.g., `1.0.6`).
- Use `scripts/bump_version.py` to bump versions.
- Docker images tagged with semver on release (triggered by `v*` tags).

---

## Environment Variables (Docker)

Key variables for `idm-logger` service:

| Variable | Description |
|----------|-------------|
| `IDM_HOST` | Heat pump IP address |
| `IDM_PORT` | Modbus TCP port (default: 502) |
| `METRICS_URL` | VictoriaMetrics URL |
| `INTERNAL_API_KEY` | Shared secret for ML service ↔ idm-logger communication |
| `MQTT_HOST` | MQTT broker hostname |
| `MQTT_PORT` | MQTT broker port |
| `MQTT_USER` / `MQTT_PASSWORD` | MQTT credentials |

---

## Common Tasks

### Add a new Modbus sensor

1. Add register address to `idm_logger/sensor_addresses.py`
2. Add constant to `idm_logger/const.py` if needed
3. Add frontend translation key to `frontend/src/locales/en.json` and `de.json`
4. Add chart component or widget to appropriate view in `frontend/src/views/`

### Add a new notification channel

1. Create `idm_logger/notifications/<channel>.py` subclassing `base.py`
2. Register in `idm_logger/notifications/__init__.py`
3. Add config fields to `config.yaml.example`
4. Add UI config in `frontend/src/views/Config.vue`

### Add a new API endpoint

1. Add route to `idm_logger/web.py`
2. Document with Flasgger docstring (`@swag_from` or inline YAML)
3. Add to `frontend/src/utils/api.js` if called from frontend
4. Write test in `tests/test_webserver.py`

### Add a new frontend view

1. Create `frontend/src/views/NewView.vue` using `<script setup>`
2. Register route in `frontend/src/router/index.js`
3. Add navigation link to `frontend/src/components/Layout.vue`
4. Add i18n keys to both locale files

---

## Security Considerations

- Never commit secrets, API keys, or passwords to the repository.
- Sensitive config values are encrypted with Fernet (`cryptography` library).
- The `INTERNAL_API_KEY` must be set in production — it authenticates ML service → backend calls.
- Rate limiting is applied to login and sensitive write endpoints.
- Technician mode uses time-based codes for elevated access (`technician_auth.py`).
- All user-supplied HTML/CSS is sanitized via DOMPurify before rendering.
- The app is designed to run behind a reverse proxy with HTTPS termination.

---

## Known Patterns to Follow

- **Exponential backoff:** Use `retry_utils.py` helpers for all network/Modbus retries.
- **Batch writes:** Metrics are batched before writing to VictoriaMetrics (`batch_processor.py`).
- **Graceful shutdown:** `logger.py` handles SIGINT/SIGTERM — new background threads should register cleanup handlers.
- **Error boundaries:** Wrap Modbus reads in try/except; log errors but don't crash the polling loop.
- **i18n first:** Every new UI string needs translations in both `en.json` and `de.json`.
- **Component naming:** Vue components in `PascalCase.vue`, utility functions in `camelCase`.
