# ❓ FAQ - Häufig gestellte Fragen

**IDM Metrics Collector - Antworten auf die wichtigsten Fragen**

---

## 📑 Inhaltsverzeichnis

- [Allgemeine Fragen](#-allgemeine-fragen)
- [Installation & Setup](#-installation--setup)
- [KI & Machine Learning](#-ki--machine-learning)
- [Funktionen & Features](#-funktionen--features)
- [Integration & Kompatibilität](#-integration--kompatibilität)
- [Problembehebung](#-problembehebung)
- [Sicherheit & Datenschutz](#-sicherheit--datenschutz)
- [Performance & Ressourcen](#-performance--ressourcen)

---

## 🌟 Allgemeine Fragen

### Was ist IDM Metrics Collector?

IDM Metrics Collector ist eine **All-in-One Open-Source Monitoring- und Steuerungslösung** für IDM Wärmepumpen mit Navigator 2.0 Steuerung. Die Software kombiniert:

- 📊 Professionelles Echtzeit-Dashboard
- 🤖 KI-basierte Anomalieerkennung
- 🏠 Native Home Assistant Integration
- 📅 Intelligente Automatisierung
- 🔔 Multi-Kanal Benachrichtigungen
- ☀️ Photovoltaik-Optimierung

Alles in einer **Docker-basierten Lösung** ohne komplexe Konfiguration.

---

### Ist die Software wirklich kostenlos?

**Ja, zu 100%!** IDM Metrics Collector ist unter der **MIT-Lizenz** veröffentlicht:

✅ Kostenlose private und kommerzielle Nutzung
✅ Offener Quellcode auf GitHub
✅ Keine versteckten Kosten oder Abonnements
✅ Keine Cloud-Services erforderlich

Optionale Features (z.B. Community-Dashboard) sind ebenfalls kostenlos.

---

### Welche Wärmepumpen werden unterstützt?

| Hersteller | Modell | Status | Details |
|------------|--------|--------|---------|
| **IDM** | Navigator 2.0 | ✅ Vollständig | Alle Register dokumentiert |
| **Alpha Innotec** | Luxtronik 2.0 | ⚠️ Experimentell | Meiste Register kompatibel |
| **Stiebel Eltron** | ISG/IWP | ⚠️ Experimentell | Mit Anpassungen möglich |
| **Bosch/Buderus** | Logamatic EMS | ⚠️ Community-Support | Register-Mapping erforderlich |
| **Viessmann** | Vitocal | ⚠️ Community-Support | Register-Mapping erforderlich |
| **NIBE** | S-Series | ⚠️ Community-Support | Modbus-Modul benötigt |
| **Wolf** | CHA | ⚠️ Community-Support | Register-Mapping erforderlich |

Dokumentation für weitere Hersteller: `docs/<HERSTELLER>_MODBUS_REGISTERS.md`

---

### Benötige ich Programmierkenntnisse?

**Nein!** Die Installation besteht aus 3 Befehlen:

```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker compose up -d
```

Die Ersteinrichtung erfolgt über ein grafisches Webinterface. Keine Konfigurationsdateien editieren nötig!

Einzige Voraussetzung: **Docker muss installiert sein**.

---

### Wie unterscheidet sich das von Grafana + InfluxDB?

| Feature | Traditionell (Grafana/InfluxDB) | IDM Metrics Collector |
|---------|--------------------------------|----------------------|
| **Komplexität** | 5+ separate Services | 1 Docker Compose |
| **Setup-Zeit** | 2-4 Stunden | 5 Minuten |
| **KI-Features** | ❌ Nicht vorhanden | ✅ Integriert (River ML) |
| **Wärmepumpen-Steuerung** | ⚠️ Node-RED erforderlich | ✅ Eingebaut |
| **Home Assistant** | ⚠️ Manuelle YAML-Konfiguration | ✅ Auto-Discovery |
| **Updates** | Manuell, Service für Service | ✅ Automatisch (Watchtower) |
| **Dashboard** | ⚠️ Dashboards selbst erstellen | ✅ 7 Templates vorinstalliert |

**Fazit**: IDM Metrics Collector ist **schneller, einfacher und intelligenter**.

---

## 🔧 Installation & Setup

### Welche Hardware benötige ich?

**Minimum-Anforderungen:**
- Raspberry Pi 4 (4GB RAM) **oder**
- Synology/QNAP NAS (Docker-fähig) **oder**
- Intel NUC, Mini-PC, Ubuntu Server

**Empfohlene Hardware:**
- 4GB+ RAM
- 20GB freier Speicherplatz
- Gigabit-Ethernet (kein WLAN!)

**Netzwerk:**
- LAN-Verbindung zur Wärmepumpe (kein WLAN!)
- Feste IP für Server (empfohlen)

---

### Wie aktiviere ich Modbus TCP an der Wärmepumpe?

**Für IDM Navigator 2.0:**

1. **Fachmannebene aktivieren**
   - Einstellungen → Service → Code eingeben (von Installateur)

2. **Modbus aktivieren**
   - Fachmann-Menü → Kommunikation → Modbus TCP
   - Modbus TCP: **Aktiviert**
   - Port: **502** (Standard)

3. **IP-Adresse notieren**
   - Netzwerk → IP-Adresse anzeigen
   - Beispiel: `192.168.1.50`

**Wichtig**: Fachmann-Code bei Ihrem Installateur anfragen!

---

### Docker Installation - Wie geht das?

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Ausloggen und wieder einloggen
```

**Raspberry Pi OS:**
```bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
sudo systemctl enable docker
sudo reboot
```

**Synology NAS:**
- Control Panel → Package Center → Docker installieren

**QNAP NAS:**
- App Center → Container Station installieren

---

### Port 5008 ist bereits belegt - was tun?

**Option 1: Anderen Port verwenden**

```yaml
# docker-compose.yml anpassen
services:
  idm-logger:
    ports:
      - "8080:5008"  # Statt 5008:5008
```

Dann im Browser: `http://<ip>:8080`

**Option 2: Belegenden Dienst identifizieren**

```bash
sudo lsof -i :5008
# oder
sudo netstat -tulpn | grep 5008
```

---

### Wie sichere ich meine Daten?

**Automatisches Backup** (empfohlen):

1. **WebDAV konfigurieren** (z.B. Nextcloud)
   - Einstellungen → Backup → WebDAV URL eingeben
   - Username & Passwort
   - Automatisch täglich um 02:00 Uhr

2. **Lokales Backup**
   - Docker Volumes werden automatisch gesichert
   - Speicherort: `./backups/`

**Manuelles Backup:**

```bash
# Komplettes Backup erstellen
docker compose exec idm-logger python -m idm_logger.backup

# Backup wiederherstellen
docker compose exec idm-logger python -m idm_logger.restore /path/to/backup.tar.gz
```

---

## 🤖 KI & Machine Learning

### Wie funktioniert die KI-Anomalieerkennung?

Die KI verwendet **Online Machine Learning** mit dem **River Framework**:

1. **Datenerfassung** (alle 30-60s)
   - 50+ Sensoren der Wärmepumpe
   - Temperaturen, Drücke, Status, Leistung

2. **Feature Engineering** (automatisch)
   - Zeitliche Merkmale (Stunde, Wochentag)
   - Delta-Features (Änderungsraten)
   - Berechnete Werte (COP, Spreizung)

3. **Multi-Mode Learning**
   - Separate Modelle für Heizen, Kühlen, Warmwasser
   - Jeder Modus hat eigenes "Normal-Verhalten"

4. **Anomalie-Scoring**
   - Score 0.0-1.0 (0=normal, 1=anomal)
   - Threshold: 0.7 (konfigurierbar)
   - Debouncing: 3+ aufeinanderfolgende Anomalien

5. **Alerting**
   - Benachrichtigung bei echter Anomalie
   - 1h Cooldown (kein Spam)

**Vorteil**: Erkennt Probleme, die statische Schwellwerte übersehen würden!

---

### Muss ich das ML-Modell trainieren?

**Nein - das passiert automatisch!**

- **Warm-up Phase**: Erste 1-2 Stunden (120+ Updates)
  - Während dieser Zeit werden keine Anomalien gemeldet
  - Modell lernt den Normalzustand Ihrer Anlage

- **Kontinuierliches Lernen**: Danach läuft es 24/7
  - Modell passt sich saisonal an (Sommer vs. Winter)
  - Verbessert sich mit jeder Datenpunkt

- **Persistenz**: Modell-State wird gespeichert
  - Bei Container-Neustart kein Datenverlust
  - Warmup nicht erneut erforderlich

---

### Welche Anomalien kann die KI erkennen?

**Typische Erkennungen:**

| Anomalie | Wie erkannt | Früherkennung |
|----------|-------------|---------------|
| **Defekter Durchflusssensor** | Temperatur-Spreizung passt nicht zu Leistung | ✅ 1-2 Tage vorher |
| **Undichter Heizkreis** | COP sinkt schleichend über Wochen | ✅ 2-4 Wochen vorher |
| **Verschmutzter Filter** | Druckdifferenz erhöht sich graduell | ✅ 1-2 Wochen vorher |
| **Falsche Heizkurve** | System verhält sich anders als normal | ✅ Sofort |
| **Kompressor-Probleme** | Untypische Laufzeiten/Vibrationen | ✅ 2-4 Wochen vorher |
| **Kältemittelverlust** | COP-Degradation über Monate | ✅ 1-3 Monate vorher |

---

### Kann ich die KI-Sensitivität anpassen?

**Ja!** Über Umgebungsvariablen in `docker-compose.yml`:

```yaml
ml_service:
  environment:
    # Anomalie-Schwellwert (0.0-1.0)
    ANOMALY_THRESHOLD: "0.7"  # Standard
    # 0.5 = Sensitiver (mehr Alarme)
    # 0.9 = Weniger sensitiv (nur gravierende Anomalien)

    # Debounce-Count (consecutive anomalies)
    ANOMALY_DEBOUNCE_COUNT: "3"  # Standard
    # 5 = Weniger False Positives
    # 1 = Sofortige Alarmierung

    # Cooldown-Periode (Minuten)
    ANOMALY_COOLDOWN_MINUTES: "60"  # 1 Stunde

    # Modell-Komplexität
    MODEL_N_TREES: "25"  # Anzahl Entscheidungsbäume
```

Nach Änderung Container neu starten:
```bash
docker compose restart ml_service
```

---

## 🎛️ Funktionen & Features

### Wie erstelle ich ein Dashboard?

**Option 1: Template verwenden** (empfohlen)

1. Dashboard öffnen
2. **"Aus Vorlage erstellen"** Button klicken
3. Template auswählen:
   - Temperaturübersicht
   - Leistungsanalyse
   - Effizienz-Monitor
   - Heizkreis Detail
   - Warmwasser-Monitor
   - Solar-Integration
4. Fertig! Dashboard ist sofort einsatzbereit

**Option 2: Manuell erstellen**

1. **"Neues Panel hinzufügen"** klicken
2. Panel-Typ wählen:
   - **Line Chart** - Zeitverläufe
   - **Stat Panel** - Einzelwerte
   - **Gauge** - Tachometer
3. Metriken auswählen (z.B. `idm_heatpump_temp_flow`)
4. **Drag & Drop** zum Anordnen

---

### Wie richte ich Benachrichtigungen ein?

**Telegram-Bot (beliebt):**

1. **Bot erstellen**
   - Telegram öffnen → @BotFather suchen
   - `/newbot` eingeben
   - Bot-Namen wählen
   - **API-Token** notieren

2. **Chat-ID herausfinden**
   - Bot-Nachricht senden: `/start`
   - https://api.telegram.org/bot<TOKEN>/getUpdates
   - **Chat-ID** kopieren

3. **In IDM Metrics konfigurieren**
   - Einstellungen → Benachrichtigungen → Telegram
   - API-Token & Chat-ID eingeben
   - Speichern & Testen

**Signal (E2E-verschlüsselt):**

Siehe: [Signal Notifications Setup](docs/MANUAL.md#signal-setup)

**ntfy.sh (einfachste Option):**

1. https://ntfy.sh öffnen
2. Topic wählen (z.B. `heatpump-alerts-12345`)
3. IDM Metrics → Einstellungen → Notifications → ntfy
4. Topic eingeben
5. In ntfy App subscriben

---

### Wie erstelle ich einen Zeitplan?

1. **Zeitpläne** (Schedule) öffnen
2. **Neuer Zeitplan** klicken
3. **Wochentag** auswählen
4. **Zeitblock ziehen**:
   - Klicken & Drag über gewünschten Zeitraum
5. **Aktion konfigurieren**:
   - Solltemperatur (z.B. 22°C)
   - Betriebsmodus (Heizen/Eco/Standby)
   - Heizkreis (A/B/C)
6. **Speichern**

**Beispiel: Nachtabsenkung**
- Mo-Fr: 23:00-06:00 → 18°C (Eco-Modus)
- Mo-Fr: 06:00-08:00 → 22°C (Heizen)
- Sa-So: 22:00-09:00 → 18°C (Eco-Modus)

---

### Kann ich die Wärmepumpe fernsteuern?

**Ja**, über mehrere Wege:

1. **Web-Interface**
   - Steuerung (Control) → Sollwerte ändern
   - Sofort-Aktionen (z.B. "1x Warmwasser")

2. **Home Assistant**
   - MQTT-Entities erscheinen automatisch
   - Automations, Scripts, Dashboards

3. **REST API**
   ```bash
   curl -X POST http://<ip>:5008/api/control/set_temperature \
     -H "Authorization: Bearer <token>" \
     -d '{"circuit": "A", "temperature": 22}'
   ```

4. **MQTT (für Experten)**
   ```bash
   mosquitto_pub -t "idm/heatpump/temp_setpoint_hc_a/set" -m "22"
   ```

**Sicherheitshinweis**: EEPROM hat nur ~10.000 Schreibzyklen!
Nicht häufiger als alle 5 Minuten schreiben.

---

## 🏠 Integration & Kompatibilität

### Wie integriere ich Home Assistant?

**Automatische Integration via MQTT Discovery:**

1. **MQTT-Broker in Home Assistant**
   - Configuration.yaml:
     ```yaml
     mqtt:
       broker: localhost
       username: mqtt_user
       password: mqtt_pass
     ```

2. **IDM Metrics konfigurieren**
   - Einstellungen → MQTT
   - Broker IP, Username, Password
   - **Home Assistant Discovery**: Aktiviert
   - Topic-Prefix: `idm/heatpump`

3. **Speichern & Neu starten**
   ```bash
   docker compose restart idm-logger
   ```

4. **In Home Assistant prüfen**
   - Einstellungen → Geräte & Dienste → MQTT
   - "IDM Heat Pump" Device sollte erscheinen
   - 50+ Entities automatisch verfügbar!

**Keine manuelle YAML-Konfiguration nötig!**

Details: [docs/MQTT_SETUP.md](docs/MQTT_SETUP.md)

---

### Funktioniert das mit Amazon Alexa?

**Ja**, über Home Assistant:

1. Home Assistant Cloud (Nabu Casa) Abo **oder**
2. Alexa Smart Home Skill für Home Assistant

Dann:
```
"Alexa, stelle Heizung auf 22 Grad"
"Alexa, wie warm ist die Vorlauftemperatur?"
```

---

### Kann ich mehrere Wärmepumpen überwachen?

**Derzeit nicht direkt**, aber geplant für Q4 2026.

**Workaround**:
- Separate IDM Metrics Instanzen pro Wärmepumpe
- Unterschiedliche Ports (5008, 5009, 5010...)
- VictoriaMetrics kann geteilt werden (verschiedene Prefixes)

---

### Solar-PV Integration - wie geht das?

**Voraussetzung**: Home Assistant mit Solar-Wechselrichter Integration

**Setup:**

1. **IDM Metrics konfigurieren**
   - Einstellungen → Features → Solar-Integration aktivieren

2. **Home Assistant Automation erstellen**
   ```yaml
   automation:
     - alias: "PV-Überschuss an Wärmepumpe"
       trigger:
         - platform: state
           entity_id: sensor.solar_excess_power
       action:
         - service: mqtt.publish
           data:
             topic: "idm/heatpump/power_solar_surplus/set"
             payload: "{{ states('sensor.solar_excess_power') | float / 1000 }}"
   ```

3. **Effekt**:
   - Bei PV-Überschuss: Solltemperatur +2-5°C
   - Speicher wird mit Sonnenstrom geladen
   - Maximaler Eigenverbrauch

Details: [docs/SOLAR_INTEGRATION.md](docs/SOLAR_INTEGRATION.md)

---

## 🔧 Problembehebung

### Ich sehe keine Daten im Dashboard

**Checkliste:**

1. **Modbus-Verbindung prüfen**
   ```bash
   docker compose logs idm-logger | grep -i modbus
   ```

   Sollte zeigen:
   ```
   [INFO] Modbus connected to 192.168.1.50:502
   [INFO] Successfully read 50 registers
   ```

2. **Ist Modbus TCP aktiviert?**
   - An der Wärmepumpe: Fachmann-Menü → Modbus TCP → Aktiviert

3. **Netzwerkverbindung prüfen**
   ```bash
   ping 192.168.1.50
   telnet 192.168.1.50 502
   ```

4. **IP-Adresse korrekt?**
   - Einstellungen → Verbindung → IP prüfen

5. **VictoriaMetrics läuft?**
   ```bash
   docker compose ps
   # victoriametrics sollte "Up" sein
   ```

---

### Fehlermeldung: "Connection refused"

**Ursachen:**

1. **Falsche IP-Adresse**
   - An der Wärmepumpe die IP prüfen

2. **Modbus TCP nicht aktiviert**
   - Fachmann-Code benötigt zur Aktivierung

3. **Firewall blockiert**
   - Port 502 muss offen sein
   - Prüfen: `telnet <wärmepumpen-ip> 502`

4. **Wärmepumpe nicht im gleichen Netzwerk**
   - Keine VLANs oder Subnetz-Trennung

---

### KI meldet zu viele False Positives

**Lösungen:**

1. **Threshold erhöhen**
   ```yaml
   # docker-compose.yml
   ml_service:
     environment:
       ANOMALY_THRESHOLD: "0.8"  # Statt 0.7
   ```

2. **Debounce-Count erhöhen**
   ```yaml
   ANOMALY_DEBOUNCE_COUNT: "5"  # Statt 3
   ```

3. **Warm-up Phase abwarten**
   - Erste 2-3 Tage kann es zu Fehlalarmen kommen
   - Modell lernt noch Normalzustand

4. **Betriebsmodus-Filter**
   - Defrost-Modus wird automatisch übersprungen
   - Andere Modi können ignoriert werden

---

### Dashboard lädt langsam

**Optimierungen:**

1. **Zeitbereich reduzieren**
   - Statt 30 Tage → 7 Tage

2. **Weniger Panels**
   - Max. 8 Charts pro Dashboard empfohlen

3. **Downsampling aktiviert?**
   - VictoriaMetrics macht das automatisch
   - Prüfen: Einstellungen → VictoriaMetrics → Retention

4. **Browser-Cache leeren**
   ```
   Ctrl+Shift+R (Hard Reload)
   ```

---

### Benachrichtigungen kommen nicht an

**Telegram:**
- Bot-Token korrekt?
- Chat-ID richtig?
- Bot mit `/start` aktiviert?

**Signal:**
- signal-cli installiert und registriert?
- Nummer verifiziert?

**Email:**
- SMTP-Server erreichbar?
- Port 587 (TLS) oder 465 (SSL)?
- Authentifizierung korrekt?

**Test-Funktion nutzen:**
- Einstellungen → Benachrichtigungen → "Test senden"

---

### Container starten nicht

```bash
# Logs prüfen
docker compose logs

# Einzelnen Container prüfen
docker compose logs idm-logger
docker compose logs ml_service

# Port-Konflikte?
sudo lsof -i :5008
sudo lsof -i :8428

# Container neu bauen
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🔐 Sicherheit & Datenschutz

### Ist meine Datenverbindung sicher?

**Standard-Setup (LAN-only):**
- ✅ Alle Daten bleiben im lokalen Netzwerk
- ✅ Keine Cloud-Verbindung erforderlich
- ✅ Keine Telemetrie (außer optional aktiviert)

**Fernzugriff (Internet):**
- ⚠️ **Reverse Proxy mit HTTPS verwenden!**
- ⚠️ **IP-Whitelist aktivieren!**
- ✅ Starkes Admin-Passwort (min. 12 Zeichen)

**Empfohlenes Setup für Fernzugriff:**
```
Internet → Cloudflare Tunnel → Nginx (HTTPS) → IDM Metrics
```

---

### Welche Daten werden gesammelt?

**Lokal gespeichert:**
- Wärmepumpen-Sensordaten (Temperaturen, Drücke, Status)
- Konfiguration (IP-Adressen, Passwörter gehashed)
- Alert-Historie
- Zeitpläne
- Dashboard-Layouts

**NICHT gespeichert:**
- Keine personenbezogenen Daten
- Keine Nutzungsstatistiken
- Keine IP-Adressen von Clients (außer für Rate-Limiting)

**Optional (Telemetrie-Server):**
- Anonymisierte Betriebsdaten für Community-ML
- Opt-In, standardmäßig deaktiviert

---

### Kann mich jemand hacken?

**Sicherheitsmaßnahmen:**
- ✅ Passwort-Hashing (bcrypt, 12 rounds)
- ✅ Session-Cookies (HTTPOnly, Secure)
- ✅ Rate Limiting (200 req/min)
- ✅ IP-Whitelist/Blacklist
- ✅ Brute-Force Protection
- ✅ Security Headers (CSP, X-Frame-Options)
- ✅ SQL-Injection geschützt (SQLAlchemy ORM)
- ✅ XSS geschützt (Vue 3 Sanitization)

**Penetration Test:**
- ✅ Keine kritischen Schwachstellen gefunden
- ✅ OWASP Top 10 konform

Details: [docs/SECURITY_ANALYSIS.md](docs/SECURITY_ANALYSIS.md)

**Best Practices:**
- Reverse Proxy mit HTTPS verwenden
- Starkes Admin-Passwort
- IP-Whitelist aktivieren
- Regelmäßige Updates (automatisch via Watchtower)

---

### Wie ändere ich mein Admin-Passwort?

**Option 1: Web-Interface**
1. Login als Admin
2. Einstellungen → Sicherheit → Passwort ändern
3. Altes Passwort + Neues Passwort eingeben

**Option 2: Container-Shell**
```bash
docker compose exec idm-logger python -m idm_logger.reset_password
# Neues Passwort eingeben
```

---

## ⚡ Performance & Ressourcen

### Wie viel RAM/CPU benötigt die Software?

**Ressourcen-Verbrauch:**

| Container | RAM (Idle) | RAM (Peak) | CPU (Avg) | Storage |
|-----------|-----------|-----------|-----------|---------|
| **idm-logger** | 150 MB | 300 MB | 2-5% | 500 MB |
| **ml_service** | 100 MB | 200 MB | 1-3% | 50 MB |
| **victoriametrics** | 80 MB | 200 MB | 1-2% | 2 GB/Jahr |
| **Gesamt** | ~330 MB | ~700 MB | ~5-10% | ~3 GB/Jahr |

**Empfehlung:**
- **Minimum**: 2GB RAM, 2 CPU Cores, 10GB Storage
- **Optimal**: 4GB RAM, 4 CPU Cores, 50GB Storage

---

### Wie lange werden Daten gespeichert?

**VictoriaMetrics (Time Series):**
- **Standard**: 1 Jahr
- **Konfigurierbar**: 1 Monat bis 10 Jahre
- **Downsampling**: Nach 30 Tagen automatisch (5min → 1h Aggregation)

```yaml
# docker-compose.yml
victoriametrics:
  command:
    - '--retentionPeriod=24'  # Monate (12=1 Jahr, 120=10 Jahre)
```

**SQLite (Configuration):**
- Unbegrenzt (sehr klein, ~10MB)

---

### Funktioniert das auf einem Raspberry Pi?

**Ja!** Getestet auf:

| Modell | RAM | Status | Empfehlung |
|--------|-----|--------|------------|
| **Raspberry Pi 5** | 8GB | ✅ Perfekt | Ideal |
| **Raspberry Pi 4** | 4GB | ✅ Gut | Empfohlen |
| **Raspberry Pi 4** | 2GB | ⚠️ Funktioniert | Bei wenigen Charts |
| **Raspberry Pi 3** | 1GB | ❌ Zu langsam | Nicht empfohlen |

**Optimierungen für Pi:**
```yaml
# docker-compose.yml - ML Service Limits
ml_service:
  deploy:
    resources:
      limits:
        memory: 512M  # Statt 768M
```

---

### Wie viel Netzwerkverkehr erzeugt die Software?

**Modbus TCP Polling:**
- ~200 Bytes alle 60 Sekunden
- **~10 KB/Tag** zur Wärmepumpe

**MQTT Publishing (optional):**
- ~1 KB pro Sensor-Update
- **~50 KB/Stunde** zum MQTT Broker

**Web-Interface:**
- Initial Load: ~500 KB (einmalig)
- WebSocket Updates: ~100 Bytes/Update
- **~1-2 MB/Tag** für Dashboards

**Gesamt**: <5 MB/Tag - **vernachlässigbar!**

---

### Kann ich die Polling-Frequenz ändern?

```yaml
# docker-compose.yml
idm-logger:
  environment:
    POLL_INTERVAL: "60"  # Sekunden
    # 30 = Mehr Daten, höhere Last
    # 120 = Weniger Daten, weniger Last
```

**Empfehlung**: 30-60 Sekunden
- Zu schnell: EEPROM-Verschleiß, keine signifikanten Änderungen
- Zu langsam: Wichtige Events werden verpasst

---

## 📞 Support & Weiterführende Hilfe

### Ich habe eine Frage, die hier nicht beantwortet wird

**Reihenfolge der Anlaufstellen:**

1. **📖 Dokumentation durchsuchen**
   - [Benutzerhandbuch](docs/MANUAL.md)
   - [Feature-Übersicht](FEATURES.md)
   - [Architektur-Dokumentation](docs/ARCHITECTURE.md)

2. **🔍 GitHub Issues durchsuchen**
   - [Existing Issues](https://github.com/Xerolux/idm-metrics-collector/issues)
   - Vielleicht wurde die Frage bereits beantwortet

3. **💬 Community fragen**
   - [Discord Server](https://discord.gg/Qa5fW2R)
   - [Home Assistant Forum](https://community.home-assistant.io/)

4. **🐛 Issue erstellen**
   - [Neue Frage/Bug Report](https://github.com/Xerolux/idm-metrics-collector/issues/new)

---

### Wie kann ich zum Projekt beitragen?

**Möglichkeiten:**

1. **📝 Dokumentation verbessern**
   - Tippfehler korrigieren
   - Anleitungen ergänzen
   - Übersetzungen (EN, FR, IT)

2. **🐛 Bugs melden**
   - Detaillierte Fehlerbeschreibung
   - Logs beifügen
   - Reproduktionsschritte

3. **💡 Feature-Ideen**
   - Use-Case beschreiben
   - Mockups/Screenshots hilfreich

4. **💻 Code-Beiträge**
   - Pull Requests willkommen
   - Coding Guidelines beachten

5. **⭐ Projekt promoten**
   - GitHub Star geben
   - Social Media teilen
   - Blog-Posts schreiben

---

### Gibt es einen kommerziellen Support?

**Community-Support (kostenlos):**
- Discord, GitHub Issues, Forum

**Professioneller Support (optional):**
- Für Heizungsbauer/Installateure
- Installation & Setup-Service
- Custom Modbus-Mapping für andere Hersteller
- Kontakt: [support@example.com](#)

---

## 🎓 Nützliche Links

| Thema | Link |
|-------|------|
| 📖 **Hauptdokumentation** | [docs/MANUAL.md](docs/MANUAL.md) |
| 🏗️ **Architektur** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| 🔧 **Installation** | [INSTALL.md](INSTALL.md) |
| 🏠 **MQTT Setup** | [docs/MQTT_SETUP.md](docs/MQTT_SETUP.md) |
| ☀️ **Solar Integration** | [docs/SOLAR_INTEGRATION.md](docs/SOLAR_INTEGRATION.md) |
| 💾 **Backup & Restore** | [docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md) |
| 🔐 **Security Analysis** | [docs/SECURITY_ANALYSIS.md](docs/SECURITY_ANALYSIS.md) |
| 📊 **Features** | [FEATURES.md](FEATURES.md) |
| 🗺️ **Roadmap** | [ROADMAP.md](ROADMAP.md) |
| 📜 **Changelog** | [CHANGELOG.md](CHANGELOG.md) |

---

**Letzte Aktualisierung**: 2026-02-03
**Version**: 1.0.3

**Frage nicht beantwortet?** [Issue erstellen](https://github.com/Xerolux/idm-metrics-collector/issues/new)
