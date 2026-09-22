# Backup und Restore-Funktionalität

## Übersicht

Die IDM Metrics Collector Backup-Funktion erstellt vollständige System-Backups, die alle wichtigen Komponenten und Daten sichern.

## Was wird gesichert?

### 1. Konfiguration & Einstellungen
- **Config**: Alle Systemkonfigurationen aus `config.data`
- **Datenbank-Einstellungen**: Alle Einstellungen aus der SQLite-Datenbank
- **Scheduler-Regeln**: Zeitgesteuerte Aktionen und Automationen
- **Secret Key**: Verschlüsselungsschlüssel (`.secret.key`)

### 2. VictoriaMetrics Datenbank
- **Vollständiger Snapshot**: Alle historischen Metriken der Wärmepumpe
- **Zeitreihen-Daten**: Kompletter Verlauf aller gemessenen Werte
- **Methode**: Nutzt VictoriaMetrics Snapshot-API
- **Speicherort im Container**: `/storage` (Volume: `vm-data`)

### 3. Grafana Dashboards & Einstellungen
- **Dashboards**: Alle benutzerdefinierten und vorinstallierten Dashboards
- **Grafana-Datenbank**: `grafana.db` mit allen Einstellungen
- **Alerting-Regeln**: Konfigurierte Benachrichtigungen
- **Plugins**: Installierte Grafana-Plugins
- **Provisioning-Dateien**: Datasource- und Dashboard-Konfigurationen
- **Speicherort im Container**: `/var/lib/grafana` (Volume: `grafana-data`)

### 4. ML Service (River)
- **Konfiguration**: `main.py`, `requirements.txt`, `Dockerfile`
- **Service-Logs**: Letzte 50 Log-Zeilen für Debugging
- **AI Anomaly State**: `anomaly_state.json` (Trainingsfortschritt)
- **Hinweis**: Das River-ML-Modell selbst wird zur Laufzeit trainiert und ist nicht direkt serialisierbar

### 5. Webseiten-Einstellungen
- **Datenbank**: `idm_logger.db` mit allen Benutzereinstellungen
- **Metadata**: Backup-Version, Erstellungszeit, Hostname

## Backup erstellen

### Via Web-Interface
1. Navigiere zu **Einstellungen** > **Backup & Restore**
2. Klicke auf **Backup erstellen**
3. Das Backup wird in `/app/data/backups/` gespeichert

### Via API
```bash
curl -X POST http://localhost:5008/api/backup/create \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Via Python
```python
from idm_logger.backup import backup_manager

result = backup_manager.create_backup()
if result["success"]:
    print(f"Backup erstellt: {result['filename']}")
    print(f"Größe: {result['size']} bytes")
else:
    print(f"Fehler: {result['error']}")
```

## Backup-Prozess

1. **Metadaten sammeln**: Version, Zeitstempel, Hostname
2. **Config & DB**: Konfiguration und Datenbankeinstellungen sichern
3. **VictoriaMetrics**:
   - Snapshot via API erstellen (`/snapshot/create`)
   - Snapshot aus Container kopieren
   - Snapshot im Container löschen (Speicherplatz sparen)
4. **Grafana**:
   - Dashboards via API exportieren
   - Volume-Daten aus Container kopieren
   - Provisioning-Dateien vom Host kopieren
5. **ML Service**: Config-Dateien und Logs sichern
6. **ZIP erstellen**: Alle Daten in komprimiertes Archiv packen
7. **WebDAV Upload**: Optional zu Nextcloud/WebDAV hochladen

## Backup wiederherstellen

### Via Web-Interface
1. Navigiere zu **Einstellungen** > **Backup & Restore**
2. Wähle ein Backup aus der Liste
3. Klicke auf **Wiederherstellen**
4. Optional: "Secret Key wiederherstellen" aktivieren (Vorsicht!)

### Via API
```bash
curl -X POST http://localhost:5008/api/backup/restore \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_file": "idm_backup_20260116_120000.zip",
    "restore_secrets": false
  }'
```

### Via Python
```python
from idm_logger.backup import backup_manager

