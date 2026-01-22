# SPDX-License-Identifier: MIT
"""Dashboard configuration management."""

import uuid
import logging
from typing import Dict, List, Any, Optional
from .config import config

logger = logging.getLogger(__name__)


def get_default_dashboards() -> List[Dict[str, Any]]:
    """Get default dashboard configuration matching Grafana standard dashboard."""
    return [
        {
            "id": "default",
            "name": "Home Dashboard",
            "charts": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Wärmepumpe Temperaturen",
                    "queries": [
                        {
                            "label": "Aussen",
                            "query": "idm_heatpump_temp_outside",
                            "color": "#3b82f6",  # Blue
                        },
                        {
                            "label": "Vorlauf",
                            "query": "idm_heatpump_temp_heat_pump_flow",
                            "color": "#ef4444",  # Red
                        },
                        {
                            "label": "Rücklauf",
                            "query": "idm_heatpump_temp_heat_pump_return",
                            "color": "#f59e0b",  # Orange
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Warmwasser Temperaturen",
                    "queries": [
                        {
                            "label": "WW oben",
                            "query": "idm_heatpump_temp_water_heater_top",
                            "color": "#ef4444",
                        },
                        {
                            "label": "WW unten",
                            "query": "idm_heatpump_temp_water_heater_bottom",
                            "color": "#f59e0b",
                        },
                        {
                            "label": "Sollwert",
                            "query": "idm_heatpump_temp_water_target",
                            "color": "#22c55e",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Leistung",
                    "queries": [
                        {
                            "label": "Leistungsaufnahme",
                            "query": "idm_heatpump_power_current_draw",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Wärmeleistung",
                            "query": "idm_heatpump_power_current",
                            "color": "#3b82f6",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Energie (kumuliert)",
                    "queries": [
                        {
                            "label": "Gesamt",
                            "query": "idm_heatpump_energy_heat_total",
                            "color": "#3b82f6",
                        },
                        {
                            "label": "Heizung",
                            "query": "idm_heatpump_energy_heat_heating",
                            "color": "#22c55e",
                        },
                        {
                            "label": "Warmwasser",
                            "query": "idm_heatpump_energy_heat_total_water",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Heizkreis A - Temperaturen",
                    "queries": [
                        {
                            "label": "Vorlauf Ist",
                            "query": "idm_heatpump_temp_flow_current_circuit_a",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Vorlauf Soll",
                            "query": "idm_heatpump_temp_flow_target_circuit_a",
                            "color": "#22c55e",
                        },
                        {
                            "label": "Raum",
                            "query": "idm_heatpump_temp_room_circuit_a",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Speicher & Quelltemperaturen",
                    "queries": [
                        {
                            "label": "Pufferspeicher",
                            "query": "idm_heatpump_temp_heat_storage",
                            "color": "#a855f7",
                        },
                        {
                            "label": "Kältespeicher",
                            "query": "idm_heatpump_temp_cold_storage",
                            "color": "#3b82f6",
                        },
                        {
                            "label": "Quelle Eingang",
                            "query": "idm_heatpump_temp_heat_source_input",
                            "color": "#06b6d4",
                        },
                        {
                            "label": "Quelle Ausgang",
                            "query": "idm_heatpump_temp_heat_source_output",
                            "color": "#14b8a6",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "COP Verlauf",
                    "queries": [
                        {
                            "label": "COP",
                            "query": "idm_heatpump_power_current / idm_heatpump_power_current_draw",
                            "color": "#22c55e",
                        }
                    ],
                    "hours": 24,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "AI Anomalie-Erkennung",
                    "queries": [
                        {
                            "label": "Anomalie Score",
                            "query": "idm_anomaly_score",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Anomalie Flag",
                            "query": "idm_anomaly_flag",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
            ],
        }
    ]


class DashboardManager:
    """Manages dashboard configurations."""

    def __init__(self):
        """Initialize dashboard manager."""
        self._ensure_dashboards_key()
        self._repair_broken_dashboards()

    def _repair_broken_dashboards(self):
        """Repair broken dashboards from bad seed data."""
        dashboards = self.get_all_dashboards()
        repaired = False

        for i, dashboard in enumerate(dashboards):
            if dashboard.get("id") == "default":
                # Check for broken chart titles from the bad example
                broken_titles = [
                    "Underfloor Heating",
                    "Tank Heating Sensing",
                    "Radiators Flow & Return: 1st & 2nd Floor",
                    "3rd Floor: Flow & Return Temperatures",
                    "3rd Floor Deep Dive",
                    "Consumption change",
                ]

                chart_titles = [c.get("title") for c in dashboard.get("charts", [])]

                # If any of the specific broken titles are present
                if any(title in chart_titles for title in broken_titles):
                    logger.info("Detected broken dashboard configuration. Repairing...")
                    # Replace with fresh default
                    default_dashboards = get_default_dashboards()
                    # We assume get_default_dashboards returns a list with one dashboard
                    dashboards[i] = default_dashboards[0]
                    repaired = True
                    break

        if repaired:
            config.data["dashboards"] = dashboards
            config.save()
            logger.info("Dashboard repair completed.")

    def _ensure_dashboards_key(self):
        """Ensure dashboards key exists in config."""
        if "dashboards" not in config.data:
            config.data["dashboards"] = get_default_dashboards()
            config.save()

    def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """Get all dashboards."""
        return config.data.get("dashboards", [])

    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific dashboard by ID."""
        dashboards = self.get_all_dashboards()
        for dashboard in dashboards:
            if dashboard["id"] == dashboard_id:
                return dashboard
        return None

    def create_dashboard(self, name: str) -> Dict[str, Any]:
        """Create a new dashboard."""
        dashboards = self.get_all_dashboards()
        new_dashboard = {
            "id": str(uuid.uuid4()),
            "name": name,
            "charts": [],
        }
        dashboards.append(new_dashboard)
        config.data["dashboards"] = dashboards
        config.save()
        logger.info(f"Created dashboard: {name}")
        return new_dashboard

    def update_dashboard(
        self, dashboard_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a dashboard."""
        dashboards = self.get_all_dashboards()
        for i, dashboard in enumerate(dashboards):
            if dashboard["id"] == dashboard_id:
                dashboards[i].update(updates)
                config.data["dashboards"] = dashboards
                config.save()
                logger.info(f"Updated dashboard: {dashboard_id}")
                return dashboards[i]
        return None

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        dashboards = self.get_all_dashboards()
        if len(dashboards) <= 1:
            logger.warning("Cannot delete the last dashboard")
            return False

        dashboards = [d for d in dashboards if d["id"] != dashboard_id]
        config.data["dashboards"] = dashboards
        config.save()
        logger.info(f"Deleted dashboard: {dashboard_id}")
        return True

    def add_chart(
        self,
        dashboard_id: str,
        title: str,
        queries: List[Dict[str, str]],
        hours: int = 12,
    ) -> Optional[Dict[str, Any]]:
        """Add a chart to a dashboard."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        new_chart = {
            "id": str(uuid.uuid4()),
            "title": title,
            "queries": queries,
            "hours": hours,
        }

        dashboard["charts"].append(new_chart)
        self.update_dashboard(dashboard_id, {"charts": dashboard["charts"]})
        return new_chart

    def update_chart(
        self, dashboard_id: str, chart_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a chart in a dashboard."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        for i, chart in enumerate(dashboard["charts"]):
            if chart["id"] == chart_id:
                dashboard["charts"][i].update(updates)
                self.update_dashboard(dashboard_id, {"charts": dashboard["charts"]})
                return dashboard["charts"][i]
        return None

    def delete_chart(self, dashboard_id: str, chart_id: str) -> bool:
        """Delete a chart from a dashboard."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False

        charts = [c for c in dashboard["charts"] if c["id"] != chart_id]
        if len(charts) == len(dashboard["charts"]):
            return False

        self.update_dashboard(dashboard_id, {"charts": charts})
        return True


# Global instance
dashboard_manager = DashboardManager()
