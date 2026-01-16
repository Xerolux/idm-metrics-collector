# IDM ML Service - AI Anomalie-Erkennung

## 🤖 Übersicht

Der ML Service ist ein spezialisierter Microservice für die Echtzeit-Anomalieerkennung in IDM Wärmepumpen-Daten. Er nutzt **River** (Online Machine Learning) mit dem **HalfSpaceTrees** Algorithmus, um ungewöhnliches Verhalten frühzeitig zu erkennen.

## 🎯 Features

- ✅ **Online Learning**: Modell lernt kontinuierlich aus neuen Daten
- ✅ **Model Persistence**: Zustand bleibt über Container-Neustarts erhalten
- ✅ **Feature Engineering**: Automatische Berechnung abgeleiteter Features (Effizienz, Zeitinformationen)
- ✅ **Flexible Konfiguration**: Alle Parameter über Environment Variables steuerbar
- ✅ **Alert Integration**: Automatische Benachrichtigungen bei Anomalien
- ✅ **Health Check Endpoint**: Monitoring-fähig auf Port 8080
- ✅ **Multi-Circuit Support**: Unterstützung für mehrere Heizkreise und Zonen

## 📊 Wie funktioniert es?

### HalfSpaceTrees Algorithmus

HalfSpaceTrees ist ein **unsupervised anomaly detection** Algorithmus, der:

1. Einen "Normalzustand" aus historischen Daten lernt
2. Neue Datenpunkte mit diesem Normalzustand vergleicht
3. Einen **Anomalie-Score** zwischen 0 und 1 berechnet
   - **0.0 - 0.5**: Normales Verhalten
   - **0.5 - 0.7**: Leicht ungewöhnlich
   - **0.7 - 0.9**: Anomalie (Standard-Threshold)
   - **0.9 - 1.0**: Starke Anomalie

### Feature Engineering

Der Service berechnet automatisch zusätzliche Features:

**Temporale Features:**
- Stunde des Tages (0-23)
- Wochentag (0-6)
- Wochenende (Ja/Nein)

**Berechnete Features:**
- Temperaturdifferenz (Vorlauf - Rücklauf)
- Effizienz-Approximation (Heizleistung / Stromverbrauch)

Diese zusätzlichen Features verbessern die Erkennungsgenauigkeit erheblich.

## ⚙️ Konfiguration

### Environment Variables

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `METRICS_URL` | `http://victoriametrics:8428` | VictoriaMetrics URL |
| `UPDATE_INTERVAL` | `30` | Update-Intervall in Sekunden |
| `MEASUREMENT_NAME` | `idm_heatpump` | Metric Prefix |
| **ML Configuration** |
| `ANOMALY_THRESHOLD` | `0.7` | Schwellwert für Anomalie-Erkennung (0.0-1.0) |
| `MIN_DATA_RATIO` | `0.8` | Min. Anteil verfügbarer Sensoren (0.0-1.0) |
| `MODEL_N_TREES` | `25` | Anzahl Trees im Forest |
| `MODEL_HEIGHT` | `15` | Maximale Tree-Höhe |
| `MODEL_WINDOW_SIZE` | `250` | Sliding Window für Anomalien |
| `MODEL_SAVE_INTERVAL` | `300` | Model-Speicherung alle N Sekunden |
| `MODEL_PATH` | `/app/data/model_state.pkl` | Pfad für Model Persistence |
| **Alert Configuration** |
| `ENABLE_ALERTS` | `true` | Alerts aktivieren |
| `ALERT_COOLDOWN` | `3600` | Mindestabstand zwischen Alerts (Sekunden) |
| `IDM_LOGGER_URL` | `http://idm-logger:5000` | URL des IDM Logger Service |
| **Sensor Coverage** |
| `ML_CIRCUITS` | `A` | Heizkreise (kommasepariert: `A,B,C`) |
| `ML_ZONES` | `` | Zonen (kommasepariert: `0,1,2`) |

### Beispiel: Mehrere Heizkreise

```yaml
environment:
  - ML_CIRCUITS=A,B,C
  - ML_ZONES=0,1
  - ANOMALY_THRESHOLD=0.75
  - UPDATE_INTERVAL=30
```

## 🏥 Health Check

