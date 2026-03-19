# 📦 Installation Guide - IDM Metrics Collector

**Umfassende Installationsanleitung für alle Plattformen**

---

## 📑 Inhaltsverzeichnis

1. [System-Voraussetzungen](#-system-voraussetzungen)
2. [Docker Installation](#-docker-installation)
3. [IDM Metrics Collector Installation](#-idm-metrics-collector-installation)
4. [Plattform-spezifische Anleitungen](#-plattform-spezifische-anleitungen)
5. [Ersteinrichtung](#-ersteinrichtung)
6. [Erweiterte Konfiguration](#-erweiterte-konfiguration)
7. [Updates & Wartung](#-updates--wartung)
8. [Deinstallation](#-deinstallation)
9. [Problembehandlung](#-problembehandlung)

---

## ✅ System-Voraussetzungen

### Hardware-Anforderungen

<table>
<tr>
<td width="50%">

#### Minimum-Konfiguration
- **CPU**: 2 Cores (ARM oder x86_64)
- **RAM**: 2 GB
- **Storage**: 10 GB freier Speicherplatz
- **Netzwerk**: Ethernet (kein WLAN!)

**Geeignet für**:
- Raspberry Pi 4 (4GB)
- Einfache Dashboards
- Wenige Charts

</td>
<td width="50%">

#### Empfohlene Konfiguration
- **CPU**: 4 Cores (x86_64)
- **RAM**: 4 GB+
- **Storage**: 50 GB SSD
- **Netzwerk**: Gigabit-Ethernet

**Optimal für**:
- Intel NUC, Mini-PC
- Synology/QNAP NAS
- Viele Charts & Langzeit-Speicherung
- Schnelle Reaktionszeiten

</td>
</tr>
</table>

### Software-Voraussetzungen

| Komponente | Version | Notwendig | Hinweis |
|------------|---------|-----------|---------|
| **Docker Engine** | 20.10+ | ✅ Pflicht | Oder Docker Desktop |
| **Docker Compose** | 2.0+ | ✅ Pflicht | V2 empfohlen (integriert) |
| **Git** | 2.0+ | ✅ Pflicht | Zum Klonen des Repos |
| **Linux/Unix OS** | - | ⚠️ Empfohlen | Oder macOS, Windows mit WSL2 |
| **Internet** | - | ✅ Initial | Für Image-Download |

### Netzwerk-Voraussetzungen

- ✅ **LAN-Verbindung** zur IDM Wärmepumpe (Port 502)
- ✅ **Modbus TCP aktiviert** an der Wärmepumpe (Fachmannebene)
- ✅ **Feste IP-Adresse** für Server (empfohlen)
- ⚠️ **Kein WLAN** - Verbindung zu instabil für Modbus TCP
- ⚠️ **Keine VLANs** zwischen Server und Wärmepumpe

---

## 🐳 Docker Installation

### Ubuntu / Debian

```bash
# Docker Repository hinzufügen
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Repository zur APT-Liste hinzufügen
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker installieren
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Benutzer zur Docker-Gruppe hinzufügen (kein sudo mehr nötig)
sudo usermod -aG docker $USER

# Ausloggen und wieder einloggen, dann testen:
docker --version
docker compose version
```

### Raspberry Pi OS

```bash
# Docker Convenience Script (empfohlen für Pi)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Benutzer zur Docker-Gruppe
sudo usermod -aG docker pi

# Docker beim Boot starten
sudo systemctl enable docker

# Neustart erforderlich
sudo reboot

# Nach Neustart testen
docker --version
docker compose version
```

### CentOS / RHEL / Fedora

```bash
# Docker Repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Docker installieren
sudo yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker starten
sudo systemctl start docker
sudo systemctl enable docker

# Benutzer zur Docker-Gruppe
sudo usermod -aG docker $USER

# Abmelden und neu anmelden
```

### macOS (Docker Desktop)

1. **Docker Desktop herunterladen**
   - https://www.docker.com/products/docker-desktop/

2. **DMG-Datei öffnen und installieren**
   - Docker.app in den Programme-Ordner ziehen

3. **Docker Desktop starten**
   - Beim ersten Start: Lizenz akzeptieren

4. **Überprüfen**
   ```bash
   docker --version
   docker compose version
   ```

### Windows (Docker Desktop mit WSL2)

1. **WSL2 installieren** (falls noch nicht vorhanden)
   ```powershell
   # In PowerShell als Administrator
   wsl --install
   ```

2. **Docker Desktop herunterladen**
   - https://www.docker.com/products/docker-desktop/

3. **Installieren und starten**
   - Installer ausführen
   - Bei Aufforderung WSL2-Backend auswählen

4. **Überprüfen** (in PowerShell oder WSL2-Terminal)
   ```bash
   docker --version
   docker compose version
   ```

---

## 🚀 IDM Metrics Collector Installation

### Standard-Installation (Empfohlen)

**Schritt 1: Repository klonen**

```bash
# In Ihr bevorzugtes Verzeichnis wechseln
cd /opt  # oder ~/docker oder /home/user/apps

# Repository klonen
git clone https://github.com/Xerolux/idm-metrics-collector.git

# In das Verzeichnis wechseln
cd idm-metrics-collector
```

**Schritt 2: Konfiguration anpassen (optional)**

```bash
# .env Datei erstellen (optional für erweiterte Konfiguration)
cp .env.example .env

# .env editieren
nano .env
```

**Beispiel `.env` Datei:**
```bash
# Wärmepumpe
IDM_HOST=192.168.1.50
IDM_PORT=502

# Admin-Passwort (wird beim ersten Start gesetzt)
# ADMIN_PASSWORD=MeinSicheresPasswort

# Polling-Intervall (Sekunden)
POLL_INTERVAL=60

# MQTT (optional)
MQTT_ENABLED=false
MQTT_BROKER=
MQTT_USERNAME=
MQTT_PASSWORD=

# VictoriaMetrics Retention (Monate)
VM_RETENTION_PERIOD=12
```

**Schritt 3: Container starten**

```bash
# Alle Container im Hintergrund starten
docker compose up -d

# Status prüfen (alle Container sollten "Up" sein)
docker compose ps

# Logs verfolgen (Ctrl+C zum Beenden)
docker compose logs -f
```

**Erwartete Ausgabe:**
```
[+] Running 4/4
 ✔ Network idm-metrics-collector_default        Created
 ✔ Container idm-metrics-collector-victoriametrics-1  Started
 ✔ Container idm-metrics-collector-ml_service-1       Started
 ✔ Container idm-metrics-collector-idm-logger-1       Started
 ✔ Container idm-metrics-collector-watchtower-1       Started
```

**Schritt 4: Web-Interface öffnen**

```
http://<server-ip>:5008
```

Beispiel: `http://192.168.1.100:5008`

---

## 🖥️ Plattform-spezifische Anleitungen

### Synology NAS (DSM 7.0+)

**1. Container Manager installieren**
- Paket-Zentrum → Container Manager suchen und installieren

**2. SSH aktivieren** (für Git)
- Systemsteuerung → Terminal & SNMP → SSH aktivieren

**3. Per SSH verbinden**
```bash
ssh admin@nas-ip
sudo -i  # Root-Rechte
```

**4. Installation**
```bash
cd /volume1/docker  # oder /volume2/docker
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker compose up -d
```

**5. Im Browser öffnen**
```
http://nas-ip:5008
```

**Firewall-Regel hinzufügen:**
- Systemsteuerung → Sicherheit → Firewall → Bearbeiten
- Regel erstellen: Erlauben, Port 5008, TCP

---

### QNAP NAS (QTS/QuTS)

**1. Container Station installieren**
- App Center → Container Station suchen und installieren

**2. SSH aktivieren**
- Systemsteuerung → Telnet / SSH → SSH aktivieren

**3. Per SSH verbinden**
```bash
ssh admin@qnap-ip
```

**4. Installation**
```bash
cd /share/Container
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker-compose up -d
```

**5. Im Browser öffnen**
```
http://qnap-ip:5008
```

---

### Proxmox LXC Container

**1. LXC Container erstellen**
- Proxmox Web UI → Create CT
- Template: Ubuntu 22.04
- Cores: 2, RAM: 4096 MB, Disk: 20 GB
- Network: DHCP oder statische IP

**2. Container starten und verbinden**
```bash
# In Proxmox Shell
pct start 100
pct enter 100
```

**3. Docker installieren**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**4. IDM Metrics installieren**
```bash
cd /opt
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker compose up -d
```

**Wichtig für LXC**:
- Container muss "privileged" oder mit "nesting=1" Flag erstellt werden
- `/etc/pve/lxc/100.conf` ergänzen:
  ```
  features: nesting=1
  ```

---

### Unraid

**1. Community Applications Plugin installieren** (falls nicht vorhanden)
- Apps → Community Applications

**2. Docker Compose Manager installieren**
- Apps → "Docker Compose Manager" suchen

**3. Repository klonen**
- Terminal öffnen
  ```bash
  cd /mnt/user/appdata
  git clone https://github.com/Xerolux/idm-metrics-collector.git
  ```

**4. Docker Compose Manager starten**
- Apps → Docker Compose Manager → Add Stack
- Name: IDM-Metrics
- Path: `/mnt/user/appdata/idm-metrics-collector`
- Compose Up ausführen

**5. Im Browser öffnen**
```
http://unraid-ip:5008
```

---

### Windows mit WSL2

**1. WSL2 Ubuntu installieren** (falls noch nicht vorhanden)
```powershell
wsl --install -d Ubuntu-22.04
```

**2. Ubuntu starten** (aus Startmenü)

**3. Docker installieren**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**4. Terminal neu starten, dann IDM Metrics installieren**
```bash
cd ~
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker compose up -d
```

**5. Im Browser öffnen** (auch von Windows aus!)
```
http://localhost:5008
```

---

## ⚙️ Ersteinrichtung

### Setup-Wizard (Web-Interface)

**1. Browser öffnen**
```
http://<server-ip>:5008
```

**2. Willkommensbildschirm**
- Sprache: Deutsch (Standard)
- Weiter klicken

**3. Wärmepumpen-Verbindung**
- **Host/IP**: IP-Adresse Ihrer IDM Wärmepumpe (z.B. `192.168.1.50`)
- **Modbus Port**: `502` (Standard)
- **Timeout**: `5` Sekunden (Standard)
- **Verbindung testen** klicken

**Erfolgreich**: ✅ "Verbindung erfolgreich, 50+ Register gelesen"
**Fehler**: ❌ Siehe [Problembehandlung](#-problembehandlung)

**4. Features aktivieren**
- ☑️ **Heizkreis A** (immer aktiv)
- ☑️ **Heizkreis B** (falls vorhanden)
- ☑️ **Heizkreis C** (falls vorhanden)
- ☑️ **Zonen-Sensoren** (falls verbaut)
- ☑️ **Solar-Integration** (falls PV-Anlage vorhanden)

**5. VictoriaMetrics**
- **URL**: `http://victoriametrics:8428/write` (Standard, nicht ändern!)
- **Retention**: `12` Monate (oder länger)

**6. Admin-Sicherheit**
- **Benutzername**: `admin` (Standard)
- **Passwort**: Sicheres Passwort vergeben (min. 6 Zeichen, empfohlen 12+)
- **Passwort wiederholen**

**7. Einrichtung abschließen**
- Zusammenfassung prüfen
- **Einrichtung abschließen** klicken

**8. Dashboard erscheint!** 🎉
- Nach 30-60 Sekunden sollten erste Daten erscheinen

---

## 🔧 Erweiterte Konfiguration

### MQTT / Home Assistant Integration

**In IDM Metrics Collector:**
1. Einstellungen → MQTT
2. **Aktiviert**: ✅
3. **Broker**: IP Ihres MQTT-Brokers (z.B. `192.168.1.10`)
4. **Port**: `1883` (Standard) oder `8883` (TLS)
5. **Username**: MQTT-Benutzername
6. **Password**: MQTT-Passwort
7. **TLS**: ✅ (falls konfiguriert)
8. **Home Assistant Discovery**: ✅ Aktivieren
9. **Topic-Prefix**: `idm/heatpump` (Standard)
10. **Speichern & Testen**

**In Home Assistant:**
- Nichts zu tun! Sensoren erscheinen automatisch unter:
  - Einstellungen → Geräte & Dienste → MQTT
  - Device: "IDM Heat Pump"

Details: [docs/MQTT_SETUP.md](docs/MQTT_SETUP.md)

---

### Benachrichtigungen einrichten

**Telegram:**
1. @BotFather in Telegram öffnen
2. `/newbot` → Bot-Namen eingeben → API-Token erhalten
3. Bot-Nachricht senden: `/start`
4. Chat-ID herausfinden: https://api.telegram.org/bot<TOKEN>/getUpdates
5. IDM Metrics: Einstellungen → Benachrichtigungen → Telegram
6. Token & Chat-ID eingeben → Speichern & Testen

**Signal:**
Siehe: [docs/MANUAL.md - Signal Setup](docs/MANUAL.md#signal-notifications)

**ntfy.sh (einfachste Option):**
1. https://ntfy.sh öffnen
2. Topic wählen (z.B. `heatpump-alerts-xyz123`)
3. IDM Metrics: Einstellungen → Benachrichtigungen → ntfy
4. Topic eingeben → Speichern
5. In ntfy-App subscriben: https://ntfy.sh/heatpump-alerts-xyz123

---

### Reverse Proxy (HTTPS)

**Nginx-Beispiel:**

```nginx
# /etc/nginx/sites-available/idm-metrics

server {
    listen 443 ssl http2;
    server_name heatpump.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    location / {
        proxy_pass http://localhost:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket Support (wichtig!)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    server_name heatpump.example.com;
    return 301 https://$server_name$request_uri;
}
```

Aktivieren:
```bash
sudo ln -s /etc/nginx/sites-available/idm-metrics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Traefik-Beispiel:**

```yaml
# docker-compose.yml ergänzen
services:
  idm-logger:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.idm.rule=Host(`heatpump.example.com`)"
      - "traefik.http.routers.idm.entrypoints=websecure"
      - "traefik.http.routers.idm.tls.certresolver=letsencrypt"
      - "traefik.http.services.idm.loadbalancer.server.port=5008"
```

---

## 🔄 Updates & Wartung

### Automatische Updates (Watchtower)

Watchtower ist bereits im Docker Compose integriert und aktualisiert alle Container automatisch:

- **Prüfung**: Täglich um 03:00 Uhr
- **Aktion**: Automatischer Pull & Restart bei neuer Version
- **Benachrichtigung**: Optional per Email/Discord/Telegram konfigurierbar

**Keine Aktion erforderlich!**

### Manuelle Updates

```bash
cd /pfad/zu/idm-metrics-collector

# Neue Images pullen
docker compose pull

# Container mit neuen Images neu starten
docker compose up -d

# Alte Images aufräumen (optional)
docker image prune -f
```

### Logs rotieren

```bash
# Alte Logs löschen (älter als 7 Tage)
docker compose exec idm-logger python -m idm_logger.log_rotate --days 7
```

### Backup erstellen

**Manuelles Backup:**
```bash
# Komplettes Backup (Config + Daten)
docker compose exec idm-logger python -m idm_logger.backup

# Backup wird gespeichert in: ./backups/backup-YYYY-MM-DD-HH-MM-SS.tar.gz
```

**Automatisches Backup:**
- Einstellungen → Backup → WebDAV aktivieren
- Täglich um 02:00 Uhr automatisches Backup

Details: [docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md)

---

## 🗑️ Deinstallation

### Vollständige Entfernung

```bash
cd /pfad/zu/idm-metrics-collector

# Container stoppen und entfernen
docker compose down

# Volumes löschen (ACHTUNG: Alle Daten gehen verloren!)
docker compose down -v

# Installation löschen
cd ..
rm -rf idm-metrics-collector
```

### Nur Container stoppen (Daten behalten)

```bash
# Container stoppen
docker compose stop

# Später wieder starten
docker compose start
```

---

## 🔧 Problembehandlung

### Container starten nicht

**Problem**: `docker compose up -d` schlägt fehl

**Lösung 1**: Logs prüfen
```bash
docker compose logs
```

**Lösung 2**: Port-Konflikte?
```bash
# Port 5008 bereits belegt?
sudo lsof -i :5008

# Port 8428 bereits belegt?
sudo lsof -i :8428

# Lösung: Ports in docker-compose.yml ändern
```

**Lösung 3**: Docker neu starten
```bash
sudo systemctl restart docker
```

---

### Keine Verbindung zur Wärmepumpe

**Problem**: "Connection refused" oder "Timeout"

**Checkliste:**

1. **Ist Modbus TCP aktiviert?**
   - An der Wärmepumpe: Fachmann-Menü → Kommunikation → Modbus TCP → Aktiviert

2. **Ist die IP korrekt?**
   - Ping-Test: `ping 192.168.1.50`
   - Modbus-Port-Test: `telnet 192.168.1.50 502`

3. **Firewall-Probleme?**
   ```bash
   # An der Wärmepumpe Port 502 freigeben (falls Firewall aktiv)
   ```

4. **Netzwerk-Trennung?**
   - Server und Wärmepumpe müssen im gleichen Subnetz sein
   - Keine VLANs dazwischen

---

### Dashboard zeigt keine Daten

**Problem**: Dashboard ist leer oder zeigt "No Data"

**Checkliste:**

1. **VictoriaMetrics läuft?**
   ```bash
   docker compose ps
   # victoriametrics sollte "Up" sein
   ```

2. **Modbus-Daten werden empfangen?**
   ```bash
   docker compose logs idm-logger | grep "Successfully read"
   # Sollte alle 60s eine Meldung zeigen
   ```

3. **VictoriaMetrics erreichbar?**
   ```bash
   curl http://localhost:8428/api/v1/query?query=idm_heatpump_temp_outside
   # Sollte JSON mit Daten zurückgeben
   ```

4. **Zeitbereich korrekt?**
   - Dashboard: Zeitbereich auf "Letzte 24h" oder "Letzte 7 Tage" setzen

---

### KI meldet zu viele False Positives

**Lösung**: Sensitivität anpassen

```yaml
# docker-compose.yml
ml_service:
  environment:
    ANOMALY_THRESHOLD: "0.8"  # Höher = weniger sensitiv (Standard: 0.7)
    ANOMALY_DEBOUNCE_COUNT: "5"  # Mehr aufeinanderfolgende Anomalien nötig (Standard: 3)
```

```bash
docker compose restart ml_service
```

---

### Hoher RAM-Verbrauch

**Problem**: Container verwenden zu viel RAM (z.B. auf Raspberry Pi)

**Lösung**: Ressourcen-Limits setzen

```yaml
# docker-compose.yml
services:
  ml_service:
    deploy:
      resources:
        limits:
          memory: 384M  # Statt 768M

  victoriametrics:
    command:
      - '--memory.allowedPercent=50'  # Max. 50% des verfügbaren RAMs
```

---

### Port 5008 bereits belegt

**Lösung**: Anderen Port verwenden

```yaml
# docker-compose.yml
services:
  idm-logger:
    ports:
      - "8080:5008"  # Statt 5008:5008
```

Dann im Browser: `http://<ip>:8080`

---

## 📞 Support

### Weitere Hilfe benötigt?

1. **📖 Dokumentation**
   - [Benutzerhandbuch](docs/MANUAL.md)
   - [FAQ](docs/FAQ.md)
   - [Feature-Übersicht](FEATURES.md)

2. **💬 Community**
   - [Discord Server](https://discord.gg/Qa5fW2R)
   - [Home Assistant Forum](https://community.home-assistant.io/)

3. **🐛 Issue melden**
   - [GitHub Issues](https://github.com/Xerolux/idm-metrics-collector/issues)

---

**Installation erfolgreich?** 🎉
→ Weiter zur [Ersteinrichtung](docs/MANUAL.md) oder [FAQ](docs/FAQ.md)
