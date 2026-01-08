# Web Interface Updates - Neue Features

## ✅ Alle Probleme behoben!

### 1. ✅ Restart-Button hinzugefügt
**Location:** Config-Seite (`http://localhost:5008/config`)

Der Service kann jetzt direkt aus dem Web-Interface neu gestartet werden:
- Scrolle runter auf der Config-Seite
- Klicke auf "Restart Service" (orangener Button)
- Bestätige den Dialog
- Der Container startet automatisch neu

**Wie es funktioniert:**
- Sendet SIGTERM an den Container
- Docker startet den Container automatisch neu (`restart: unless-stopped`)
- Alle Konfigurationsänderungen werden beim Neustart übernommen

### 2. ✅ Port-Änderung im Web-Interface
**Location:** Config-Seite unter "Web Interface"

Du kannst jetzt den Web-Server-Port direkt ändern:
```
Web Interface
  Web Server Port: [5000]
  Change requires container restart to take effect
```

**Validation:**
- Port muss zwischen 1024 und 65535 liegen
- Wird in der Datenbank gespeichert
- Erfordert Neustart (nutze den Restart-Button!)

**WICHTIG:** Nach Port-Änderung musst du auch die docker-compose.yml anpassen:
```yaml
ports:
  - "5008:5000"  # Ändere 5000 auf deinen neuen Port
```

### 3. ✅ Write Capabilities Toggle
**Location:** Config-Seite unter "Web Interface"

Du kannst write_enabled jetzt per UI umschalten:
```
☑ Enable write operations and scheduling
  Requires restart to activate scheduler
```

**Vorher:** Musste config.yaml manuell editiert werden
**Jetzt:** Einfach Checkbox an/aus und Speichern
**Wichtig:** Neustart erforderlich, damit der Scheduler aktiviert wird!

### 4. ✅ Schedule-Fehler behoben

**Das Problem:**
```
ERROR Exception on /schedule [GET]
```

**Root Cause:**
- Scheduler war beim Start deaktiviert (write_enabled=False)
- Du hast dann write_enabled aktiviert, ohne neu zu starten
- scheduler_instance existierte, war aber nicht gestartet
- Fehlende Null-Checks verursachten Internal Server Error

**Die Lösung:**
- ✅ Zusätzliche Null-Checks für scheduler_instance
- ✅ Try-Catch um Sensor-Enumeration
- ✅ Freundliche Fehlermeldung: "Scheduler not available. Please restart the service."
- ✅ Bessere Error-Handling bei modbus_client_instance

## 🚀 So testest du die neuen Features:

### Test 1: Lokales Image neu bauen

```bash
cd ~/idm-metrics-collector
git pull

# Container mit neuem Code bauen und starten
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up --build -d

# Logs verfolgen
docker compose -f docker-compose.dev.yml logs -f idm-logger
```

### Test 2: Config-Seite öffnen

```bash
# Im Browser öffnen
http://localhost:5008/config
```

Du solltest jetzt sehen:
- ✅ Neuer Bereich "Web Interface" mit Port und Write Enabled
- ✅ Restart-Button am Ende der Seite

### Test 3: Write Capabilities aktivieren

1. Gehe zu Config-Seite
2. Aktiviere: ☑ Enable write operations and scheduling
3. Klicke "Save Changes"
4. Klicke "Restart Service"
5. Warte 10 Sekunden
6. Refresh die Seite
7. Gehe zu "Schedule" (`/schedule`)
8. **KEIN** Internal Server Error mehr! 🎉

### Test 4: Port ändern (optional)

1. Gehe zu Config-Seite
2. Ändere "Web Server Port" von 5000 auf z.B. 5001
3. Klicke "Save Changes"
4. Klicke "Restart Service"
5. **WICHTIG:** Passe docker-compose.yml an:
   ```yaml
   ports:
     - "5008:5001"  # Neuer Port
   ```
6. Restart Container: `docker compose restart idm-logger`
7. Website ist jetzt unter `http://localhost:5008` erreichbar (mapping zu 5001 intern)

### Test 5: Schedule verwenden

**Voraussetzungen:**
- ✅ write_enabled ist aktiviert
- ✅ Service wurde neu gestartet
- ✅ IDM Host ist konfiguriert

**Steps:**
1. Gehe zu `/schedule`
2. Du solltest die Schedule-Seite sehen (kein Fehler!)
3. Füge einen neuen Job hinzu:
   - Wähle einen Sensor
   - Setze einen Wert
   - Wähle eine Zeit
   - Wähle Tage
4. Klicke "Save Schedule"
5. Der Job erscheint in der Liste
6. Teste mit "Test" Button (Run Now)

## 📋 Zusammenfassung der Commits

**Branch:** `claude/test-docker-compose-website-dnR2k`

**Commits:**
1. ✅ Add 'latest' tag to GHCR image (4ccf8c0)
2. ✅ Fix Docker container startup: ModuleNotFoundError (8dca60f)
3. ✅ Add quick-fix guide (fdbf4ef)
4. ✅ **Add web interface features** (216d4da) ← **NEUER COMMIT**

## ⚠️ Wichtige Hinweise

### Schedule funktioniert nur wenn:
1. ✅ write_enabled ist aktiviert
2. ✅ Service wurde neu gestartet (nach Aktivierung)
3. ✅ IDM Host ist korrekt konfiguriert
4. ✅ Modbus-Verbindung funktioniert

### Restart-Button funktioniert nur in Docker:
- Container muss mit `restart: unless-stopped` laufen
- Bei lokalem Python-Start: Script endet, startet nicht automatisch neu

### Port-Änderung erfordert:
1. Änderung im Web-Interface speichern
2. Service neu starten
3. Docker-Compose Port-Mapping anpassen (falls nötig)
4. Container neu starten

## 🎉 Fertig!

Alle Features sind implementiert und committed:
- ✅ Restart-Button
- ✅ Port-Änderung
- ✅ Write Enabled Toggle
- ✅ Schedule-Fehler behoben

Teste die neuen Features und merge dann zum Main-Branch! 🚀

---

**Stand:** 2026-01-08
**Commit:** 216d4da
**Branch:** claude/test-docker-compose-website-dnR2k
