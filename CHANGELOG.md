# Changelog

## 0.6.0 - 2026-01-09 - EEPROM-Schutz und Heizkreis A Dashboard Update

### Neue Features

#### 1. EEPROM-Schutz für kritische Register
- **Metadata-System**: Neues Modul `register_metadata.py` lädt Register-Informationen aus `idm_navigator_modbus_registers.yaml`
- **EEPROM-Warnung**: Register mit begrenzten Schreibzyklen (markiert mit `*` in der iDM-Dokumentation) werden mit Warnungen geschützt
- **Cyclic-Change Hinweis**: Register die zyklisch geändert werden müssen (markiert mit `7)`) erhalten entsprechende Hinweise
- **Bestätigungsdialog**: Vor dem Schreiben auf EEPROM-sensitive Register erscheint ein Bestätigungsdialog
- **Visuelle Kennzeichnung**: Im Control-Interface werden EEPROM-sensitive Register mit gelber Warnung und cyclic_change Register mit blauer Info-Box gekennzeichnet

#### 2. Dashboard-Optimierung
- **Webseite Dashboard**: Behält die 6 ursprünglichen Widgets bei (übersichtlich)
- **Deutsche Bezeichnungen**: Dashboard-Widgets haben deutsche Labels
- **Grafana-Integration**:
  - **Heizkreis A**: Alle Werte als Zeitreihen-Diagramme in Grafana (nicht als Widgets)
  - **COP**: Nur als Diagramm in Grafana visualisieren (keine Widget-Darstellung)
  - Begründung: Zeitreihen-Diagramme zeigen Trends besser als statische Widgets

### Technische Änderungen

#### Backend (Python)
- `idm_logger/register_metadata.py`: Neues Modul zum Laden der Register-Metadaten aus YAML
- `idm_logger/sensor_addresses.py`:
  - Erweitert um `eeprom_sensitive` und `cyclic_change_required` Felder
  - System Status (Adresse 1005) als EEPROM-sensitiv markiert
- `idm_logger/web.py`:
  - API-Endpoints liefern jetzt EEPROM und cyclic_change Informationen
  - Sowohl `/api/control` als auch `/api/schedule` wurden erweitert

#### Frontend (Vue.js)
- `frontend/src/views/Control.vue`:
  - Visuelle Warnungen für EEPROM-sensitive Register (gelb)
  - Info-Hinweise für cyclic_change Register (blau)
  - Bestätigungsdialog vor EEPROM-Schreiboperationen
- `frontend/src/views/Dashboard.vue`:
  - Behält 6 Standard-Widgets bei (wie vorher)
  - Deutsche Widget-Bezeichnungen
  - Hinweis: Heizkreis A und COP sollten in Grafana als Diagramme visualisiert werden

### FLOAT-Dekodierung (bereits korrekt)
Die FLOAT-Dekodierung folgt der iDM Navigator 2.0 Spezifikation:
- 32-bit IEEE754 über 2 Register
- Word-Order: Reg_L (low word) dann Reg_H (high word) → `wordorder="little"`
- Byte-Order innerhalb Register: High-Byte vor Low-Byte → `byteorder="big"`
- Dies ist bereits korrekt in `sensor_addresses.py:163` implementiert

### Installation / Build

**WICHTIG**: Das Frontend muss mit Node.js >= 20.19 oder >= 22.12 neu gebaut werden:

```bash
cd frontend
npm install
npm run build
```

Die gebauten Dateien werden nach `idm_logger/static/` kopiert.

### Dateien

**Neue Dateien:**
- `idm_logger/register_metadata.py` - Register-Metadaten Management
- `CHANGELOG.md` - Diese Datei

**Geänderte Dateien:**
- `idm_logger/sensor_addresses.py`
- `idm_logger/web.py`
- `frontend/src/views/Control.vue`
- `frontend/src/views/Dashboard.vue`

**Daten-Dateien (unverändert, als Referenz):**
- `idm_navigator_modbus_registers.yaml` - Vollständige Register-Definitionen
- `idm_navigator_modbus_registers.json` - JSON-Format
- `idm_navigator_modbus_registers.csv` - CSV-Format

### Hinweise für Benutzer

1. **EEPROM-Warnung ernst nehmen**: Register wie "System Status" (SYSMODE) haben begrenzte Schreibzyklen. Nicht häufig ändern!
2. **Cyclic-Change beachten**: Einige Register sollten zyklisch geändert werden (z.B. alle 10 Minuten gemäß iDM-Dokumentation)
3. **Grafana-Visualisierung**:
   - **COP-Wert**: Als Zeitreihen-Diagramm in Grafana anlegen (nicht als Widget im Web-Dashboard)
   - **Heizkreis A**: Alle Heizkreis A Werte als Diagramme in Grafana visualisieren
   - Vorteil: Zeitreihen zeigen Trends, Verläufe und historische Daten besser als statische Widgets
4. **Web-Dashboard**: Bleibt übersichtlich mit 6 Basis-Widgets. Individuelle Anpassung möglich durch "Add Widget" Button
