# Chart Debugging Guide

## Problem: Charts zeigen keine Daten an

### Symptome
- Charts werden gerendert, aber zeigen keine Werte
- Zoom funktioniert nicht
- Tooltips zeigen keine Daten an
- Keine Fehlermeldung in der Konsole

### Mögliche Ursachen

#### 1. Keine Queries im Chart ✅ Wahrscheinlichste Ursache

Das passiert, wenn ein Chart ohne Drag & Drop Sensoren erstellt wurde.

**Lösung**: Sensoren aus der linken Sidebar in den Chart ziehen

#### 2. VictoriaMetrics hat keine Daten

Die Wärmepumpe muss erst Daten gesammelt haben.

**Prüfung**:
```bash
curl "http://localhost:5008/api/metrics/query?query=idm_heatpump_temp_outside"
```

**Erwartete Antwort**:
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [...]
  }
}
```

#### 3. Modbus-Verbindungsfehler

**Prüfung**: Logs ansehen
```bash
docker logs idm-metrics-collector
```

**Suche nach**:
- `Connection unexpectedly closed`
- `Modbus Error`
- `Connection refused`

#### 4. Chart-Konfiguration fehlerhaft

**Prüfung**: Browser-Konsole öffnen (F12) und nach Fehlern suchen

---

## Debug-Schritte

### Schritt 1: API-Test

Teste, ob die Metrics-API funktioniert:

```bash
# Einzelner Wert
curl "http://localhost:5008/api/metrics/query?query=idm_heatpump_temp_outside"

# Zeitbereich
curl "http://localhost:5008/api/metrics/query_range?query=idm_heatpump_temp_outside&start=$(date -d '24 hours ago' +%s)&end=$(date +%s)&step=60"
```

### Schritt 2: Dashboard-Konfiguration prüfen

Browser-Konsole (F12) öffnen und:

```javascript
// Aktuelles Dashboard anzeigen
fetch('/api/dashboards')
  .then(r => r.json())
  .then(d => console.log('Dashboards:', d))

// Erster Chart prüfen
fetch('/api/dashboards')
  .then(r => r.json())
  .then(d => {
    const firstDashboard = d[0]
    const firstChart = firstDashboard.charts[0]
    console.log('Erster Chart:', firstChart)
    console.log('Queries:', firstChart.queries)
  })
```

### Schritt 3: Netzwerk-Tab prüfen

1. F12 öffnen → Network Tab
2. Seite refreshen
3. Nach `query_range` Requests suchen
4. Response prüfen:
   - Status: 200 OK
   - Response enthält `data.result.values`

### Schritt 4: ChartCard Props prüfen

In der Browser-Konsole (Vue DevTools oder Console):

```javascript
// Chart-Component finden
const chartCard = document.querySelector('.bg-white.rounded-lg').__vueParentComponent
console.log('Props:', chartCard.props)
console.log('Queries:', chartCard.props.queries)
console.log('Hours:', chartCard.props.hours)
```

---

## Häufige Probleme

### Problem 1: "query_range" gibt leere Ergebnisse zurück

**Ursache**: VictoriaMetrics hat noch keine Daten für den Zeitraum

**Lösung**:
- Warten, bis die Wärmepumpe mindestens einen Zyklus läuft (ca. 5-10 Minuten)
- Oder Zeitraum auf "Alles" (0 Stunden) setzen

### Problem 2: Chart zeigt "No data"

**Ursache**: Queries Array ist leer

**Lösung**:
1. Edit Mode aktivieren
2. Chart bearbeiten (Bleistift-Icon)
3. Queries hinzufügen ODER
4. Sensoren aus Sidebar in Chart ziehen

### Problem 3: TypeError in ChartCard

**Ursache**: Query-String ist ungültig

**Lösung**:
- Query-String muss gültiger Metric-Name sein
- Beispiel: `idm_heatpump_temp_outside`
- Nicht: `idm_heatpump_temp_outside ` (mit Leerzeichen)

---

## Manuelles Erstellen eines Charts mit Daten

### Methode 1: Drag & Drop
1. Edit Mode aktivieren
2. Sensor aus linker Sidebar auf Chart-Bereich ziehen
3. Chart wird automatisch erstellt mit Daten

### Methode 2: API-Call
```bash
curl -X POST http://localhost:5008/api/dashboards/default/charts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aussentemperatur",
    "queries": [
      {
        "label": "Aussen",
        "query": "idm_heatpump_temp_outside",
        "color": "#3b82f6"
      }
    ],
    "hours": 24
  }'
```

---

## Logging aktivieren

### Frontend Logging

In `ChartCard.vue` (temporary):

```javascript
const fetchData = async () => {
    console.log('Fetching chart data:', {
        title: props.title,
        queries: props.queries,
        hours: props.hours
    });

    // ... rest of function

    console.log('Chart data loaded:', {
        datasetsCount: datasets.length,
        points: datasets.map(d => d.data?.length || 0)
    });
}
```

### Backend Logging

Bereits aktiv in `web.py`:

```python
@app.route("/api/metrics/query_range", methods=["GET"])
@login_required
def metrics_query_range():
    logger.info(f"Query range request: {request.args}")
    # ...
```

---

## Schnelltest

In Browser-Konsole ausführen:

```javascript
// Teste, ob Chart Component mounted ist
const charts = document.querySelectorAll('[class*="chart"]')
console.log(`Gefundene Charts: ${charts.length}`)

// Teste API
fetch('/api/metrics/query_range?query=idm_heatpump_temp_outside&start=' + (Math.floor(Date.now()/1000) - 86400) + '&end=' + Math.floor(Date.now()/1000) + '&step=60')
  .then(r => r.json())
  .then(d => console.log('API Response:', d))
  .catch(e => console.error('API Error:', e))
```

---

## Nächste Schritte

1. **Browser-Konsole öffnen** (F12)
2. **Network Tab** → nach `query_range` suchen
3. **Response prüfen** → enthält er `values`?
4. **Console Tab** → nach Fehlermeldungen suchen
5. **Vue DevTools** → ChartCard Component → Props prüfen

Wenn immer noch Probleme:
- Logs ansehen: `docker logs idm-metrics-collector`
- VictoriaMetrics prüfen: `http://localhost:8428/vmui`
- Issue erstellen mit Screenshots und Console-Logs
