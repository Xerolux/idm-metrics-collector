# Dashboard Features & Verbesserungen

## Übersicht

Dieses Dokument beschreibt die neuen Dashboard-Features, die implementiert wurden, um das integrierte Dashboard näher an Grafana heranzuführen.

---

## ✅ Implementierte Features (Version 0.7.0)

### 1. Dark Mode Support 🌙

**Neu in v0.7.0**: Vollständiger Dark Mode mit System-Preference-Unterstützung.

**Funktionen:**
- **Automatische Erkennung**: Folgt System-Preference (prefers-color-scheme)
- **Manuelle Umschaltung**: Button in der Navigation
- **Persistenz**: Wahl wird im LocalStorage gespeichert
- **Chart-Integration**: Alle Charts passen sich automatisch an

**Verwendung:**
```javascript
// Automatisch aktiviert
// Button in der Top-Navigation (Mond/Sonne Icon)

// API für Components:
import { useUiStore } from '@/stores/ui';

const ui = useUiStore();
ui.setDarkMode(true);  // Aktivieren
ui.toggleDarkMode();   // Umschalten
```

**Technische Details:**
- CSS Class: `.my-app-dark` auf `<html>`
- Store: Pinia UI Store
- Reactive Charts: Berechnen Farben basierend auf Dark Mode

---

### 2. Chart Templates 📋

**Neu in v0.7.0**: One-Click Dashboards für häufige Anwendungsfälle.

**Verfügbare Templates:**

| Template | Beschreibung | Charts |
|----------|-------------|--------|
| Temperaturübersicht | Alle Temperaturen auf einen Blick | 4 |
| Leistungsanalyse | Strom & Wärmeleistung | 3 |
| Effizienz-Monitor | COP & Heizkurve | 3 |
| Heizkreis A Detail | Detaillierte HK-Ansicht | 3 |
| Warmwasser-Monitor | WW-Temperaturen & -Verbrauch | 2 |
| Solar-Integration | Kollektoren & Speicher | 2 |
| Alle Metriken | Komplette Übersicht | 5 |

**Verwendung:**
1. Dashboard öffnen
2. "Aus Vorlage erstellen" Button (Copy Icon)
3. Template auswählen
4. Fertig! Das Dashboard wird automatisch erstellt

**API:**
```javascript
import { chartTemplates, getTemplateById } from '@/utils/chartTemplates';

// Alle Templates
console.log(chartTemplates);

// Bestimmtes Template
const template = getTemplateById('temperature-overview');
```

---

### 3. Chart Zoom & Pan ⚡

Das Zoom-Plugin `chartjs-plugin-zoom` ist vollständig aktiviert und konfiguriert.

**Funktionen:**
- **Mausrad-Zoom**: Scrollen um in den Chart hinein- und herauszuzoomen
- **Drag-Zoom**: Bereich mit der Maus ziehen um zu zoomen
- **Pinch-Zoom**: Touch-Gesten für Mobile Geräte
- **Pan**: Gedrückt halten + Ctrl + Maus bewegen zum Verschieben
- **Reset-Button**: Appears when zoomed, klicken um zurückzusetzen

**Verwendung:**
```javascript
// Automatisch aktiviert für alle ChartCard Components
// Keine zusätzliche Konfiguration nötig
```

**Technische Details:**
- Plugin: `chartjs-plugin-zoom` v2.2.0
- Zoom-Achse: X (zeitbasiert)
- Geschwindigkeit: 0.1 (smooth)
- Limits: Original Datenbereich

---

### 2. Verbesserte Tooltips

Die Tooltips wurden komplett überarbeitet für bessere Lesbarkeit und mehr Informationen.

**Verbesserungen:**
- **Deutsches Datumsformat**: `dd.MM.yyyy HH:mm`
- **Weißer Hintergrund**: Bessere Lesbarkeit bei verschiedenen Themes
- **Rahmen & Padding**: Professionelleres Erscheinungsbild
- **Farbige Indikatoren**: Jede Serie mit ihrer Farbe im Tooltip
- **2 Dezimalstellen**: Präzise Wertanzeige

**Beispiel:**
```
22.01.2026 14:30

━━━━━━━━━━━━━━━━━━━━━
🔵 Aussen: 5.23
🔴 Vorlauf: 42.15
🟠 Rücklauf: 38.42
```

---

### 3. Dual Y-Achsen Support

Charts können jetzt zwei verschiedene Y-Achsen verwenden - perfekt für Temperatur + Leistung in einem Chart.

**Verwendung:**

