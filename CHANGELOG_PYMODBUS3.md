# Changelog: Migration zu pymodbus 3.x

## Datum: 2026-01-08

### Übersicht

Das Repository wurde für **pymodbus 3.x** aktualisiert. Die pymodbus-Bibliothek hat zwischen Version 2.x und 3.x Breaking Changes in der API eingeführt.

---

## Geänderte Dateien

### 1. `requirements.txt`

**Vorher:**
```
pymodbus<3.0.0
```

**Nachher:**
```
pymodbus>=3.0.0
```

**Grund:** Die neueste pymodbus-Version (3.11.4) wird verwendet.

---

### 2. `idm_logger/modbus.py`

#### Import-Anpassung

**Vorher:**
```python
# Compatibility with pymodbus < 3.0.0
try:
    from pymodbus.client.sync import ModbusTcpClient
except ImportError:
    from pymodbus.client import ModbusTcpClient
```

**Nachher:**
```python
from pymodbus.client import ModbusTcpClient
```

**Grund:** In pymodbus 3.x gibt es kein `sync` Modul mehr, alle Clients sind direkt unter `pymodbus.client` verfügbar.

#### API-Parameter-Änderung: `unit` → `device_id`

**Vorher:**
```python
rr = self.client.read_holding_registers(sensor.address, count=sensor.size, unit=1)
rr = self.client.write_registers(sensor.address, registers, unit=1)
```

**Nachher:**
```python
rr = self.client.read_holding_registers(sensor.address, count=sensor.size, device_id=1)
rr = self.client.write_registers(sensor.address, registers, device_id=1)
```

**Grund:** pymodbus 3.x hat den Parameter `unit` in `device_id` umbenannt.

**Betroffene Zeilen:**
- Zeile 45: Sensor-Lesevorgänge
- Zeile 67: Binary-Sensor-Lesevorgänge
- Zeile 126: Schreibvorgänge

---

### 3. `docker-compose.yml`

**Hinzugefügt:**
```yaml
environment:
  # IDM Heat Pump connection
  - IDM_HOST=192.168.178.103
  - IDM_PORT=502
```

**Grund:** Umgebungsvariablen für die IDM-Wärmepumpen-Verbindung hinzugefügt.

---

### 4. `docker-compose.dev.yml`

**Hinzugefügt:**
```yaml
environment:
  # IDM Heat Pump connection
  - IDM_HOST=192.168.178.103
  - IDM_PORT=502
```

**Grund:** Gleiche Änderung wie in `docker-compose.yml` für die Development-Umgebung.

---

### 5. `config.yaml.example`

**Vorher:**
```yaml
host: "192.168.1.100"
```

**Nachher:**
```yaml
host: "192.168.178.103"
```

**Grund:** Beispiel-IP an die tatsächlich getestete Wärmepumpe angepasst.

---

## Neue Dateien

### 1. `test_live.py`

Live-Test-Skript zum Testen der Modbus-Verbindung zur IDM-Wärmepumpe.

**Features:**
- Liest wichtige Sensordaten aus (Temperaturen, Leistung, Energie)
- Unterstützt pymodbus 3.x API
- Nur Read-Only-Operationen
- Formatierte Ausgabe mit Einheiten

**Verwendung:**
```bash
python test_live.py
```

### 2. `DOCKER_SETUP.md`

Umfassende Dokumentation für Docker-Deployment:
- Quick Start Anleitung
- Konfiguration der Umgebungsvariablen
- Troubleshooting
- Backup-Anleitungen

### 3. `CHANGELOG_PYMODBUS3.md`

Dieses Dokument.

---

## Breaking Changes

### Für Nutzer

**Keine Breaking Changes für Endnutzer.** Die Anwendung funktioniert nach dem Update genauso wie vorher.

**Docker-Nutzer:**
- Neue Umgebungsvariablen `IDM_HOST` und `IDM_PORT` können optional verwendet werden
- Wenn nicht gesetzt, wird die Standardkonfiguration aus der Datenbank verwendet

### Für Entwickler

**Wichtig:** Wenn Sie lokal entwickeln:

1. **Alte pymodbus-Installation entfernen:**
   ```bash
   pip uninstall pymodbus
   ```

2. **Neue Version installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Code-Änderungen beachten:**
   - Alle `unit=` Parameter in `device_id=` ändern
   - Import-Statement vereinfachen

---

## Test-Ergebnisse

### Live-Test mit IDM Wärmepumpe (192.168.178.103:502)

**Test erfolgreich am: 2026-01-08**

```
============================================================
IDM Wärmepumpe Live-Test (READ ONLY)
============================================================
Host: 192.168.178.103:502
============================================================

[OK] Verbindung erfolgreich!

Sensor                              Wert            Register
------------------------------------------------------------
Außentemperatur                     -0.43           1000
Außentemperatur Durchschnitt        -2.09           1002
System Status                       1               1005
Wärmespeicher Temperatur            45.5 °C         1008
Warmwasser oben Temperatur          47.9 °C         1012
Warmwasser unten Temperatur         50.6 °C         1014
Wärmepumpe Vorlauf                  49.5 °C         1050
Wärmepumpe Rücklauf                 44.8 °C         1052
Wärmequelle Eingang                 -1.00           1056
Wärmequelle Ausgang                 -1.00           1058
Aktuelle Leistung                   10.08 kW        1790
Heizenergie gesamt                  19129.78        1750

============================================================
[OK] Test abgeschlossen - Verbindung geschlossen
============================================================
```

**Ergebnis:** ✅ Alle Register erfolgreich ausgelesen, Wärmepumpe kommuniziert korrekt.

---

## Kompatibilität

### Unterstützte pymodbus-Versionen

- ✅ pymodbus >= 3.0.0 (empfohlen: 3.11.4)
- ❌ pymodbus < 3.0.0 (nicht mehr unterstützt)

### Rückwärtskompatibilität

Diese Version ist **nicht rückwärtskompatibel** mit pymodbus 2.x.

Wenn Sie pymodbus 2.x verwenden müssen, nutzen Sie einen älteren Commit vor diesem Update.

---

## Migration Guide

### Für bestehende Installationen

#### Docker-Installation

1. Docker Compose Services stoppen:
   ```bash
   docker compose down
   ```

2. Neueste Images pullen:
   ```bash
   docker compose pull
   ```

3. Services neu starten:
   ```bash
   docker compose up -d
   ```

#### Native Installation

1. Repository aktualisieren:
   ```bash
   git pull
   ```

2. Dependencies aktualisieren:
   ```bash
   pip install -r requirements.txt
   ```

3. Service neustarten:
   ```bash
   sudo systemctl restart idm-logger
   ```

---

## Weitere Informationen

- **pymodbus 3.x Dokumentation:** https://pymodbus.readthedocs.io/
- **IDM Navigator Modbus Dokumentation:** Siehe `Modbus TCP_Navigator 2.0_DE.pdf`
- **Docker Setup:** Siehe `DOCKER_SETUP.md`

---

## Kontakt

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/Xerolux/idm-metrics-collector/issues
- Pull Requests sind willkommen!
