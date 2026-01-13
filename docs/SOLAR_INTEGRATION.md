# Solar / PV Integration

Du kannst dein Photovoltaik (PV) System mit der iDM Wärmepumpe integrieren, um den Energieverbrauch zu optimieren (PV-Überschussladen).

## Voraussetzungen

*   Ein funktionierendes PV-System (Wechselrichter), das Daten über Modbus TCP, MQTT oder eine andere API bereitstellt.
*   `idm-logger` läuft und ist mit deiner iDM Wärmepumpe verbunden.
*   MQTT Broker (optional, aber für eine einfache Integration empfohlen).

## Register

Die iDM Wärmepumpe (Navigator 2.0) stellt spezifische Register für die PV-Integration bereit:

| Register (Dez) | Name | Sensor Name | Einheit | Typ | Zugriff | Beschreibung |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **74** | Aktueller PV-Überschuss | `power_solar_surplus` | kW | Float32 | RW | Schreibe hier den aktuellen PV-Überschuss (Einspeisung). |
| 78 | Aktuelle PV Produktion | `power_solar_production` | kW | Float32 | RW | Schreibe die aktuelle PV-Produktion. |
| 82 | Hausverbrauch | `power_use_house` | kW | Float32 | RW | Schreibe den aktuellen Hausverbrauch. |

**Wichtig:** Das wichtigste Register zur Optimierung des Wärmepumpenbetriebs ist **74 (PV-Überschuss)**.

## Verwendung

### Via MQTT (Empfohlen)

1.  **Aktiviere MQTT** in deiner `config.yaml` oder über die Weboberfläche.
2.  **Veröffentliche (Publish)** den aktuellen PV-Überschusswert (in kW) auf folgendes Topic:

    ```
    idm/heatpump/power_solar_surplus/set
    ```

    *   **Payload**: Der Wert als Zahl (z.B. `2.5` für 2500 Watt).
    *   **Einheit**: Kilowatt (kW). Wenn dein Wechselrichter Watt liefert, teile durch 1000.
    *   **Frequenz**: Du kannst diesen Wert alle paar Sekunden oder Minuten aktualisieren (z.B. alle 10-60 Sekunden).

    **Beispiel:**
    ```bash
    mosquitto_pub -h dein_broker -t "idm/heatpump/power_solar_surplus/set" -m "3.2"
    ```

### Via Python Skript (Extern)

Wenn du eine direkte Modbus-Verbindung oder ein eigenes Skript bevorzugst, kannst du direkt auf Register 74 schreiben.

*   **Adresse**: 74
*   **Typ**: Float32 (2 Register)
*   **Byte-Reihenfolge**: Big Endian
*   **Wort-Reihenfolge**: Little Endian

*Hinweis: Der `idm-logger` verwaltet die Verbindung zur Wärmepumpe. Wenn du ein externes Skript verwendest, um via Modbus zu schreiben, stelle sicher, dass es nicht mit dem Verbindungslimit des Loggers in Konflikt gerät (Modbus TCP erlaubt normalerweise mehrere Verbindungen, aber begrenzt).*

### Logik

*   **Überschuss > 0**: Die Wärmepumpe kann ihre Zieltemperatur erhöhen, um Energie zu speichern (wenn in den Navigator-Einstellungen konfiguriert).
*   **Überschuss = 0**: Normalbetrieb.

## Konfiguration im iDM Navigator

Stelle sicher, dass deine iDM Wärmepumpe so konfiguriert ist, dass sie das PV-Signal verwendet:
*   Gehe zu den **Photovoltaik** Einstellungen im Navigator-Panel.
*   Aktiviere die **PV-Signal** Quelle (oft "GLT" oder "Modbus TCP" genannt).

## Fehlerbehebung

*   **Wert wird nicht angezeigt**: Prüfe die `idm-logger` Protokolle. Der Sensor `power_solar_surplus` ist in manchen Konfigurationen als "write-only" markiert (um Fehler beim Lesen zu vermeiden), daher erscheint er möglicherweise nicht in der Standard-Leseschleife oder InfluxDB, es sei denn, du schreibst darauf.
*   **Skalierung**: Stelle sicher, dass du **kW** (Kilowatt) sendest, nicht Watt. Das Senden von `2500` anstatt `2.5` wird als 2,5 MegaWatt interpretiert!
