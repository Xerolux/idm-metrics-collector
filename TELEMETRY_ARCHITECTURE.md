# Telemetry & AI Crowd-Sourcing Architecture

## Überblick

Das Ziel dieses Konzepts ist es, anonymisierte Sensordaten von vielen Wärmepumpen zu sammeln, um die Fehlererkennungs-Modelle (Anomaly Detection) zentral zu trainieren und zu verbessern. Die verbesserten Modelle werden dann mit Software-Updates an alle Nutzer verteilt.

## Client-Side (Implementiert)

Der Client (IDM Logger) wurde erweitert um:
1.  **Konfiguration**:
    *   `heatpump_model`: Das Modell der Maschine (z.B. AERO SLM).
    *   `share_data`: Zustimmung des Nutzers (Opt-in/Opt-out).
    *   `installation_id`: Eine zufällige UUIDv4, die bei der Installation generiert wird, um Daten einer Instanz zuzuordnen, ohne persönliche Daten (IP, Standort) zu speichern.
2.  **Telemetry Manager**:
    *   Sammelt Sensordaten im Hintergrund.
    *   Puffert Daten, um Netzwerklast zu minimieren.
    *   Sendet Daten periodisch an einen konfigurierten Endpunkt (`TELEMETRY_ENDPOINT`).
3.  **Datenschutz**:
    *   Es werden **keine** IP-Adressen, Passwörter oder Standortdaten gesendet.
    *   Nur die rohen Sensorwerte + Maschinentyp + UUID.

## Server-Side (To Do)

Um die Daten zu empfangen, wird ein zentraler Server benötigt.

### 1. Ingest API

Ein einfacher REST-Endpunkt, der JSON-Payloads empfängt.

*   **Endpoint**: `POST /api/v1/submit`
*   **Payload**:
    ```json
    {
      "installation_id": "550e8400-e29b-41d4-a716-446655440000",
      "heatpump_model": "AERO SLM",
      "version": "1.0.0",
      "data": [
        { "timestamp": 1700000000, "temp_outdoor": 12.5, "power_compressor": 0, ... },
        ...
      ]
    }
    ```
*   **Security**: Rate Limiting, Basic Validation. Ggf. API-Key für Clients, falls Missbrauch erkannt wird.

### 2. Storage

*   **Time-Series Database**: InfluxDB oder TimescaleDB für die Sensordaten.
*   **Metadata DB**: PostgreSQL für die Verwaltung der Installationen (UUID -> Modell, Firmware Version).

### 3. AI Training Pipeline

*   **Data Cleaning**: Filtern von fehlerhaften Daten.
*   **Training**: Trainieren von `river` Modellen (HalfSpaceTrees) oder komplexeren Modellen (Autoencoder, LSTM) auf den gesammelten Daten, segmentiert nach Wärmepumpen-Modell.
*   **Evaluation**: Testen der Modelle gegen bekannte Fehler-Szenarien.

### 4. Model Distribution

*   Export der trainierten Parameter (z.B. als Pickle oder ONNX).
*   Integration in das Docker-Image des `ml-service` oder Download-Mechanismus im Client.

## Datenschutz & GDPR

*   **Anonymisierung**: Die `installation_id` ist nicht auf eine Person zurückführbar, solange keine Nutzerkonten existieren.
*   **Transparenz**: Der Nutzer muss explizit zustimmen (Checkbox im Setup).
*   **Widerruf**: Der Nutzer kann das Teilen jederzeit in den Einstellungen deaktivieren.

## Nächste Schritte

1.  Aufsetzen des Ingest-Servers (z.B. mit FastAPI und VictoriaMetrics).
2.  Bereitstellen der URL unter `collector.xerolux.de` (Standard im Client).
3.  Optional: Setzen der Environment-Variable `TELEMETRY_ENDPOINT` im Docker-Image, falls eine andere URL verwendet werden soll.
