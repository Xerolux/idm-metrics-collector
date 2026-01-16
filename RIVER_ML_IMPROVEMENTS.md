# River ML Integration - Verbesserungsvorschläge

## Priorität 1: Kritische Verbesserungen

### 1.1 Konfigurierbare Parameter
**Datei**: `ml_service/main.py`

Folgende Parameter als Environment Variables:
- `ANOMALY_THRESHOLD` (default: 0.7)
- `MIN_DATA_RATIO` (default: 0.5)
- `MODEL_N_TREES` (default: 25)
- `MODEL_HEIGHT` (default: 15)
- `MODEL_WINDOW_SIZE` (default: 250)

### 1.2 Model Persistence
**Problem**: Bei Container-Restart geht gelernter Zustand verloren

**Lösung**:
```python
import pickle
import os

MODEL_PATH = "/app/data/model_state.pkl"

def save_model_state():
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

def load_model_state():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None
```

Volume im docker-compose:
```yaml
ml-service:
  volumes:
    - ml-model-data:/app/data
```

### 1.3 Circuit & Zone Configuration
**Aktuell**: Nur Circuit A hardcoded
**Sollte**: Aus config.yaml lesen oder ENV variable

```python
CIRCUITS = os.environ.get("ML_CIRCUITS", "A").split(",")
ZONES = [int(z) for z in os.environ.get("ML_ZONES", "").split(",") if z]
```

## Priorität 2: Funktionale Erweiterungen

### 2.1 Grafana Dashboard Integration
**Neues Panel** im idm-heatpump.json:

```json
{
  "title": "AI Anomalie Erkennung",
  "targets": [
    {
      "expr": "idm_anomaly_score",
      "legendFormat": "Anomalie Score"
    },
    {
      "expr": "idm_anomaly_flag * 100",
      "legendFormat": "Anomalie Erkannt"
    }
  ],
  "thresholds": [
    {
      "value": 70,
      "color": "orange"
    },
    {
      "value": 90,
      "color": "red"
    }
  ]
}
```

### 2.2 Alert Integration
**Datei**: `ml_service/main.py`

Integration mit Signal Messenger:
```python
def send_anomaly_alert(score: float, data: dict):
    """Send alert via idm-logger notification system"""
    # Post to idm-logger API endpoint
    alert_url = "http://idm-logger:5000/api/internal/alert"
    payload = {
        "type": "anomaly",
        "score": score,
        "sensors": data,
        "timestamp": time.time()
    }
    requests.post(alert_url, json=payload)
```

### 2.3 Feature Engineering
**Erweiterte Features**:
```python
from datetime import datetime

def enrich_features(data: dict) -> dict:
    """Add temporal and computed features"""
    now = datetime.now()

    # Temporal features
    data['hour_of_day'] = now.hour
    data['day_of_week'] = now.weekday()
    data['is_weekend'] = 1 if now.weekday() >= 5 else 0

    # Computed features (if available)
    if 'flow_temp' in data and 'return_temp' in data:
        data['temp_diff'] = data['flow_temp'] - data['return_temp']

    if 'power_consumption' in data and 'heating_power' in data:
        data['efficiency'] = data['heating_power'] / max(data['power_consumption'], 1)

    return data
```

## Priorität 3: Monitoring & Observability

### 3.1 Model Performance Metrics
**Neue Metriken schreiben**:
```python
def write_ml_metrics(score: float, features_count: int, processing_time: float):
    lines = [
        f"idm_ml_score value={score}",
        f"idm_ml_features_count value={features_count}",
        f"idm_ml_processing_time value={processing_time}",
        f"idm_ml_model_updates value=1"  # Counter
    ]
    # Write to VictoriaMetrics
```

### 3.2 Health Check Endpoint
**Neuer Flask Micro-Service** im ml_service:
```python
from flask import Flask, jsonify

health_app = Flask(__name__)

@health_app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "model_state": "trained" if model_trained else "learning",
        "last_score": last_score,
        "features_count": len(SENSORS),
        "uptime": time.time() - start_time
    })

# Run in separate thread
threading.Thread(target=lambda: health_app.run(host='0.0.0.0', port=8080)).start()
```

## Priorität 4: Dokumentation

### 4.1 README.md für ml_service
**Datei**: `ml_service/README.md`

Inhalt:
- Was macht der Service?
- Wie funktioniert HalfSpaceTrees?
- Welche Parameter gibt es?
- Wie interpretiert man den Anomaly Score?
- Troubleshooting Guide

### 4.2 Inline Dokumentation
Mehr Kommentare für:
- Model Parameter Choices (warum n_trees=25?)
- Threshold Logic (warum 0.7?)
- Feature Selection (warum diese Sensoren?)

## Weitere Ideen

### Multi-Model Ensemble
Statt nur HalfSpaceTrees:
```python
from river import ensemble

model = ensemble.VotingClassifier([
    ('hst', anomaly.HalfSpaceTrees()),
    ('lof', anomaly.LocalOutlierFactor()),
])
```

### Adaptive Thresholds
Basierend auf Historie:
```python
from collections import deque

score_history = deque(maxlen=1000)

def adaptive_threshold():
    if len(score_history) < 100:
        return 0.7  # Default
    mean = np.mean(score_history)
    std = np.std(score_history)
    return mean + 2 * std  # 2-sigma rule
```

### Seasonal Decomposition
Für Wärmepumpen mit starken saisonalen Mustern:
```python
from river import time_series

preprocessor = time_series.STLDecompose()
```

## Implementation Roadmap

1. **Phase 1** (Quick Wins):
   - Konfigurierbare Thresholds
   - Circuit/Zone Config aus ENV
   - Grafana Dashboard Panel

2. **Phase 2** (Core Features):
   - Model Persistence
   - Alert Integration
   - Feature Engineering

3. **Phase 3** (Advanced):
   - Model Performance Monitoring
   - Health Check Endpoint
   - Adaptive Thresholds

4. **Phase 4** (Nice to Have):
   - Multi-Model Ensemble
   - Seasonal Decomposition
   - ML Service Dashboard in Frontend
