/**
 * Chart Type Registry
 *
 * Zentral Registrierung für alle Chart-Typen im Dashboard
 */

export const ChartType = {
    LINE: 'line',
    BAR: 'bar',
    STAT: 'stat',
    GAUGE: 'gauge',
    HEATMAP: 'heatmap',
    TABLE: 'table',
    STATE_TIMELINE: 'state_timeline',
    TELEMETRY_STATUS: 'telemetry_status',
};

export const ChartTypeConfig = {
    [ChartType.LINE]: {
        name: 'Linien-Diagramm',
        description: 'Zeitverläufe mit einer oder mehreren Serien',
        icon: 'pi pi-chart-line',
        component: () => import('../components/ChartCard.vue'),
        supported: true,
    },
    [ChartType.BAR]: {
        name: 'Balken-Diagramm',
        description: 'Verteilungen und Vergleiche',
        icon: 'pi pi-chart-bar',
        component: () => import('../components/BarCard.vue'),
        supported: true,
    },
    [ChartType.STAT]: {
        name: 'Statistik-Wert',
        description: 'Einzelwerte mit Trend-Anzeige',
        icon: 'pi pi-hashtag',
        component: () => import('../components/StatCard.vue'),
        supported: true,
    },
    [ChartType.GAUGE]: {
        name: 'Tachometer',
        description: 'Werte im Halbkreis anzeigen',
        icon: 'pi pi-ticket',
        component: () => import('../components/GaugeCard.vue'),
        supported: true,
    },
    [ChartType.HEATMAP]: {
        name: 'Heatmap',
        description: 'Wärmekarten-Darstellung',
        icon: 'pi pi-th',
        component: () => import('../components/HeatmapCard.vue'),
        supported: true,
    },
    [ChartType.TABLE]: {
        name: 'Tabelle',
        description: 'Daten in tabellarischer Form',
        icon: 'pi pi-table',
        component: () => import('../components/TableCard.vue'),
        supported: true,
    },
    [ChartType.STATE_TIMELINE]: {
        name: 'Status-Zeitstrahl',
        description: 'Status-Verläufe über Zeit',
        icon: 'pi pi-clock',
        component: () => import('../components/StateTimelineCard.vue'),
        supported: true,
    },
    [ChartType.TELEMETRY_STATUS]: {
        name: 'Community Status',
        description: 'Zeigt den Community-Datenpool-Status und Beitragsstatus',
        icon: 'pi pi-cloud',
        component: () => import('../components/TelemetryStatusCard.vue'),
        supported: true,
    },
};

/**
 * Get all supported chart types
 */
export function getSupportedChartTypes() {
    return Object.entries(ChartTypeConfig)
        .filter(([_, config]) => config.supported)
        .map(([type, config]) => ({
            type,
            ...config,
        }));
}

/**
 * Get chart type config
 */
export function getChartTypeConfig(type) {
    return ChartTypeConfig[type] || null;
}

/**
 * Check if chart type is supported
 */
export function isChartTypeSupported(type) {
    return ChartTypeConfig[type]?.supported || false;
}

export default ChartType;
