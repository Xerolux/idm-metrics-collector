# Community AI Concept: "Sharing is Caring"

## Das Prinzip

Das Ziel ist es, eine starke Gemeinschaft aufzubauen, in der jeder Beitrag zählt. Das Prinzip ist einfach:
**Wer Daten teilt, profitiert von den besseren KI-Modellen der Gemeinschaft.**

Nutzer, die keine Daten teilen, können weiterhin ihre lokale KI nutzen und trainieren, erhalten aber keinen Zugriff auf die vortrainierten, robusten "Community-Modelle", die auf den Daten von hunderten Wärmepumpen basieren.

## Workflow

### 1. Datenbeitrag (Contribution)
Der IDM Logger sendet regelmäßig (z.B. alle 5 Minuten) anonymisierte Telemetrie-Daten an den Server.
*   **Identifikation**: Über die zufällige `installation_id`.
*   **Validierung**: Der Server speichert den Zeitstempel des letzten gültigen Uploads für diese ID.

### 2. Berechtigungsprüfung (Eligibility Check)
Wenn der Nutzer ein Update des KI-Modells anfordert (oder der Logger dies automatisch tut):
1.  Der Client sendet eine Anfrage an `GET /api/v1/model/check?installation_id=...`.
2.  Der Server prüft in der Datenbank: **Hat diese ID in den letzten 30 Tagen Daten gesendet?**
3.  **Ja**: Der Server antwortet mit `{ "eligible": true }` und ggf. einem signierten Download-Link oder Token.
4.  **Nein**: Der Server antwortet mit `{ "eligible": false, "reason": "No data contribution in last 30 days" }`.

### 3. Modell-Download
Berechtigte Nutzer können das neueste `model.pkl` herunterladen. Dieses Modell ist robuster, da es Anomalien aus vielen verschiedenen Installationen kennt und Fehlalarme minimiert.

## Datenschutz & DSGVO (GDPR) Strategie

Da der Server in Deutschland steht und Datenschutz oberste Priorität hat:

1.  **Datenminimierung**:
    *   Wir speichern keine IP-Adressen dauerhaft. Im Log werden sie maskiert (z.B. `192.168.xxx.xxx`).
    *   Die `installation_id` ist pseudonomisiert und nicht ohne weiteres einer Person zuzuordnen (außer der Nutzer meldet sich im Support mit dieser ID).

2.  **Zweckbindung**:
    *   Die Daten werden ausschließlich zum Trainieren der Fehlererkennungs-KI verwendet.

3.  **Speicherdauer**:
    *   Rohdaten in VictoriaMetrics haben eine Retention Policy (z.B. 12 Monate). Danach werden sie automatisch gelöscht.
    *   Metadaten zur Berechtigung (wann zuletzt gesendet) werden ebenfalls nach Inaktivität bereinigt.

4.  **Recht auf Löschung**:
    *   Da wir die Daten über die `installation_id` finden können, kann ein Nutzer theoretisch die Löschung seiner Daten beantragen, indem er seine ID mitteilt. Wir können dann ein `DELETE` in der Datenbank ausführen.

5.  **Sicherheit**:
    *   Serverstandort: Deutschland.
    *   Kein direkter Datenbankzugriff von außen (nur Localhost-Binding).
    *   API nur über HTTPS mit Authentifizierung (Token).
    *   Strikte Firewall-Regeln (UFW).

### Modellschutz (DRM / Encryption)

Damit die wertvollen "Community Models" nicht einfach kopiert und weiterverkauft werden können, sind sie geschützt:

1.  **Verschlüsselung**: Das Modell wird auf dem Server verschlüsselt (`.enc`).
2.  **Decryption**: Der `ml_service` im Client enthält den Schlüssel, um das Modell im Arbeitsspeicher zu nutzen.
3.  **Backup-Ausschluss**: Die verschlüsselten Modelldateien werden explizit vom Benutzer-Backup ausgeschlossen, damit sie nicht ungewollt verbreitet werden.

## Rechtliches & Eigentum

Der Nutzer stimmt im Setup explizit zu:
*   Die gesendeten, anonymisierten Daten gehen in das Eigentum des Tool-Betreibers über.
*   Der Betreiber darf diese Daten kommerziell nutzen (z.B. Verkauf von Enterprise-Lösungen, Training proprietärer Modelle).
*   Dies sichert die Finanzierung der Infrastruktur und Weiterentwicklung.

## Ausblick: Monatliche Updates

Der Server kann so konfiguriert werden, dass am 1. jeden Monats ein Trainings-Skript läuft:
1.  Exportiere Daten des letzten Monats.
2.  Trainiere das `river` Modell inkrementell weiter.
3.  Veröffentliche das neue Modell als `v2023.10`.
4.  Clients laden es automatisch herunter, wenn sie berechtigt sind.