result = backup_manager.restore_backup(
    backup_file_path="/app/data/backups/idm_backup_20260116_120000.zip",
    restore_secrets=False
)

if result["success"]:
    print(f"Wiederhergestellt: {', '.join(result['restored_items'])}")
else:
    print(f"Fehler: {result['error']}")
```

## Restore-Prozess

1. **Backup extrahieren**: ZIP in temporäres Verzeichnis entpacken
2. **Config & DB**: Konfiguration und Einstellungen wiederherstellen
3. **VictoriaMetrics**:
   - Snapshot in Container kopieren
   - Snapshot via API wiederherstellen (`/snapshot/restore`)
4. **Grafana**:
   - Dashboards via API importieren
   - Volume-Daten in Container kopieren
   - Grafana neu starten
   - Provisioning-Dateien auf Host wiederherstellen
5. **AI State**: Anomaly-State wiederherstellen
6. **Aufräumen**: Temporäre Dateien löschen
7. **Config neu laden**: System-Reload durchführen

## Backup-Aufbewahrung

Standardmäßig werden die letzten 10 Backups aufbewahrt. Ältere Backups werden automatisch gelöscht.

### Konfiguration
```yaml
backup:
  retention: 10  # Anzahl der aufzubewahrenden Backups
  auto_upload: true  # Automatischer Upload zu WebDAV
```

### Manuelle Bereinigung
```python
from idm_logger.backup import backup_manager

result = backup_manager.cleanup_old_backups(keep_count=10)
print(f"Behalten: {result['kept']}, Gelöscht: {result['deleted']}")
```

## WebDAV / Nextcloud Integration

Backups können automatisch zu Nextcloud oder einem WebDAV-Server hochgeladen werden.

### Konfiguration
```yaml
webdav:
  enabled: true
  url: "https://nextcloud.example.com/remote.php/dav/files/username/"
  username: "your-username"
  password: "your-password"

backup:
  auto_upload: true
```

### Manueller Upload
```python
from idm_logger.backup import backup_manager

result = backup_manager.upload_to_webdav(
    "/app/data/backups/idm_backup_20260116_120000.zip"
)

if result["success"]:
    print("Upload erfolgreich")
else:
    print(f"Fehler: {result['error']}")
```

## Backup-Dateien

### Struktur
```
idm_backup_20260116_120000.zip
├── backup.json                    # Metadata, Config, DB-Settings
├── database/
│   └── idm_logger.db             # SQLite Datenbank
├── secrets/
│   └── .secret.key               # Verschlüsselungsschlüssel
├── ai/
│   └── anomaly_state.json        # AI-Trainingsstand
├── victoriametrics/
│   └── <snapshot-name>/          # VM Snapshot-Daten
│       ├── data/
│       └── metadata.json
├── grafana/
│   ├── dashboards/               # Exportierte Dashboards
│   │   ├── dashboard1.json
│   │   └── dashboard2.json
│   ├── volume/                   # Grafana Volume-Daten
│   │   ├── grafana.db
│   │   ├── alerting/
│   │   └── plugins/
│   ├── provisioning/             # Datasource-Config
│   │   ├── datasources/
│   │   └── dashboards/
│   └── host_dashboards/          # Host Dashboard-Dateien
└── ml_service/
    ├── main.py
    ├── requirements.txt
    ├── Dockerfile
    └── ml_service_logs.txt