```vue
<ChartCard
    title="Temperatur & Leistung"
    :queries="[
        { label: 'Vorlauf', query: 'temp_flow', color: '#ef4444' },
        { label: 'Leistung', query: 'power_watt', color: '#3b82f6' }
    ]"
    y-axis-mode="dual"
    :hours="24"
/>
```

**Eigenschaften:**
- **Linke Y-Achse**: Erste Query (z.B. Temperatur in °C)
- **Rechte Y-Achse**: Zweite+ Queries (z.B. Leistung in Watt)
- **Keine doppelten Grids**: Vermeidet visuelles Chaos
- **Automatische Skalierung**: Beide Achsen skalieren unabhängig

**API:**
```javascript
props: {
    yAxisMode: {
        type: String,
        default: 'single', // or 'dual'
        required: false
    }
}
```

---

### 4. StatCard Component

Ein Panel für die Anzeige von Einzelwerten mit optionaler Trend-Anzeige und Soll/Ist Vergleich.

**Features:**
- Große Anzeige des aktuellen Werts
- Optionaler Trend-Indikator (Pfeil + Prozent)
- Farbschwellen basierend auf Wert
- Einheiten-Unterstützung
- Letzte Aktualisierung (relativ)
- Soll/Ist Vergleich mit Fortschrittsbalken

**Beispiel:**

```vue
<StatCard
    title="Aktuelle Vorlauftemperatur"
    query="idm_heatpump_temp_flow_current"
    unit="°C"
    :decimals="1"
    :show-trend="true"
    :show-target="true"
    target-query="idm_heatpump_temp_flow_target"
    :color-thresholds="{
        low: 30,
        high: 50,
        lowColor: 'text-blue-600',
        highColor: 'text-red-600',
        normalColor: 'text-gray-900'
    }"
/>
```

**Props:**
```javascript
{
    title: String,           // Panel Titel
    query: String,           // Metric Query
    unit: String,            // Einheit (z.B. '°C', 'kW')
    decimals: Number,        // Dezimalstellen (default: 1)
    showTrend: Boolean,      // Zeige Trend vs. Vorperiode
    showTarget: Boolean,     // Zeige Soll/Ist Vergleich
    targetQuery: String,     // Query für Sollwert
    colorThresholds: {       // Farbige Warnschwellen
        low: Number,
        high: Number,
        lowColor: String,
        highColor: String,
        normalColor: String
    }
}
```

---

### 5. GaugeCard Component

Ein halbkreisförmiges Tachometer-Panel für visuelle Darstellung von Werten.

**Features:**
- Halbkreis-Gauge mit animiertem Wertebalken
- Farbige Zonen (Grün -> Gelb -> Rot)
- Sollwert-Markierung
- Optionaler Target/Actual Vergleich
- Min/Max Konfiguration

**Beispiel:**

```vue
<GaugeCard
    title="COP Leistungszahl"
    query="idm_heatpump_cop"
    unit=""
    :min="0"
    :max="10"
    :decimals="2"
    :show-zones="true"
    :zones="[
        { value: 33, color: '#ef4444' },
        { value: 66, color: '#f59e0b' }
    ]"
/>
```

**Props:**
```javascript
{
    title: String,           // Panel Titel
    query: String,           // Metric Query
    unit: String,            // Einheit
    min: Number,             // Minimum (default: 0)
    max: Number,             // Maximum (default: 100)
    decimals: Number,        // Dezimalstellen (default: 1)
    showZones: Boolean,      // Zeige Zonen-Markierungen
    zones: Array,            // [{ value: number, color: string }]
    showTarget: Boolean,     // Zeige Soll/Ist Vergleich
    target: Number,          // Fester Sollwert
    targetQuery: String      // Query für Sollwert
}
```

**Farbschema:**
- Grün (0-33%): Gut
- Gelb (34-66%): Warnung
- Rot (67-100%): Kritisch
- Oder eigene Zonen konfigurieren

---

## 🚀 Historische TODO-Liste (Archiv)

Stand April 2026: Die folgenden Punkte stammen aus älteren Planungsständen und sind
in der aktuellen v1.x weitgehend umgesetzt. Diese Liste bleibt nur als Historie erhalten.

### Mittlere Priorität

- [ ] **Dark Mode Theme**: System preference basierender Dark Mode
- [ ] **Dashboard Export**: PNG/PDF Export des gesamten Dashboards
- [ ] **Chart Templates**: Vorkonfigurierte Templates für häufige Charts
- [ ] **Math Queries**: Unterstützung für Ausdrücke (A/B, A*100)
- [ ] **Responsive Preview**: Mobile/Tablet Vorschau-Modus

### Niedrige Priorität

