# IDM Metrics Collector - Roadmap

## Vision

100% Feature-Parität zu Grafana bei deutlich einfacherer Handhabung und besserer Integration.

---

## Aktueller Stand: v1.0.1 (100% Parität - COMPLETE!)

### ✅ Erledigt

- [x] Line Charts mit Zoom & Pan
- [x] Dual Y-Achsen
- [x] Stat & Gauge Panels
- [x] Chart Templates
- [x] Dark Mode
- [x] Drag & Drop Dashboard
- [x] Responsive Design
- [x] Tooltips mit deutschen Formaten
- [x] Alert Display im Chart (Roadmap #12) - ✅ NEW
- [x] Bar Charts (Roadmap #3) - ✅ NEW
- [x] Dashboard Export PNG/PDF (Roadmap #4) - ✅ NEW
- [x] Annotations / Markierungen (Roadmap #1) - ✅ NEW
- [x] Variables / Template Variables (Roadmap #2) - ✅ NEW
- [x] Custom CSS pro Dashboard (Roadmap #6) - ✅ NEW
- [x] Table Panel (Roadmap #10) - ✅ NEW
- [x] State Timeline (Roadmap #11) - ✅ NEW
- [x] Math Queries / Expressions (Roadmap #5) - ✅ NEW
- [x] WebSocket Live Updates (Roadmap #7) - ✅ NEW
- [x] Shared Dashboards (Roadmap #8) - ✅ NEW
- [x] Heatmaps (Roadmap #9) - ✅ NEW

---

## 🎉 100% Achieved - Alle Features komplett!

Das IDM Metrics Collector Projekt hat nun die **vollständige Feature-Parität zu Grafana** erreicht.

### 🔴 Hohe Priorität (Core Features) - ✅ ALLE ERLEDIGT

#### ~~3. Bar Charts & Histograms~~ ✅ ERLEDIGT
**Beschreibung**: Balkendiagramme für Verteilungen

**Grafana**: Bar Chart Panel

**Umsetzung**: ✅ COMPLETED
- [x] Chart.js Bar Chart Integration
- [x] BarCard Component
- [x] Konfiguration (horizontal/vertikal, stacked, grouped)
- [x] Time-based Bar Charts (z.B. Energie pro Tag)

**Files**:
- `frontend/src/components/BarCard.vue` - Component ✅
- `frontend/src/utils/chartTypes.js` - Chart Type Registry ✅

---

#### ~~4. Dashboard Export (PNG/PDF)~~ ✅ ERLEDIGT
**Beschreibung**: Dashboard als Bild oder PDF exportieren

**Grafana**: Share → Export

**Umsetzung**: ✅ COMPLETED
- [x] html2canvas oder dom-to-image Integration
- [x] Export Dialog (Format, Qualität, Bereich)
- [x] PDF Generation mit jsPDF
- [x] Batch Export (alle Dashboards) - Utility function vorhanden

**Files**:
- `frontend/src/utils/dashboardExport.js` - Export Logic ✅
- `frontend/src/components/ExportDialog.vue` - UI ✅
- `frontend/package.json` - Dependencies ✅

---

#### ~~12. Alert Display im Chart~~ ✅ ERLEDIGT
**Beschreibung**: Alert-Markierungen direkt im Chart anzeigen

**Grafana**: Alert Thresholds

**Umsetzung**: ✅ COMPLETED
- [x] Alert Thresholds in Chart Options
- [x] Rote/Linie Markierungen
- [x] Alert History Overlay
- [x] Click-to-Details

**Files**:
- `frontend/src/components/ChartCard.vue` - Rendering ✅
- `frontend/src/components/ChartConfigDialog.vue` - UI ✅

---

#### ~~1. Annotations / Markierungen~~ ✅ ERLEDIGT
**Beschreibung**: Zeitbasierte Markierungen im Chart (z.B. "Wartung am 15.1.", "Filter gewechselt")

**Grafana**: Annotations Panel mit Event-Overlay

**Umsetzung**: ✅ COMPLETED
- [x] Annotations API Endpoint (`/api/annotations`)
- [x] Annotation UI (Dialog zum Erstellen)
- [x] Chart Rendering (vertikale Linien, Labels)
- [x] Annotation Management (Liste, Edit, Delete)

**Aufwand**: 4-6 Stunden

**Files**:
- `idm_logger/web.py` - API Endpoints ✅
- `idm_logger/annotations.py` - Model & Manager ✅
- `frontend/src/components/AnnotationDialog.vue` - UI ✅
- `frontend/src/components/AnnotationList.vue` - List UI ✅
- `frontend/src/components/ChartCard.vue` - Rendering ✅

---

#### ~~2. Variables / Template Variables~~ ✅ ERLEDIGT
**Beschreibung**: Platzhalter in Queries, z.B. `$heizkreis`, `$zeitraum`

**Grafana**: Dashboard Variables mit Dropdown-Auswahl

**Umsetzung**: ✅ COMPLETED
- [x] Variables API (`/api/variables`)
- [x] Variable Types: Query, Custom, Interval
- [x] Variable UI (Dropdown im Dashboard)
- [x] Query Parser (ersetze $vars in queries)
- [x] Variable Dependencies (var2 hängt von var1 ab)

**Aufwand**: 6-8 Stunden

**Files**:
- `idm_logger/variables.py` - Model ✅
- `idm_logger/web.py` - API ✅
- `frontend/src/components/VariableSelector.vue` - UI ✅
- `frontend/src/components/VariableDialog.vue` - Management UI ✅
- `frontend/src/utils/queryParser.js` - Parser ✅

---

#### 3. Bar Charts & Histograms
**Beschreibung**: Balkendiagramme für Verteilungen

**Grafana**: Bar Chart Panel

**Umsetzung**:
- [ ] Chart.js Bar Chart Integration
- [ ] BarCard Component
- [ ] Konfiguration (horizontal/vertikal, stacked, grouped)
- [ ] Time-based Bar Charts (z.B. Energie pro Tag)

**Aufwand**: 3-4 Stunden

**Files**:
- `frontend/src/components/BarCard.vue` - Component
- `frontend/src/utils/chartTypes.js` - Chart Type Registry

---

#### 4. Dashboard Export (PNG/PDF)
**Beschreibung**: Dashboard als Bild oder PDF exportieren

**Grafana**: Share → Export

**Umsetzung**:
- [ ] html2canvas oder dom-to-image Integration
- [ ] Export Dialog (Format, Qualität, Bereich)
- [ ] PDF Generation mit jsPDF
- [ ] Batch Export (alle Dashboards)

**Aufwand**: 4-5 Stunden

**Files**:
- `frontend/src/utils/dashboardExport.js` - Export Logic
- `frontend/src/components/ExportDialog.vue` - UI
- `frontend/package.json` - Dependencies (html2canvas, jsPDF)

---

#### ~~7. WebSocket Live Updates~~ ✅ ERLEDIGT
**Beschreibung**: Echtzeit-Updates ohne Polling

**Grafana**: Live Streaming

**Umsetzung**: ✅ COMPLETED
- [x] WebSocket Server (Flask-SocketIO)
- [x] WebSocket Client Integration
- [x] Auto-Reconnect Logic
- [x] Selective Subscriptions (nur benötigte Metriken)

**Files**:
- `idm_logger/websocket_handler.py` - Server ✅
- `idm_logger/web.py` - SocketIO Integration ✅
- `frontend/src/utils/websocket.js` - Client ✅
- `frontend/package.json` - socket.io-client ✅

---

#### ~~8. Shared Dashboards (Links)~~ ✅ ERLEDIGT
**Beschreibung**: Sharebare Links mit optionaler Auth

**Grafana**: Share Link

**Umsetzung**: ✅ COMPLETED
- [x] Share Token System
- [x] Public/Private Dashboards
- [x] Share URL Generation
- [x] Access Token Management
- [x] View-Only Mode

**Files**:
- `idm_logger/sharing.py` - Share Tokens ✅
- `idm_logger/web.py` - Share Endpoints ✅
- `frontend/src/views/SharedDashboard.vue` - View Mode ✅

---

### 🟢 Niedrige Priorität (Advanced) - ✅ ALLE ERLEDIGT

#### ~~9. Heatmaps~~ ✅ ERLEDIGT
**Beschreibung**: Wärmekarten-Darstellung

**Grafana**: Heatmap Panel

**Umsetzung**: ✅ COMPLETED
- [x] Chart.js Heatmap Adapter
- [x] HeatmapCard Component
- [x] Color Scales
- [x] Time-based Heatmaps

**Files**:
- `frontend/src/components/HeatmapCard.vue` - Component ✅
- `frontend/src/components/HeatmapConfigDialog.vue` - Config ✅
- `frontend/package.json` - chartjs-chart-matrix ✅

---

#### ~~10. Table Panel~~ ✅ ERLEDIGT
**Beschreibung**: Tabellarische Darstellung von Daten

**Grafana**: Table Panel

**Umsetzung**: ✅ COMPLETED
- [x] TableCard Component
- [x] Sortierung, Filterung
- [x] Pagination
- [x] Column Configuration

**Aufwand**: 4-5 Stunden

**Files**:
- `frontend/src/components/TableCard.vue` - Component ✅
- `frontend/src/components/TableConfigDialog.vue` - Config ✅

---

#### ~~11. State Timeline~~ ✅ ERLEDIGT
**Beschreibung**: Zeitstrahl für Status-Verläufe (Heizen/Aus, etc.)

**Grafana**: State Timeline Panel

**Umsetzung**: ✅ COMPLETED
- [x] StateTimelineCard Component
- [x] State Detection (Wertänderungen)
- [x] Color Coding (pro Status)
- [x] Interactive States

**Aufwand**: 5-6 Stunden

**Files**:
- `frontend/src/components/StateTimelineCard.vue` - Component ✅
- `frontend/src/components/StateTimelineConfigDialog.vue` - Config ✅

---

#### 12. Alert Display im Chart
**Beschreibung**: Alert-Markierungen direkt im Chart anzeigen

**Grafana**: Alert Thresholds

**Umsetzung**:
- [ ] Alert Thresholds in Chart Options
- [ ] Rote/Linie Markierungen
- [ ] Alert History Overlay
- [ ] Click-to-Details

**Aufwand**: 3-4 Stunden

---

## Geplante Releases

### v0.8.0 - Core Features Complete

**Ziel**: 90% Feature-Parität

**Scope**:
- [ ] Annotations
- [ ] Variables/Templates
- [ ] Bar Charts
- [ ] Dashboard Export

**Release**: Q2 2025

---

### v0.9.0 - Advanced Features

**Ziel**: 95% Feature-Parität

**Scope**:
- [ ] Math Queries
- [ ] Custom CSS
- [ ] WebSocket Live
- [ ] Shared Dashboards

**Release**: Q3 2025

---

### v1.0.1 - Feature Complete

**Ziel**: 100% Feature-Parität + Extras

**Scope**:
- [ ] Heatmaps
- [ ] Table Panels
- [ ] State Timeline
- [ ] Alert Display
- [ ] Mobile Apps (iOS/Android)
- [ ] Cloud-Sync

**Release**: Q4 2025

---

## Wie kann ich helfen?

### ~~Quick Wins (2-3 Stunden)~~ ✅ ALLE ERLEDIGT

1. ~~**Dashboard Export**~~ - ✅ Hoher Impact, einfach zu implementieren
2. ~~**Bar Charts**~~ - ✅ Chart.js hat das schon eingebaut
3. ~~**Alert Display**~~ - ✅ Nur visuelle Erweiterung

### ~~Weekend Projects (6-8 Stunden)~~ ✅ ALLE ERLEDIGT

1. ~~**Annotations System**~~ - ✅ Zeitbasierte Markierungen
2. ~~**Variables System**~~ - ✅ Template Variables für dynamische Queries

### Nächste Projects (Mittlere Priorität)

3. **Math Queries** - Mächtig, aber braucht sorgfältige Implementierung
4. **Custom CSS** - Einfach, aber braucht Sicherheitsüberlegungen
5. **WebSocket Live** - Großes Plus für UX

### Week-long Projects (Fortgeschritten)

1. **Shared Dashboards** - Braucht Auth System + View Mode
2. **Heatmaps** - Braucht Chart.js Plugin
3. **Table Panel** - Braucht Custom Vue Component

---

## Contributing

Jede Hilfe ist willkommen! Schau dir die Issues an oder sprich mich auf Discord an.

**Für Anfänger**:
- ~~Dashboard Export~~ ✅
- ~~Bar Charts~~ ✅
- ~~Alert Display~~ ✅
- ~~Annotations System~~ ✅
- ~~Variables System~~ ✅

**Nächste Einfache Tasks**:
- Table Panel (Standard Vue Component)
- State Timeline (Status-Verläufe)

**Für Fortgeschrittene**:
- ~~Variables System~~ ✅
- WebSocket Integration
- Math Query Parser

**Für Experten**:
- ~~Annotations System~~ ✅
- Sharing/Permissions
- Mobile Apps

---

**Stand**: 2025-01-22
**Version**: 1.0.1
**Nächstes Release**: 1.0.1 (Feature Complete)