Der Service bietet einen Health Check Endpoint auf **Port 8080**:

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_state": "trained",
  "last_score": 0.234,
  "features_count": 45,
  "uptime_seconds": 3600,
  "update_interval": 30,
  "anomaly_threshold": 0.7,
  "updates_processed": 120
}
```

## 📈 Metriken

Der Service schreibt folgende Metriken nach VictoriaMetrics:

| Metrik | Beschreibung |
|--------|--------------|
| `idm_anomaly_score` | Anomalie-Score (0.0-1.0) |
| `idm_anomaly_flag` | Binär: Anomalie erkannt (0/1) |
| `idm_ml_features_count` | Anzahl verarbeiteter Features |
| `idm_ml_processing_time_ms` | Verarbeitungszeit in Millisekunden |
| `idm_ml_model_updates` | Counter für Model-Updates |

Diese können im **Grafana Dashboard** visualisiert werden.

## 🔔 Alerts

Bei erkannten Anomalien:

1. ✅ Metrik `idm_anomaly_flag=1` wird gesetzt
2. ✅ Alert wird an IDM Logger geschickt
3. ✅ Notification Manager verschickt Benachrichtigungen (Signal/Email/etc.)
4. ✅ Cooldown verhindert Spam (Standard: 1 Stunde)

**Alert-Nachricht Beispiel:**
```
⚠️ Anomalie erkannt! Score: 0.85 (Schwellwert: 0.7)
```

## 🛠️ Troubleshooting

### Modell lernt nicht

**Symptom**: `model_state: "learning"` bleibt bestehen

**Lösung**:
- Mindestens 10 Updates benötigt für Training-Phase
- Prüfe `MIN_DATA_RATIO` - evtl. zu hoch
- Überprüfe VictoriaMetrics Connection

### Zu viele False Positives

**Symptom**: Ständig Anomalien, obwohl alles normal läuft

**Lösung**:
```yaml
environment:
  - ANOMALY_THRESHOLD=0.8  # Höherer Threshold
  - MODEL_WINDOW_SIZE=500  # Größeres Window
```

### Keine Alerts

**Symptom**: Anomalien erkannt, aber keine Benachrichtigungen

**Lösung**:
- Prüfe `ENABLE_ALERTS=true`
- Überprüfe IDM Logger URL
- Checke Notification Manager Config im Haupt-Service
- Prüfe Cooldown (`ALERT_COOLDOWN`)

### Model State geht verloren

**Symptom**: Nach Neustart beginnt Training von vorne

**Lösung**:
- Überprüfe Volume Mount: `ml-model-data:/app/data`
- Prüfe Schreibrechte im Container
- Logs prüfen: `docker logs idm-ml-service | grep "model"`

## 🧪 Testing

### Manuell Anomalie erzeugen

Für Tests kannst du künstliche Anomalien erzeugen:

1. **Extreme Werte** in VictoriaMetrics schreiben
2. **Viele Sensoren gleichzeitig ausfallen** lassen
3. **Threshold temporär senken**:
   ```bash
   docker exec idm-ml-service sh -c 'export ANOMALY_THRESHOLD=0.3'
   ```

### Health Check testen

```bash
# Status prüfen
docker exec idm-ml-service curl -s http://localhost:8080/health | jq

# Logs verfolgen
docker logs -f idm-ml-service
```

## 📚 Technische Details

### Dependencies

- **River 0.23.0**: Online ML Framework
- **Flask**: Health Check Server
- **requests**: HTTP Client für API Calls
- **schedule**: Job Scheduler

### Model Details

**HalfSpaceTrees Parameter:**
- `n_trees=25`: Ensemble aus 25 Trees (mehr = genauer, aber langsamer)
- `height=15`: Max Tree-Tiefe (höher = mehr Granularität)
- `window_size=250`: Sliding Window (größer = stabilere Scores)
- `seed=42`: Reproduzierbarkeit

**Preprocessing:**
- `StandardScaler`: Z-Score Normalisierung aller Features

### Architektur

```
┌─────────────────────────────────────┐
│  VictoriaMetrics (Datenquelle)      │
└────────────────┬────────────────────┘
                 │ Prometheus API
                 ▼
┌─────────────────────────────────────┐
│  ML Service                          │
│  ┌──────────────────────────────┐  │
│  │  Data Fetcher                │  │
│  └──────────┬───────────────────┘  │
│             ▼                        │
│  ┌──────────────────────────────┐  │
│  │  Feature Engineering         │  │
│  └──────────┬───────────────────┘  │
│             ▼                        │
│  ┌──────────────────────────────┐  │
│  │  River HalfSpaceTrees        │  │
│  │  (Online Learning)           │  │
│  └──────────┬───────────────────┘  │
│             ▼                        │
│  ┌──────────────────────────────┐  │
│  │  Anomaly Detector            │  │
│  │  (Threshold: 0.7)            │  │
│  └──────────┬───────────────────┘  │
│             ▼                        │
│  ┌──────────────────────────────┐  │
│  │  Metrics Writer              │  │
│  └──────────┬───────────────────┘  │
│             │                        │
│             ├─► VictoriaMetrics     │
│             └─► Alert System         │
└─────────────────────────────────────┘
```

## 🔮 Zukünftige Erweiterungen

- [ ] **Adaptive Thresholds**: Automatische Anpassung basierend auf Historie
- [ ] **Multi-Model Ensemble**: Kombination mehrerer Algorithmen
- [ ] **Seasonal Decomposition**: Bessere Behandlung saisonaler Muster
- [ ] **Explainable AI**: Welche Features trugen zur Anomalie bei?
- [ ] **Feedback Loop**: Benutzer-Feedback zur Verbesserung
- [ ] **Prometheus Exporter**: Native Prometheus Metrics

## 📄 Lizenz

MIT License - Teil des IDM Metrics Collector Projekts

## 🤝 Support

- GitHub Issues: https://github.com/xerolux/idm-metrics-collector/issues
- Discord: https://discord.gg/Qa5fW2R