```

### Backup-Größe
- **Klein** (ohne VM): ~1-5 MB
- **Mittel** (mit VM, kurze Historie): ~50-200 MB
- **Groß** (mit VM, 1 Jahr Daten): 500 MB - 2 GB

## Wichtige Hinweise

### Secret Key Wiederherstellung
⚠️ **VORSICHT**: Das Wiederherstellen des Secret Keys kann zu Problemen führen, wenn verschlüsselte Daten mit einem anderen Schlüssel erstellt wurden. Nur verwenden, wenn Sie sicher sind!

### Docker-Anforderungen
Die erweiterte Backup-Funktion benötigt Zugriff auf Docker-Container:
- `docker cp` muss funktionieren
- Container müssen laufen: `idm-victoriametrics`, `idm-grafana`, `idm-ml-service`
- Netzwerk-Zugriff auf Container-APIs

### VictoriaMetrics Snapshot-API
VictoriaMetrics muss mit aktivierter Snapshot-API laufen. Dies ist standardmäßig aktiviert.

### Grafana API-Zugriff
Standardmäßig verwendet die Backup-Funktion die Umgebungsvariablen:
- `GF_SECURITY_ADMIN_USER` (default: `admin`)
- `GF_SECURITY_ADMIN_PASSWORD` (default: `admin`)

Stellen Sie sicher, dass diese Credentials korrekt sind.

## Fehlerbehandlung

Die Backup-Funktion ist robust konzipiert:
- **Teilweise Fehler**: Wenn eine Komponente fehlschlägt, werden die anderen trotzdem gesichert
- **Metadata**: `backup.json` enthält Informationen, welche Komponenten erfolgreich gesichert wurden
- **Logging**: Alle Operationen werden protokolliert
- **Cleanup**: Temporäre Dateien werden immer aufgeräumt

### Beispiel-Metadata
```json
{
  "metadata": {
    "version": "1.0",
    "created_at": "2026-01-16T12:00:00",
    "hostname": "idm-logger",
    "victoriametrics_backed_up": true,
    "grafana_backed_up": true,
    "ml_service_backed_up": true
  }
}
```

## Automatische Backups

Für automatische Backups kann ein Cron-Job oder Scheduler verwendet werden:

```python
# In scheduler.py oder als Cron-Job
from idm_logger.backup import backup_manager
import schedule
import time

def scheduled_backup():
    result = backup_manager.create_backup()
    if result["success"]:
        print(f"Automatisches Backup erstellt: {result['filename']}")
        backup_manager.cleanup_old_backups()  # Alte Backups aufräumen

# Täglich um 2:00 Uhr
schedule.every().day.at("02:00").do(scheduled_backup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Troubleshooting

### Problem: VictoriaMetrics Backup schlägt fehl
**Lösung**:
- Prüfen Sie, ob der Container läuft: `docker ps | grep victoriametrics`
- Prüfen Sie die Snapshot-API: `curl http://localhost:8428/snapshot/list`
- Prüfen Sie die Logs: `docker logs idm-victoriametrics`

### Problem: Grafana Dashboards werden nicht exportiert
**Lösung**:
- Prüfen Sie Grafana-Login: `curl http://localhost:3001/api/health`
- Prüfen Sie Credentials in Umgebungsvariablen
- Grafana API erfordert Admin-Rechte

### Problem: Docker cp schlägt fehl
**Lösung**:
- Prüfen Sie Docker-Berechtigungen
- Stellen Sie sicher, dass der Benutzer zur Docker-Gruppe gehört
- Im Container-Modus: Mount Docker-Socket (`/var/run/docker.sock`)

### Problem: Backup ist sehr groß
**Lösung**:
- VictoriaMetrics Retention reduzieren
- Alte Metriken löschen
- Backup-Kompression überprüfen
- Nur relevante Daten sichern

## Sicherheit

- Backups enthalten sensible Daten (Passwörter, API-Keys)
- Speichern Sie Backups sicher
- Verschlüsseln Sie Backups vor Upload zu externen Diensten
- Nutzen Sie WebDAV über HTTPS
- Beschränken Sie Zugriff auf Backup-Verzeichnis
- Rotieren Sie regelmäßig Secret Keys

## Migration zwischen Systemen

Um das gesamte System auf einen neuen Server zu migrieren:

1. **Backup erstellen** auf altem System
2. **Docker-Compose & Code** auf neuen Server kopieren
3. **Container starten** auf neuem Server
4. **Backup wiederherstellen** auf neuem System
5. **Services neu starten**: `docker-compose restart`
6. **Funktionalität prüfen**: Dashboards, Metriken, ML Service

## Weitere Informationen

- [VictoriaMetrics Snapshot Docs](https://docs.victoriametrics.com/Single-server-VictoriaMetrics.html#how-to-work-with-snapshots)
- [Grafana API Docs](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [WebDAV4 Python Client](https://github.com/skshetry/webdav4)