- [ ] **Annotation System**: Zeitbasierte Markierungen im Chart
- [ ] **Custom CSS**: Pro Dashboard benutzerdefiniertes CSS
- [ ] **Variables**: Template-Variablen (z.B. Heizkreis-Auswahl)
- [ ] **WebSocket Live**: Echtzeit-Updates ohne Polling
- [ ] **Bar Charts**: Balkendiagramme
- [ ] **Heatmaps**: Wärmekarten-Darstellung

---

## 📊 Vergleich: Dashboard vs. Grafana

| Feature | Dashboard | Grafana | Status |
|---------|-----------|---------|--------|
| Line Charts | ✅ | ✅ | Gleichauf |
| Zoom & Pan | ✅ | ✅ | Gleichauf |
| Tooltips | ✅ | ✅ | Gleichauf |
| Dual Y-Achsen | ✅ | ✅ | Gleichauf |
| Stat Panels | ✅ | ✅ | Gleichauf |
| Gauge Charts | ✅ | ✅ | Gleichauf |
| Dark Mode | ❌ | ✅ | Fehlt |
| Annotations | ❌ | ✅ | Fehlt |
| Variables | ❌ | ✅ | Fehlt |
| Bar Charts | ❌ | ✅ | Fehlt |
| Heatmaps | ❌ | ✅ | Fehlt |
| Export | ❌ | ✅ | Fehlt |
| Alerts | ✅ (separat) | ✅ | Gleichauf |

**Gesamt**: ~70% Feature-Parität

---

## 🔧 Technische Details

### Chart.js Konfiguration

**Versionen:**
- `chart.js`: ^4.5.1
- `vue-chartjs`: ^5.3.3
- `chartjs-adapter-date-fns`: ^3.0.0
- `chartjs-plugin-zoom`: ^2.2.0

**Registrierte Plugins:**
```javascript
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
    zoomPlugin
);
```

### Performance Optimierungen

- **Debounced Saves**: 500ms Delay bei Drag & Drop
- **Lazy Loading**: Daten erst bei Bedarf geladen
- **Polling Intervall**: 60 Sekunden für Updates
- **Dynamic Step**: Berechnet based on Zeitbereich

---

## 📝 Verwendung in eigenen Dashboards

### Beispiel: Komplettes Dashboard

```vue
<template>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Stat Cards oben -->
        <StatCard
            title="Außentemperatur"
            query="idm_heatpump_temp_outside"
            unit="°C"
            :show-trend="true"
        />

        <GaugeCard
            title="COP"
            query="idm_heatpump_cop"
            :min="0"
            :max="10"
            :show-zones="true"
        />

        <!-- Dual Axis Chart -->
        <ChartCard
            title="Temperatur & Leistung"
            :queries="[
                { label: 'Vorlauf', query: 'idm_heatpump_temp_flow', color: '#ef4444' },
                { label: 'Leistung', query: 'idm_heatpump_power', color: '#3b82f6' }
            ]"
            y-axis-mode="dual"
            :hours="24"
        />

        <!-- Standard Chart -->
        <ChartCard
            title="Warmwasser"
            :queries="[
                { label: 'WW oben', query: 'idm_heatpump_temp_water_top', color: '#ef4444' },
                { label: 'WW unten', query: 'idm_heatpump_temp_water_bottom', color: '#f59e0b' }
            ]"
            :hours="24"
        />
    </div>
</template>
```

---

## 🐛 Bekannte Issues

1. **Zoom Reset**: Manchmal muss man 2x klicken um komplett zurückzusetzen
2. **Dual Axis**: Nur 2 Achsen unterstützt (links + rechts)
3. **Gauge Animation**: Kann bei schnellen Wertänderungen "haken"

---

## 🔄 Migration Guide

### Von altem Chart zu neuem mit Dual Axis

**Vorher:**
```vue
<ChartCard
    title="Nur Temperatur"
    :queries="[{ label: 'Temp', query: 'temp', color: '#ef4444' }]"
    :hours="24"
/>
```

**Nachher (Dual Axis):**
```vue
<ChartCard
    title="Temp & Leistung"
    :queries="[
        { label: 'Temp', query: 'temp', color: '#ef4444' },
        { label: 'Leistung', query: 'power', color: '#3b82f6' }
    ]"
    y-axis-mode="dual"
    :hours="24"
/>
```

---

## 📚 Nützliche Links

- [Chart.js Dokumentation](https://www.chartjs.org/docs/latest/)
- [chartjs-plugin-zoom](https://github.com/chartjs/chartjs-plugin-zoom)
- [Vue Chart.js](https://vue-chartjs.org/)

---

*Zuletzt aktualisiert: 2026-01-22*
*Version: 0.7.0*
